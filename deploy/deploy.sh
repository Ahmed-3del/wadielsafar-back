#!/usr/bin/env bash
#
# Wadi Al Safar backend — deployment script.
#
#   deploy/deploy.sh bootstrap    once per server: install docker, nginx, certbot
#   deploy/deploy.sh init         first-time deployment of this repo
#   deploy/deploy.sh domain       DNS check + Let's Encrypt certificate + TLS vhost
#   deploy/deploy.sh update       pull, rebuild, migrate, restart, verify
#
# Run `deploy/deploy.sh help` for the full command list.
#
# Every command is idempotent: running it twice is safe, and a partially
# finished run can be re-run from the top.
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.prod.yml"
ENV_FILE="${REPO_ROOT}/.env"
DEPLOY_ENV_FILE="${SCRIPT_DIR}/deploy.env"
LAST_GOOD_FILE="${SCRIPT_DIR}/.last-good-commit"

# deploy.env is the server-side config; anything already exported wins over it,
# so `DOMAIN=staging.example.com deploy/deploy.sh domain` works for one-offs.
if [ -f "$DEPLOY_ENV_FILE" ]; then
    set -a
    # shellcheck disable=SC1090
    . "$DEPLOY_ENV_FILE"
    set +a
fi

APP_NAME="${APP_NAME:-wadielsafar}"
DOMAIN="${DOMAIN:-}"
LETSENCRYPT_EMAIL="${LETSENCRYPT_EMAIL:-}"
DATA_DIR="${DATA_DIR:-/srv/wadielsafar}"
GIT_BRANCH="${GIT_BRANCH:-main}"
WEB_PORT="${WEB_PORT:-8000}"
MAX_BODY="${MAX_BODY:-50m}"
PROXY_TIMEOUT="${PROXY_TIMEOUT:-60}"
CERTBOT_WEBROOT="${CERTBOT_WEBROOT:-/var/www/certbot}"
HEALTH_PATH="${HEALTH_PATH:-/api/v1/health/}"
# Must match the uid/gid baked into deploy/Dockerfile.prod, or the container
# cannot write to the bind-mounted media/ directory.
APP_UID=10001
APP_GID=10001

# ---------------------------------------------------------------- output ----

if [ -t 1 ]; then
    C_RESET=$'\033[0m'; C_RED=$'\033[31m'; C_GREEN=$'\033[32m'
    C_YELLOW=$'\033[33m'; C_BLUE=$'\033[34m'; C_BOLD=$'\033[1m'
else
    C_RESET=""; C_RED=""; C_GREEN=""; C_YELLOW=""; C_BLUE=""; C_BOLD=""
fi

log()  { printf '%s==>%s %s\n' "$C_BLUE" "$C_RESET" "$*"; }
ok()   { printf '%s ok %s %s\n' "$C_GREEN" "$C_RESET" "$*"; }
warn() { printf '%swarn%s %s\n' "$C_YELLOW" "$C_RESET" "$*" >&2; }
die()  { printf '%sfail%s %s\n' "$C_RED" "$C_RESET" "$*" >&2; exit 1; }
step() { printf '\n%s%s%s\n' "$C_BOLD" "$*" "$C_RESET"; }

confirm() {
    local prompt="$1" reply
    if [ "${ASSUME_YES:-false}" = "true" ]; then return 0; fi
    if [ ! -t 0 ]; then
        die "$prompt -- no terminal to ask on; re-run with ASSUME_YES=true to accept."
    fi
    read -r -p "$prompt [y/N] " reply
    case "$reply" in [yY]|[yY][eE][sS]) return 0 ;; *) return 1 ;; esac
}

# --------------------------------------------------------------- helpers ----

have() { command -v "$1" >/dev/null 2>&1; }
need() { have "$1" || die "'$1' is not installed. Run: deploy/deploy.sh bootstrap"; }

if [ "$(id -u)" -eq 0 ]; then SUDO=""; else SUDO="sudo"; fi

compose() {
    docker compose \
        --project-directory "$REPO_ROOT" \
        --env-file "$ENV_FILE" \
        -f "$COMPOSE_FILE" "$@"
}

# Reads one key out of the repo-root .env without sourcing it (values there may
# contain characters the shell would re-interpret).
env_get() {
    local key="$1"
    [ -f "$ENV_FILE" ] || return 1
    sed -n "s/^${key}=//p" "$ENV_FILE" | tail -n1
}

random_secret() {
    if have openssl; then
        openssl rand -hex 32
    else
        # Hex only, so nothing generated here can break .env parsing.
        head -c 32 /dev/urandom | od -An -tx1 | tr -d ' \n'
    fi
}

require_domain() {
    [ -n "$DOMAIN" ] || die "DOMAIN is not set. Add it to ${DEPLOY_ENV_FILE} (see deploy.env.example)."
}

require_docker() {
    need docker
    docker compose version >/dev/null 2>&1 \
        || die "'docker compose' (v2) is unavailable. Run: deploy/deploy.sh bootstrap"
    docker info >/dev/null 2>&1 \
        || die "cannot reach the Docker daemon. Start it, or add your user to the 'docker' group and log in again."
}

# Probes gunicorn directly on loopback. Two headers matter: production.py sets
# SECURE_SSL_REDIRECT, so without X-Forwarded-Proto the answer is a 301 rather
# than a 200; and Django rejects any Host not in DJANGO_ALLOWED_HOSTS.
health_check() {
    local tries="${1:-30}" i
    for i in $(seq 1 "$tries"); do
        if curl -fsS -m 5 \
            -H 'Host: 127.0.0.1' \
            -H 'X-Forwarded-Proto: https' \
            "http://127.0.0.1:${WEB_PORT}${HEALTH_PATH}" >/dev/null 2>&1; then
            return 0
        fi
        sleep 2
    done
    return 1
}

# .env carries the database credentials twice — once as DATABASE_URL for Django,
# once as POSTGRES_* for the postgres image. When they drift, Django connects to
# a database the server never created, which surfaces as a confusing auth error
# at request time instead of at deploy time.
validate_env() {
    [ -f "$ENV_FILE" ] || die "missing ${ENV_FILE}. Run: deploy/deploy.sh init"

    local missing=() k
    for k in DJANGO_SECRET_KEY DJANGO_ALLOWED_HOSTS DATABASE_URL REDIS_URL \
             POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD; do
        [ -n "$(env_get "$k" || true)" ] || missing+=("$k")
    done
    if [ "${#missing[@]}" -ne 0 ]; then
        die ".env is missing required keys: ${missing[*]}"
    fi

    local url user pass db
    url="$(env_get DATABASE_URL)"
    user="$(printf '%s' "$url" | sed -n 's#^postgres[a-z]*://\([^:]*\):.*#\1#p')"
    pass="$(printf '%s' "$url" | sed -n 's#^postgres[a-z]*://[^:]*:\([^@]*\)@.*#\1#p')"
    db="$(printf '%s' "$url" | sed -n 's#.*/\([^/?]*\)$#\1#p')"

    [ "$user" = "$(env_get POSTGRES_USER)" ] \
        || die "DATABASE_URL user ('$user') does not match POSTGRES_USER in .env"
    [ "$pass" = "$(env_get POSTGRES_PASSWORD)" ] \
        || die "DATABASE_URL password does not match POSTGRES_PASSWORD in .env"
    [ "$db" = "$(env_get POSTGRES_DB)" ] \
        || die "DATABASE_URL database ('$db') does not match POSTGRES_DB in .env"

    if [ "$(env_get DJANGO_DEBUG || true)" = "True" ]; then
        die "DJANGO_DEBUG=True in a production .env — refusing to deploy."
    fi
    case ",$(env_get DJANGO_ALLOWED_HOSTS)," in
        *,127.0.0.1,*) ;;
        *) die "DJANGO_ALLOWED_HOSTS must include 127.0.0.1 (deploy.sh and the container healthcheck probe loopback)." ;;
    esac
    if [ -n "$DOMAIN" ]; then
        case ",$(env_get DJANGO_ALLOWED_HOSTS)," in
            *",${DOMAIN},"*) ;;
            *) warn "DJANGO_ALLOWED_HOSTS does not list ${DOMAIN} — requests through nginx will 400." ;;
        esac
    fi
    ok ".env validated"
}

ensure_data_dirs() {
    $SUDO mkdir -p "$DATA_DIR/media" "$DATA_DIR/staticfiles" "$DATA_DIR/backups"
    $SUDO chown -R "${APP_UID}:${APP_GID}" "$DATA_DIR/media" "$DATA_DIR/staticfiles"
    # nginx serves media/ and staticfiles/ as www-data, so they need o+rx.
    # Deliberately not applied to backups/ — database dumps stay owner-only.
    $SUDO chmod a+rX "$DATA_DIR"
    $SUDO chmod -R a+rX "$DATA_DIR/media" "$DATA_DIR/staticfiles"
    $SUDO chmod 750 "$DATA_DIR/backups"
    ok "data directories ready under $DATA_DIR"
}

write_env_file() {
    if [ -f "$ENV_FILE" ]; then
        ok ".env already exists — leaving it alone"
        return 0
    fi
    require_domain
    log "generating ${ENV_FILE} with fresh secrets"
    local secret pgpass
    secret="$(random_secret)"
    pgpass="$(random_secret)"
    sed \
        -e "s#^DJANGO_SECRET_KEY=.*#DJANGO_SECRET_KEY=${secret}#" \
        -e "s#^DJANGO_ALLOWED_HOSTS=.*#DJANGO_ALLOWED_HOSTS=${DOMAIN},localhost,127.0.0.1#" \
        -e "s#^DATABASE_URL=.*#DATABASE_URL=postgres://wadi:${pgpass}@postgres:5432/wadi_elsafar#" \
        -e "s#^POSTGRES_PASSWORD=.*#POSTGRES_PASSWORD=${pgpass}#" \
        -e "s#^DATA_DIR=.*#DATA_DIR=${DATA_DIR}#" \
        -e "s#^WEB_PORT=.*#WEB_PORT=${WEB_PORT}#" \
        "${SCRIPT_DIR}/env.production.example" > "$ENV_FILE"
    chmod 600 "$ENV_FILE"
    ok "wrote ${ENV_FILE} (mode 600)"
    warn "CORS_ALLOWED_ORIGINS and the ZOHO_/EMAIL_/SENTRY_ keys still hold placeholder values — edit .env before going live."
}

render_nginx() {
    local template="$1" tmp
    need nginx
    require_domain
    tmp="$(mktemp)"
    sed \
        -e "s#__DOMAIN__#${DOMAIN}#g" \
        -e "s#__APP_NAME__#${APP_NAME}#g" \
        -e "s#__WEB_PORT__#${WEB_PORT}#g" \
        -e "s#__STATIC_DIR__#${DATA_DIR}/staticfiles#g" \
        -e "s#__MEDIA_DIR__#${DATA_DIR}/media#g" \
        -e "s#__CERTBOT_WEBROOT__#${CERTBOT_WEBROOT}#g" \
        -e "s#__MAX_BODY__#${MAX_BODY}#g" \
        -e "s#__PROXY_TIMEOUT__#${PROXY_TIMEOUT}#g" \
        "$template" > "$tmp"
    $SUDO install -D -m 0644 "$tmp" "/etc/nginx/sites-available/${DOMAIN}.conf"
    rm -f "$tmp"
    $SUDO ln -sfn "/etc/nginx/sites-available/${DOMAIN}.conf" \
                  "/etc/nginx/sites-enabled/${DOMAIN}.conf"
    # Debian's packaged catch-all vhost answers on port 80 for any name and
    # will shadow this one if left enabled.
    if [ -e /etc/nginx/sites-enabled/default ]; then
        $SUDO rm -f /etc/nginx/sites-enabled/default
        warn "removed the packaged nginx 'default' vhost (it shadows ${DOMAIN})"
    fi
    $SUDO nginx -t || die "nginx rejected the generated config for ${DOMAIN}"
    $SUDO systemctl reload nginx
    ok "nginx vhost installed from $(basename "$template")"
}

server_public_ip() {
    local ip=""
    if have curl; then
        ip="$(curl -fsS -m 8 https://api.ipify.org 2>/dev/null || true)"
    fi
    if [ -z "$ip" ] && have ip; then
        ip="$(ip -4 route get 1.1.1.1 2>/dev/null | sed -n 's/.*src \([0-9.]*\).*/\1/p')"
    fi
    printf '%s' "$ip"
}

resolve_a_record() {
    local name="$1"
    if have dig; then
        dig +short A "$name" @1.1.1.1 2>/dev/null | grep -E '^[0-9.]+$' || true
    elif have host; then
        host -t A "$name" 1.1.1.1 2>/dev/null | sed -n 's/.*has address \([0-9.]*\)/\1/p' || true
    else
        getent ahostsv4 "$name" 2>/dev/null | awk '{print $1}' | sort -u || true
    fi
}

# -------------------------------------------------------------- commands ----

cmd_bootstrap() {
    step "Bootstrapping server packages"
    have apt-get || die "bootstrap only handles Debian/Ubuntu. Install docker, nginx and certbot by hand, then run 'init'."

    log "installing base packages"
    $SUDO apt-get update -y
    $SUDO DEBIAN_FRONTEND=noninteractive apt-get install -y \
        ca-certificates curl gnupg git nginx certbot dnsutils openssl ufw

    if ! have docker; then
        log "installing Docker Engine from the official repository"
        $SUDO install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
            | $SUDO gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        $SUDO chmod a+r /etc/apt/keyrings/docker.gpg
        printf 'deb [arch=%s signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu %s stable\n' \
            "$(dpkg --print-architecture)" "$(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")" \
            | $SUDO tee /etc/apt/sources.list.d/docker.list >/dev/null
        $SUDO apt-get update -y
        $SUDO DEBIAN_FRONTEND=noninteractive apt-get install -y \
            docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    else
        ok "docker already installed"
    fi

    $SUDO systemctl enable --now docker
    $SUDO systemctl enable --now nginx

    if [ "$(id -u)" -ne 0 ] && ! id -nG "$USER" | tr ' ' '\n' | grep -qx docker; then
        $SUDO usermod -aG docker "$USER"
        warn "added $USER to the 'docker' group — log out and back in before running 'init'."
    fi

    step "Firewall"
    if have ufw; then
        # OpenSSH is allowed before enabling, otherwise enabling ufw over SSH
        # drops the session that is running this script.
        $SUDO ufw allow OpenSSH >/dev/null
        $SUDO ufw allow 80/tcp >/dev/null
        $SUDO ufw allow 443/tcp >/dev/null
        if $SUDO ufw status | head -1 | grep -q inactive; then
            if confirm "Enable ufw now (SSH, 80 and 443 are already allowed)?"; then
                $SUDO ufw --force enable
            else
                warn "ufw left disabled; ports 80/443 rules are staged for when you enable it."
            fi
        fi
        ok "firewall rules in place (OpenSSH, 80/tcp, 443/tcp)"
    fi

    step "Bootstrap complete"
    cat <<'NEXT'
Next:
  1. cp deploy/deploy.env.example deploy/deploy.env   # set DOMAIN + LETSENCRYPT_EMAIL
  2. deploy/deploy.sh init
  3. deploy/deploy.sh domain
NEXT
}

cmd_init() {
    step "First-time deployment"
    require_domain
    require_docker
    need curl

    write_env_file
    validate_env
    ensure_data_dirs

    step "Building images"
    compose build

    step "Starting datastores"
    compose up -d postgres redis
    log "waiting for postgres and redis healthchecks"
    local i
    for i in $(seq 1 30); do
        if compose ps --format json postgres 2>/dev/null | grep -q '"Health":"healthy"' \
           || compose exec -T postgres pg_isready -q 2>/dev/null; then
            break
        fi
        sleep 2
    done
    compose exec -T postgres pg_isready -q || die "postgres never became ready — check: deploy/deploy.sh logs postgres"
    ok "datastores up"

    step "Applying migrations"
    # A one-off container, so this can never race two starting web replicas.
    compose run --rm --no-deps -e RUN_COLLECTSTATIC=false web python manage.py migrate --noinput

    step "Starting application"
    compose up -d web celery_worker

    step "Health check"
    if health_check 45; then
        ok "gunicorn answered 200 on ${HEALTH_PATH}"
    else
        compose logs --tail 60 web >&2 || true
        die "the app did not become healthy. Logs above; full log: deploy/deploy.sh logs web"
    fi

    git -C "$REPO_ROOT" rev-parse HEAD > "$LAST_GOOD_FILE" 2>/dev/null || true

    step "Admin user"
    if [ -t 0 ] && confirm "Create a Django superuser now?"; then
        compose exec web python manage.py createsuperuser
    else
        log "skipped — create one later with: deploy/deploy.sh superuser"
    fi

    step "Installing the pre-TLS nginx vhost"
    $SUDO mkdir -p "${CERTBOT_WEBROOT}/.well-known/acme-challenge"
    $SUDO chmod -R a+rX "$CERTBOT_WEBROOT"
    render_nginx "${SCRIPT_DIR}/nginx/bootstrap.conf.template"

    step "Initial deployment complete"
    cat <<NEXT
The stack is running behind loopback on port ${WEB_PORT}. It is NOT reachable
over the public internet yet — production settings force HTTPS, so the site
stays behind a 503 until the certificate exists.

Next: deploy/deploy.sh domain
NEXT
}

cmd_dns() {
    step "DNS records required for ${DOMAIN:-<DOMAIN unset>}"
    require_domain
    local ip resolved
    ip="$(server_public_ip)"

    printf '\nCreate this at your DNS provider (the registrar, or wherever the zone is hosted):\n\n'
    printf '  %-6s %-34s %s\n' "Type" "Name" "Value"
    printf '  %-6s %-34s %s\n' "----" "--------------------------------" "------------------------------"
    printf '  %-6s %-34s %s\n' "A" "$DOMAIN" "${ip:-<this server public IPv4>}"
    cat <<'RECORDS'

  TTL: 300 while you are setting things up; raise it once the site is stable.

If the zone sits behind Cloudflare, set the record to "DNS only" (grey cloud)
until the certificate is issued — the orange-cloud proxy terminates TLS itself,
and the HTTP-01 challenge cannot reach this server through it.

RECORDS

    log "checking the live A record"
    resolved="$(resolve_a_record "$DOMAIN")"
    if [ -z "$resolved" ]; then
        warn "${DOMAIN} does not resolve yet. DNS changes can take a few minutes to propagate."
        return 1
    fi
    log "${DOMAIN} resolves to: $(printf '%s' "$resolved" | tr '\n' ' ')"
    if [ -n "$ip" ] && printf '%s\n' "$resolved" | grep -qx "$ip"; then
        ok "the A record points at this server (${ip})"
        return 0
    fi
    warn "the A record does not include this server's IP (${ip:-unknown}) — certificate issuance will fail until it does."
    return 1
}

# Certbot ships options-ssl-nginx.conf and ssl-dhparams.pem with its *nginx
# plugin*. This deployment validates over the webroot instead, so on a server
# without that plugin both files are missing and nginx -t fails on the include.
ensure_tls_assets() {
    if [ ! -f /etc/letsencrypt/options-ssl-nginx.conf ]; then
        log "writing /etc/letsencrypt/options-ssl-nginx.conf"
        $SUDO mkdir -p /etc/letsencrypt
        $SUDO tee /etc/letsencrypt/options-ssl-nginx.conf >/dev/null <<'SSLOPTS'
ssl_session_cache shared:le_nginx_SSL:10m;
ssl_session_timeout 1440m;
ssl_session_tickets off;

ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers off;

ssl_ciphers "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-CHACHA20-POLY1305";
SSLOPTS
    fi
    if [ ! -f /etc/letsencrypt/ssl-dhparams.pem ]; then
        log "generating DH parameters (2048-bit; this takes a minute)"
        $SUDO openssl dhparam -out /etc/letsencrypt/ssl-dhparams.pem 2048
    fi
}

cmd_domain() {
    step "Domain authentication for ${DOMAIN:-<DOMAIN unset>}"
    require_domain
    need certbot
    need nginx
    [ -n "$LETSENCRYPT_EMAIL" ] \
        || die "LETSENCRYPT_EMAIL is not set. Add it to ${DEPLOY_ENV_FILE}."

    step "1/6  DNS"
    if ! cmd_dns; then
        confirm "DNS does not look right yet. Continue anyway?" \
            || die "stopped. Fix the A record, then re-run: deploy/deploy.sh domain"
    fi

    step "2/6  ACME challenge webroot"
    # HTTP-01 proves control of the domain: Let's Encrypt fetches a token from
    # http://DOMAIN/.well-known/acme-challenge/<token>. That path has to be
    # served over plain HTTP by nginx, which is what the bootstrap vhost does.
    $SUDO mkdir -p "${CERTBOT_WEBROOT}/.well-known/acme-challenge"
    $SUDO chmod -R a+rX "$CERTBOT_WEBROOT"
    if [ ! -e "/etc/nginx/sites-enabled/${DOMAIN}.conf" ]; then
        render_nginx "${SCRIPT_DIR}/nginx/bootstrap.conf.template"
    fi

    local token="deploy-selftest-$$"
    printf 'ok\n' | $SUDO tee "${CERTBOT_WEBROOT}/.well-known/acme-challenge/${token}" >/dev/null
    if curl -fsS -m 10 "http://${DOMAIN}/.well-known/acme-challenge/${token}" 2>/dev/null | grep -qx ok; then
        ok "the challenge path is reachable from the public internet"
    else
        warn "could not fetch http://${DOMAIN}/.well-known/acme-challenge/${token} from outside."
        warn "Usual causes: DNS not propagated, port 80 blocked by a firewall or cloud security group, or a proxy in front."
        confirm "Ask Let's Encrypt for a certificate anyway?" \
            || { $SUDO rm -f "${CERTBOT_WEBROOT}/.well-known/acme-challenge/${token}"; die "stopped."; }
    fi
    $SUDO rm -f "${CERTBOT_WEBROOT}/.well-known/acme-challenge/${token}"

    step "3/6  Certificate"
    if [ -d "/etc/letsencrypt/live/${DOMAIN}" ] && [ "${FORCE_RENEW:-false}" != "true" ]; then
        ok "a certificate for ${DOMAIN} already exists — keeping it (FORCE_RENEW=true to reissue)"
    else
        local staging_flag=""
        if [ "${LETSENCRYPT_STAGING:-false}" = "true" ]; then
            staging_flag="--staging"
            warn "using the Let's Encrypt STAGING environment — the resulting certificate is not publicly trusted."
        fi
        # --webroot rather than --nginx: no plugin rewrites the vhost, so the
        # config in deploy/nginx stays the single source of truth.
        # shellcheck disable=SC2086
        $SUDO certbot certonly \
            --webroot -w "$CERTBOT_WEBROOT" \
            -d "$DOMAIN" \
            --email "$LETSENCRYPT_EMAIL" \
            --agree-tos --no-eff-email \
            --non-interactive --keep-until-expiring \
            $staging_flag
        ok "certificate issued for ${DOMAIN}"
    fi

    step "4/6  TLS vhost"
    ensure_tls_assets
    render_nginx "${SCRIPT_DIR}/nginx/site.conf.template"

    step "5/6  Automatic renewal"
    # Certificates last 90 days. certbot's packaged timer renews anything
    # inside 30 days of expiry; the deploy hook makes nginx pick up the new
    # file, which it otherwise would not until the next restart.
    $SUDO mkdir -p /etc/letsencrypt/renewal-hooks/deploy
    $SUDO tee /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh >/dev/null <<'HOOK'
#!/bin/sh
# Installed by deploy/deploy.sh — reload nginx after a certificate renews.
systemctl reload nginx
HOOK
    $SUDO chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
    if systemctl list-unit-files 2>/dev/null | grep -q '^certbot.timer'; then
        $SUDO systemctl enable --now certbot.timer
        ok "certbot.timer enabled"
    else
        warn "no certbot.timer on this system — add a cron entry: 0 3 * * * certbot renew --quiet"
    fi
    log "renewal dry run"
    $SUDO certbot renew --dry-run --cert-name "$DOMAIN" \
        && ok "renewal dry run passed" \
        || warn "renewal dry run failed — renewals will need attention before the 90-day expiry"

    step "6/6  End-to-end check"
    if curl -fsS -m 15 "https://${DOMAIN}${HEALTH_PATH}" >/dev/null 2>&1; then
        ok "https://${DOMAIN}${HEALTH_PATH} answered 200"
    else
        warn "https://${DOMAIN}${HEALTH_PATH} did not answer 200."
        warn "Check that ${DOMAIN} is in DJANGO_ALLOWED_HOSTS in .env, then: deploy/deploy.sh restart"
    fi

    step "Domain live"
    cat <<NEXT
  API      https://${DOMAIN}/api/v1/
  Admin    https://${DOMAIN}/admin/
  Health   https://${DOMAIN}${HEALTH_PATH}

Remaining manual steps:
  * .env  -> DJANGO_ALLOWED_HOSTS must contain ${DOMAIN}
  * .env  -> CORS_ALLOWED_ORIGINS must contain every frontend origin
             (the JWT refresh cookie is SameSite=None; Secure, so those
             origins have to be https:// in production)
  After editing .env: deploy/deploy.sh restart
NEXT
}

cmd_update() {
    step "Updating deployment"
    require_docker
    need git
    validate_env

    local prev target
    prev="$(git -C "$REPO_ROOT" rev-parse HEAD)"
    log "current revision: ${prev:0:12}"

    if [ -n "$(git -C "$REPO_ROOT" status --porcelain)" ]; then
        git -C "$REPO_ROOT" status --short >&2
        confirm "The working tree has local changes (shown above). Continue?" \
            || die "stopped. Commit or stash the changes first."
    fi

    if [ "${SKIP_BACKUP:-false}" != "true" ]; then
        step "Backing up the database first"
        cmd_backup
    fi

    step "Fetching ${GIT_BRANCH}"
    git -C "$REPO_ROOT" fetch --prune origin "$GIT_BRANCH"
    target="$(git -C "$REPO_ROOT" rev-parse "origin/${GIT_BRANCH}")"
    if [ "$target" = "$prev" ]; then
        ok "already at origin/${GIT_BRANCH} (${target:0:12})"
    else
        git -C "$REPO_ROOT" log --oneline "${prev}..${target}" | sed 's/^/    /'
        # --ff-only, so a rewritten branch stops here rather than silently
        # discarding whatever is on the server.
        git -C "$REPO_ROOT" merge --ff-only "origin/${GIT_BRANCH}" \
            || die "cannot fast-forward to origin/${GIT_BRANCH}. Resolve by hand on the server."
        ok "updated to ${target:0:12}"
    fi

    step "Rebuilding images"
    compose build

    step "Applying migrations"
    compose run --rm --no-deps -e RUN_COLLECTSTATIC=false web python manage.py migrate --noinput

    step "Restarting services"
    ensure_data_dirs
    compose up -d --remove-orphans

    step "Health check"
    if health_check 45; then
        ok "gunicorn answered 200 on ${HEALTH_PATH}"
        printf '%s\n' "$target" > "$LAST_GOOD_FILE"
    else
        compose logs --tail 60 web >&2 || true
        if [ "${NO_ROLLBACK:-false}" = "true" ]; then
            die "health check failed. NO_ROLLBACK=true, so the new revision is left running."
        fi
        warn "health check failed — rolling the code back to ${prev:0:12}"
        # Code only. Migrations that already applied are NOT reversed: if the
        # failure came from a migration, restore the dump this run just took.
        git -C "$REPO_ROOT" reset --hard "$prev"
        compose build
        compose up -d --remove-orphans
        if health_check 45; then
            warn "rolled back to ${prev:0:12} and the old revision is healthy."
            warn "Any migrations from ${target:0:12} are still applied. Latest dump: ${DATA_DIR}/backups"
        else
            die "rollback did not come back healthy either. Investigate: deploy/deploy.sh logs web"
        fi
        exit 1
    fi

    if [ -e "/etc/nginx/sites-enabled/${DOMAIN}.conf" ] && [ -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]; then
        step "Refreshing the nginx vhost"
        render_nginx "${SCRIPT_DIR}/nginx/site.conf.template"
    fi

    step "Pruning old images"
    docker image prune -f >/dev/null && ok "dangling images removed"

    step "Update complete — now at ${target:0:12}"
}

cmd_rollback() {
    step "Rolling back"
    require_docker
    need git
    local ref="${1:-}"
    if [ -z "$ref" ]; then
        [ -f "$LAST_GOOD_FILE" ] || die "no revision given and no ${LAST_GOOD_FILE} recorded. Pass one: deploy/deploy.sh rollback <commit>"
        ref="$(cat "$LAST_GOOD_FILE")"
    fi
    git -C "$REPO_ROOT" rev-parse --verify "$ref" >/dev/null 2>&1 || die "unknown revision: $ref"
    confirm "Reset the working tree to ${ref} and redeploy? (migrations are NOT reversed)" || die "stopped."

    git -C "$REPO_ROOT" reset --hard "$ref"
    compose build
    compose up -d --remove-orphans
    health_check 45 && ok "healthy at ${ref}" || die "still unhealthy: deploy/deploy.sh logs web"
}

cmd_backup() {
    require_docker
    ensure_data_dirs
    local stamp file
    stamp="$(date +%Y%m%d-%H%M%S)"
    file="${DATA_DIR}/backups/db-${stamp}.sql.gz"
    log "dumping the database to ${file}"
    compose exec -T postgres pg_dump -U "$(env_get POSTGRES_USER)" -d "$(env_get POSTGRES_DB)" \
        | gzip -9 | $SUDO tee "$file" >/dev/null
    $SUDO chmod 640 "$file"
    ok "database dump written ($(du -h "$file" 2>/dev/null | cut -f1))"

    if [ "${BACKUP_MEDIA:-false}" = "true" ]; then
        local mfile="${DATA_DIR}/backups/media-${stamp}.tar.gz"
        log "archiving uploaded media to ${mfile}"
        $SUDO tar -czf "$mfile" -C "$DATA_DIR" media
        ok "media archive written"
    fi

    # Keep two weeks of dumps; the volume is not a backup destination.
    $SUDO find "${DATA_DIR}/backups" -name 'db-*.sql.gz' -mtime +14 -delete 2>/dev/null || true
}

cmd_restore() {
    local file="${1:-}"
    [ -n "$file" ] || die "usage: deploy/deploy.sh restore <path/to/db-YYYYmmdd-HHMMSS.sql.gz>"
    [ -f "$file" ] || die "no such file: $file"
    require_docker
    warn "This DROPS the current contents of $(env_get POSTGRES_DB) and replaces them with ${file}."
    confirm "Continue?" || die "stopped."

    compose stop web celery_worker
    gunzip -c "$file" | compose exec -T postgres psql -U "$(env_get POSTGRES_USER)" -d "$(env_get POSTGRES_DB)"
    compose up -d web celery_worker
    health_check 45 && ok "restored and healthy" || die "unhealthy after restore: deploy/deploy.sh logs web"
}

cmd_nginx()     { render_nginx "${SCRIPT_DIR}/nginx/site.conf.template"; }
cmd_status()    { require_docker; compose ps; }
cmd_logs()      { require_docker; compose logs -f --tail "${TAIL:-100}" "$@"; }
cmd_restart()   { require_docker; compose up -d --force-recreate web celery_worker; health_check 45 && ok "healthy" || die "unhealthy: deploy/deploy.sh logs web"; }
cmd_stop()      { require_docker; compose stop; ok "stopped (data volumes untouched)"; }
cmd_manage()    { require_docker; compose exec web python manage.py "$@"; }
cmd_superuser() { require_docker; compose exec web python manage.py createsuperuser; }
cmd_shell()     { require_docker; compose exec web bash; }
cmd_psql()      { require_docker; compose exec postgres psql -U "$(env_get POSTGRES_USER)" -d "$(env_get POSTGRES_DB)"; }

cmd_help() {
    cat <<'HELP'
Wadi Al Safar backend — deploy/deploy.sh

Setup, in order
  bootstrap            Install docker, nginx, certbot, ufw on a fresh Ubuntu/Debian server
  init                 First deployment: .env, build, migrate, start, pre-TLS nginx vhost
  domain               DNS check, Let's Encrypt HTTP-01 validation, TLS vhost, auto-renewal

Day to day
  update               Fetch origin/<branch>, rebuild, migrate, restart, health-check
                       (rolls the code back automatically if the health check fails)
  rollback [commit]    Redeploy an earlier commit (defaults to the last healthy one)
  restart              Recreate web + celery_worker (use after editing .env)
  status               docker compose ps
  logs [service]       Follow logs (TAIL=n to change how much scrollback)
  stop                 Stop every service; volumes are kept

Data
  backup               gzip pg_dump into $DATA_DIR/backups (BACKUP_MEDIA=true adds uploads)
  restore <file>       Replace the database with a dump — destructive

Django
  manage <args...>     manage.py inside the web container
  superuser            manage.py createsuperuser
  shell                bash inside the web container
  psql                 psql inside the postgres container

Other
  dns                  Print the DNS records this domain needs and check the live one
  nginx                Re-render and reload the TLS vhost from deploy/nginx/

Configuration
  deploy/deploy.env    Deployment settings (DOMAIN, LETSENCRYPT_EMAIL, DATA_DIR, ...)
  .env                 Application + compose settings (secrets, DB, CORS)

Environment flags
  ASSUME_YES=true      Answer every prompt with yes (for CI)
  SKIP_BACKUP=true     Skip the pre-update database dump
  NO_ROLLBACK=true     Leave a failed update in place instead of rolling back
  LETSENCRYPT_STAGING=true   Use the Let's Encrypt staging CA while testing
  FORCE_RENEW=true     Reissue the certificate even if a valid one exists
HELP
}

# ------------------------------------------------------------- dispatcher ----

main() {
    local cmd="${1:-help}"
    shift || true
    case "$cmd" in
        bootstrap) cmd_bootstrap "$@" ;;
        init|first|first-time) cmd_init "$@" ;;
        domain|ssl|tls) cmd_domain "$@" ;;
        dns|dns-check) cmd_dns "$@" ;;
        update|deploy) cmd_update "$@" ;;
        rollback) cmd_rollback "$@" ;;
        nginx) cmd_nginx "$@" ;;
        status|ps) cmd_status "$@" ;;
        logs) cmd_logs "$@" ;;
        restart) cmd_restart "$@" ;;
        stop|down) cmd_stop "$@" ;;
        backup) cmd_backup "$@" ;;
        restore) cmd_restore "$@" ;;
        manage) cmd_manage "$@" ;;
        superuser|createsuperuser) cmd_superuser "$@" ;;
        shell|bash) cmd_shell "$@" ;;
        psql) cmd_psql "$@" ;;
        help|-h|--help) cmd_help ;;
        *) printf 'unknown command: %s\n\n' "$cmd" >&2; cmd_help >&2; exit 2 ;;
    esac
}

main "$@"
