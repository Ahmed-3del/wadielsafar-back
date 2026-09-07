# Wadi Al Safar — Backend

Django REST API backend. See [../docs/architecture/backend.md](../docs/architecture/backend.md)
for the full architecture writeup and [../docs/api/README.md](../docs/api/README.md)
for the endpoint list and response conventions.

## Prerequisites

- Python 3.12 (the repo was built against `/opt/homebrew/bin/python3.12` —
  the system `python3` may be older and will not work with this Django
  version).
- Docker + Docker Compose (for PostgreSQL and Redis).

## Setup

```bash
cd wadi-elsafar-back
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements/development.txt

cp .env.example .env   # edit DJANGO_SECRET_KEY at minimum
```

From the repo root, start Postgres and Redis:

```bash
docker compose up -d postgres redis
```

> Postgres is published on **host port 5433**, not 5432 — many dev machines
> already run a local Postgres bound to 5432 (Homebrew, Postgres.app), which
> silently wins over Docker for `localhost` connections instead of erroring.
> `.env.example`'s `DATABASE_URL` already points at 5433.

Then, with the venv active:

```bash
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/ and role-gated endpoints
python manage.py runserver 0.0.0.0:8000
```

The API is now at `http://localhost:8000/api/v1/`, health check at
`http://localhost:8000/api/v1/health/`.

## Running the whole backend stack via Docker

```bash
docker compose up -d postgres redis backend celery_worker
```

This builds `wadi-elsafar-back/Dockerfile` and runs migrations are **not**
applied automatically — run them once via:

```bash
docker compose exec backend python manage.py migrate
```

## Deploying to a server

Production deployment lives in [deploy/](deploy/) — a Compose stack (gunicorn,
celery, Postgres, Redis) behind host nginx with a Let's Encrypt certificate.
One script drives all of it:

```bash
./deploy/deploy.sh bootstrap   # once per server: docker, nginx, certbot, ufw
./deploy/deploy.sh init        # first deployment: .env, build, migrate, start
./deploy/deploy.sh domain      # DNS check, certificate, TLS vhost, auto-renewal
./deploy/deploy.sh update      # pull, rebuild, migrate, restart, health-check
./deploy/deploy.sh seed        # airports, cruise ports, contact form questions
```

`seed` loads reference data only — nobody edits it in the panel, nothing is
deleted, and re-running it is free. `seed --demo` adds the demonstration
catalogue on top, which resets seeded rows and deletes the hotels, packages,
visas, offers and cruises the seeders do not own; it asks before it does.

`update` backs up the database first and rolls the code back automatically if
the new revision fails its health check. Full runbook, including the domain
authentication steps and troubleshooting, in [deploy/README.md](deploy/README.md).

## Tests & linting

```bash
pytest
ruff check .
black --check .
```

## Bulk import from a spreadsheet

Eleven resources take a filled-in .xlsx or .csv from the panel — airports,
cruise ports, cruises, hotels, flights, visas, visa countries, destinations,
packages, offers and services. Each gets two endpoints from
[`common/imports`](common/imports/):

```
GET  /api/v1/<resource>/import-template/   the blank sheet, with a help sheet beside it
POST /api/v1/<resource>/import/            send it back (`dry_run=true` to rehearse)
```

Rows validate through the resource's own serializer, so an import cannot write
anything the panel's forms would have refused, and there is no second
definition of a valid hotel. Three rules shape the rest:

- **All or nothing.** A sheet is one act to whoever sent it; a half-applied one
  is worse than a refusal that lists what to fix.
- **Match, never delete.** A row whose key already exists is updated in place.
- **References by name.** The sheet asks for a destination's name, not its id.

Adding a resource is a `BulkImportMixin` on its viewset plus a column list in
[`common/imports/columns.py`](common/imports/columns.py), where every `help`
line is what an agent reads in the template.

## The shipped catalogues

Airports and cruise ports are reference data, kept as CSV beside the app that
owns them and loaded by `seed_airports` / `seed_cruise_ports`:

| File | Rows | Built by |
| --- | --- | --- |
| `apps/airports/data/airports.csv` | every airport with an IATA code and a timetable, ~4,000 across 233 countries | `python apps/airports/data/build_catalogue.py` |
| `apps/cruises/data/ports.csv` | the ports cruises sail from, ~290 across 104 countries | `python apps/cruises/data/build_catalogue.py` |

Both builders take their facts from sources — OurAirports, Wikidata, and CLDR
for country names, which is where the panel's country picker gets them too —
and neither will overwrite a name somebody checked by hand or delete a row that
is in the catalogue but not in the source. The cruise-port list is the one that
is curated rather than downloaded: no open dataset says which of the world's
eleven thousand ports a cruise leaves from, so the candidates are written down
in the script and every one of them is verified against Wikidata before it is
written. Read the docstring at the top of either file before regenerating.

Run them only when a catalogue needs refreshing; day to day the CSVs are the
source of truth and the seeders are safe to re-run against a live database.

## Project layout

See [../docs/architecture/backend.md](../docs/architecture/backend.md).
Short version: `config/` holds settings/URL wiring, `apps/` holds one
Django app per business domain (each with its own
models/serializers/views/services/filters/permissions/tests split), and
`common/` holds cross-app building blocks (base model, pagination,
permissions, exception handling).

## Environment variables

See `.env.example` for the full list. Notable ones:

- `DATABASE_URL`, `REDIS_URL` — connection strings.
- `CORS_ALLOWED_ORIGINS` — must include the frontend (`:3000`) and panel
  (`:5173`) origins for the browser-based JWT refresh flow to work.
- `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` / `JWT_REFRESH_TOKEN_LIFETIME_DAYS`.
- `ZOHO_*` — unused until the Zoho CRM integration is implemented past its
  current stub (`apps/integrations/zoho`).
# wadielsafar-back
