FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/development.txt

COPY . .

EXPOSE 8000

# docker-compose.yml overrides this per-service (runserver for `backend`,
# `celery -A config worker -l info` for `celery_worker`) — this is just a
# sane default for running the image standalone.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
