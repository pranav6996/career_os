# Minimal Procfile - web runs migrations then starts, worker runs celery
web: bash start.sh
worker: celery -A core worker --loglevel=info
