# Minimal Procfile - just web and worker
web: gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A core worker --loglevel=info
