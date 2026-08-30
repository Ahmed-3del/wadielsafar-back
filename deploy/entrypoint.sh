#!/usr/bin/env bash
# Container entrypoint for the `web` and `celery_worker` services.
#
# Migrations are deliberately NOT run here: deploy.sh runs them once as a
# one-off container so two starting replicas can never race each other.
# Set RUN_MIGRATIONS=true to opt in for a single-container deployment.
set -euo pipefail

RUN_MIGRATIONS="${RUN_MIGRATIONS:-false}"
RUN_COLLECTSTATIC="${RUN_COLLECTSTATIC:-true}"
WAIT_FOR_DB_SECONDS="${WAIT_FOR_DB_SECONDS:-60}"

log() { printf '[entrypoint] %s\n' "$*"; }

log "waiting for the database (up to ${WAIT_FOR_DB_SECONDS}s)"
python - "$WAIT_FOR_DB_SECONDS" <<'PY'
import sys, time

import django
from django.db import connections
from django.db.utils import OperationalError

django.setup()
deadline = time.time() + int(sys.argv[1])
while True:
    try:
        connections["default"].ensure_connection()
        break
    except OperationalError as exc:
        if time.time() >= deadline:
            raise SystemExit(f"[entrypoint] database never became reachable: {exc}")
        time.sleep(2)
PY
log "database is up"

if [ "$RUN_MIGRATIONS" = "true" ]; then
    log "applying migrations"
    python manage.py migrate --noinput
fi

if [ "$RUN_COLLECTSTATIC" = "true" ]; then
    # production.py uses CompressedManifestStaticFilesStorage: without a
    # freshly built staticfiles.json manifest, every {% static %} lookup and
    # the admin's own assets raise at request time.
    log "collecting static files"
    python manage.py collectstatic --noinput --clear
fi

log "exec: $*"
exec "$@"
