#!/bin/bash
# Run migrations and collectstatic, then start gunicorn
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
