#!/bin/sh

# Wait for the database to be ready
until python - <<'PY'
import os
import socket

host = os.environ.get("DB_HOST", "db")
port = int(os.environ.get("DB_PORT", 5432))

try:
    socket.create_connection((host, port), timeout=2).close()
except OSError:
    raise SystemExit(1)
PY
do
    echo "Waiting for database..."
    sleep 1
done

echo "Postgres ready. Do migrations..."
python manage.py makemigrations
python manage.py migrate

python manage.py collectstatic --noinput

exec gunicorn munch.wsgi:application --bind 0.0.0.0:8000 --workers 3