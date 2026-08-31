# Deployment

Everything here targets a single Ubuntu/Debian server running the stack under
Docker Compose, with nginx on the host terminating TLS.

```
              :443                    127.0.0.1:8000
  internet ──────────▶ nginx (host) ──────────────▶ web        (gunicorn)
                         │                          celery_worker
                         ├── /static/  ─┐                │
                         └── /media/   ─┘ read from      ├──▶ postgres  (named volume)
                             $DATA_DIR directly         └──▶ redis     (named volume)
```

| File | Purpose |
| --- | --- |
| [deploy.sh](deploy.sh) | Every deployment command. Start here. |
| [docker-compose.prod.yml](docker-compose.prod.yml) | The production stack. |
| [Dockerfile.prod](Dockerfile.prod) | Production image: `requirements/production.txt`, non-root, gunicorn. |
| [entrypoint.sh](entrypoint.sh) | Waits for the DB, runs `collectstatic`, execs the service command. |
| [nginx/](nginx/) | vhost templates — a pre-TLS one and the final TLS one. |
| [deploy.env.example](deploy.env.example) | Server-side deployment settings → copy to `deploy/deploy.env`. |
| [env.production.example](env.production.example) | Application settings → becomes the repo-root `.env`. |

Two config files, and they are not interchangeable:

- **`deploy/deploy.env`** configures the *deployment* — domain, data directory,
  branch, worker counts. Read only by `deploy.sh`. Not committed.
- **`.env`** (repo root) configures the *application* — secrets, database, CORS.
  Read twice: by django-environ at startup and by docker compose. Not committed.
  `deploy.sh init` generates it for you with fresh secrets.

---

## 1. First-time deployment

### Prerequisites

A fresh Ubuntu 22.04/24.04 server with a public IPv4, root or sudo access, and
ports 22, 80 and 443 open — both in `ufw` and in any cloud firewall or security
group in front of the machine. Port 80 must stay open permanently; Let's Encrypt
re-validates over it on every renewal.

### Steps

```bash
# 1. Install docker, nginx, certbot, ufw
sudo apt-get update && sudo apt-get install -y git
sudo mkdir -p /srv && sudo chown "$USER" /srv
git clone git@github.com:Ahmed-3del/wadielsafar-back.git /srv/wadielsafar/app
cd /srv/wadielsafar/app
./deploy/deploy.sh bootstrap
```

`bootstrap` adds your user to the `docker` group. **Log out and back in** before
continuing, or `docker` calls will fail on permissions.

```bash
# 2. Configure the deployment
cp deploy/deploy.env.example deploy/deploy.env
$EDITOR deploy/deploy.env        # DOMAIN and LETSENCRYPT_EMAIL are required

# 3. Deploy
./deploy/deploy.sh init
```

`init` generates `.env` with a random `DJANGO_SECRET_KEY` and Postgres password,
builds the image, starts Postgres and Redis, runs `migrate` in a one-off
container, starts `web` and `celery_worker`, health-checks gunicorn, optionally
creates a superuser, and installs a pre-TLS nginx vhost.

```bash
# 4. Fill in the values init could not guess
$EDITOR .env                     # CORS_ALLOWED_ORIGINS, EMAIL_*, SENTRY_DSN, ZOHO_*
./deploy/deploy.sh restart
```

`CORS_ALLOWED_ORIGINS` must list every frontend origin exactly — scheme, host
and port, no trailing slash. The refresh-token cookie is `SameSite=None; Secure`
(see the comment in [config/settings/base.py](../config/settings/base.py)), so
in production those origins have to be `https://`.

At this point the API answers on loopback but returns **503 from nginx** on the
public internet. That is deliberate: production settings set
`SECURE_SSL_REDIRECT = True`, so serving it over plain HTTP would just 301-loop.
Continue to the domain step.

---

## 2. Domain authentication

"Domain authentication" here means proving to Let's Encrypt that this server
controls the domain, so it will issue a TLS certificate. The mechanism is the
**HTTP-01 challenge**: the CA generates a random token, asks for it at
`http://<domain>/.well-known/acme-challenge/<token>`, and issues the certificate
only if the file it gets back matches.

### 2.1 Point DNS at the server

```bash
./deploy/deploy.sh dns
```

This prints the exact record to create and then checks the live one against this
server's public IP:

| Type | Name | Value |
| --- | --- | --- |
| A | `api.wadielsafar.com` | the server's public IPv4 |

Set TTL to 300 while you are working, and raise it later. Add an `AAAA` record
too if the server has a public IPv6 — if an `AAAA` exists, the CA will prefer it,
and a stale one is a common cause of "connection refused" during validation.

Propagation is usually a few minutes. Re-run `deploy.sh dns` until it reports
`the A record points at this server`.

**Behind Cloudflare:** set the record to *DNS only* (grey cloud) until the
certificate is issued. The orange-cloud proxy terminates TLS itself, so the
challenge request never reaches this server. Turn the proxy back on afterwards,
and set the SSL/TLS mode to **Full (strict)** so Cloudflare validates the
certificate you just installed.

### 2.2 Issue the certificate

```bash
./deploy/deploy.sh domain
```

Six steps, all idempotent:

1. **DNS** — re-runs the check above; you can override and continue.
2. **Challenge webroot** — creates `/var/www/certbot`, makes sure the pre-TLS
   vhost is installed, then drops a test file there and fetches it back over the
   public internet. If that self-test fails, the certificate request would fail
   too, and the script says so before burning a rate-limit slot.
3. **Certificate** — `certbot certonly --webroot`. Webroot rather than
   `--nginx` on purpose: no plugin rewrites the vhost, so the templates in
   [nginx/](nginx/) stay the single source of truth. An existing valid
   certificate is kept (`FORCE_RENEW=true` to reissue).
4. **TLS vhost** — renders [nginx/site.conf.template](nginx/site.conf.template):
   HTTP→HTTPS redirect, TLS 1.2/1.3, static and media served straight off disk,
   everything else proxied to gunicorn.
5. **Auto-renewal** — enables `certbot.timer`, installs a deploy hook that
   reloads nginx after each renewal, and runs `certbot renew --dry-run`.
6. **End-to-end check** — `https://<domain>/api/v1/health/`.

While testing, use the staging CA so failed attempts do not count against the
production rate limit (5 certificates per domain per week):

```bash
LETSENCRYPT_STAGING=true ./deploy/deploy.sh domain
# then, once it works end to end:
FORCE_RENEW=true ./deploy/deploy.sh domain
```

### 2.3 After issuance

`DJANGO_ALLOWED_HOSTS` in `.env` must contain the domain, or Django answers
400 to everything coming through nginx. `deploy.sh init` writes it when it
generates `.env`; if you add a domain later, edit `.env` and
`./deploy/deploy.sh restart`.

Verify:

```bash
curl -sI https://api.wadielsafar.com/api/v1/health/   # expect 200 + HSTS header
curl -sI http://api.wadielsafar.com/api/v1/health/    # expect 301 to https
sudo certbot certificates                             # expiry date, 90 days out
```

### 2.4 Renewal

Certificates last 90 days; `certbot.timer` renews anything within 30 days of
expiry, twice a day. The deploy hook at
`/etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh` reloads nginx afterwards —
without it, nginx would keep serving the expired file from memory.

Check it is armed:

```bash
systemctl list-timers certbot.timer
sudo certbot renew --dry-run
```

### 2.5 Troubleshooting validation

| Symptom | Cause |
| --- | --- |
| `Timeout during connect (likely firewall problem)` | Port 80 blocked in the cloud security group, not just `ufw`. |
| `DNS problem: NXDOMAIN` | Record not created, or not propagated yet. |
| Challenge returns 404 | Another nginx vhost is answering first — check `/etc/nginx/sites-enabled/`; `deploy.sh` removes Debian's `default`, but a hand-written one can still shadow it. |
| Challenge returns 301 to https | Something is redirecting `/.well-known/` — both templates here exempt that path. |
| `too many certificates already issued` | Production rate limit hit. Use `LETSENCRYPT_STAGING=true` and wait out the week. |
| Validation succeeds, browser shows the wrong cert | An `AAAA` record points somewhere else, or Cloudflare's proxy is terminating TLS. |

### 2.6 Wildcard certificates

HTTP-01 cannot issue wildcards. If you need `*.wadielsafar.com`, that is DNS-01
validation — a `_acme-challenge` TXT record certbot writes through your DNS
provider's API — which needs a provider plugin and is outside what `deploy.sh`
does. For one API hostname, HTTP-01 as configured is the simpler choice.

### 2.7 Email domain authentication (separate thing)

If you set the `EMAIL_*` variables so the app sends mail from your domain, that
domain needs its own authentication records or the mail lands in spam. These are
DNS records at the domain, unrelated to TLS:

| Type | Name | Value |
| --- | --- | --- |
| TXT | `wadielsafar.com` | `v=spf1 include:<your mail provider> ~all` |
| TXT | `<selector>._domainkey.wadielsafar.com` | the DKIM public key your provider issues |
| TXT | `_dmarc.wadielsafar.com` | `v=DMARC1; p=none; rua=mailto:dmarc@wadielsafar.com` |

The exact SPF include and DKIM selector come from whichever provider
`EMAIL_HOST` points at. Start DMARC at `p=none`, read the aggregate reports for
a couple of weeks, then tighten to `quarantine` or `reject`.

---

## 3. Updating a deployment

```bash
cd /srv/wadielsafar/app
./deploy/deploy.sh update
```

In order: validate `.env` → back up the database → `git fetch` and
**fast-forward** to `origin/$GIT_BRANCH` (a rewritten branch stops the run rather
than discarding server state) → rebuild → migrate in a one-off container →
`compose up -d` → health-check → refresh the nginx vhost → prune dangling images.

If the health check fails, the script **rolls the code back** to the previous
commit, rebuilds, and verifies the old revision is healthy.

> Rollback covers code only. Migrations that already applied are *not* reversed —
> Django cannot reverse every operation. If a migration is what broke the deploy,
> restore the dump `update` took at the start (`$DATA_DIR/backups`).

Useful flags:

```bash
SKIP_BACKUP=true ./deploy/deploy.sh update    # skip the pre-update dump
NO_ROLLBACK=true ./deploy/deploy.sh update    # leave a failed deploy up for debugging
ASSUME_YES=true  ./deploy/deploy.sh update    # non-interactive, for CI
```

Manual rollback:

```bash
./deploy/deploy.sh rollback              # last known-healthy commit
./deploy/deploy.sh rollback 1a2b3c4      # a specific one
```

---

## 4. Backups

```bash
./deploy/deploy.sh backup                     # gzip pg_dump → $DATA_DIR/backups
BACKUP_MEDIA=true ./deploy/deploy.sh backup   # plus a tar of uploaded media
./deploy/deploy.sh restore /srv/wadielsafar/backups/db-20260830-140000.sql.gz
```

`update` backs up automatically. Dumps older than 14 days are pruned. They live
on the same disk as the database, which makes them useful for a bad deploy and
useless for a dead server — copy them off-box:

```bash
0 4 * * * cd /srv/wadielsafar/app && BACKUP_MEDIA=true ./deploy/deploy.sh backup >> /var/log/wadi-backup.log 2>&1
```

---

## 5. Day-to-day commands

```bash
./deploy/deploy.sh status                 # docker compose ps
./deploy/deploy.sh logs web               # follow one service (TAIL=500 for more)
./deploy/deploy.sh restart                # recreate web + worker, e.g. after editing .env
./deploy/deploy.sh manage showmigrations  # any manage.py command
./deploy/deploy.sh superuser
./deploy/deploy.sh shell                  # bash in the web container
./deploy/deploy.sh psql
./deploy/deploy.sh nginx                  # re-render the vhost after editing a template
./deploy/deploy.sh help
```

---

## 6. Notes on the setup

- **Migrations run in a one-off container**, not in the entrypoint, so two
  starting replicas can never race. Set `RUN_MIGRATIONS=true` if you ever run
  the image standalone without `deploy.sh`.
- **`collectstatic` runs on every `web` start.** Production uses
  `CompressedManifestStaticFilesStorage`; without a fresh `staticfiles.json`,
  every `{% static %}` lookup — including the admin's own CSS — raises at
  request time. Only `web` does it; `celery_worker` sets
  `RUN_COLLECTSTATIC=false` so the two cannot clobber the same bind mount.
- **Postgres publishes no host port.** Reach it with `deploy.sh psql` or an SSH
  tunnel.
- **gunicorn binds to `127.0.0.1:8000`,** not `0.0.0.0` — publishing it wide
  would let anyone bypass TLS by hitting the port directly.
- **Health checks send `X-Forwarded-Proto: https`.** With `SECURE_SSL_REDIRECT`
  on, a plain loopback probe gets a 301, not a 200, and would look unhealthy.
- **`/media/` deliberately carries no `X-Frame-Options` header.** The website
  renders certificate PDFs from `/media/` in a cross-origin iframe, and the
  global `DENY` Django sends on its own responses would blank that viewer out.
  See the comment in [config/urls.py](../config/urls.py). nginx serves those
  files directly, so keep any new `add_header` out of that location block.
- **The container runs as uid 10001.** `deploy.sh` chowns the bind-mounted
  `media/` and `staticfiles/` directories to match; if you move `DATA_DIR` by
  hand, chown it too or uploads start failing.
