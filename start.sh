#!/bin/bash
# Startup script - create static dir, run migrations, collect static, start gunicorn
set -e
echo "----------------------------------------"
echo "EXECUTING START.SH"
echo "----------------------------------------"

echo "Creating staticfiles directory..."
mkdir -p staticfiles

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting gunicorn..."
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --log-level info
