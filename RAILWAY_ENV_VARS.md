# Railway Environment Variables Guide

## Required Environment Variables

### Web Service Variables

Copy these into Railway web service → Variables tab:

```bash
# Django Secret Key (generate a new one)
SECRET_KEY=django-insecure-CHANGE-THIS-TO-A-RANDOM-50-CHARACTER-STRING

# Production settings
DEBUG=False

# Allow your Railway domain
ALLOWED_HOSTS=web-production-11cc.up.railway.app

# Database (auto-set by Railway when you add PostgreSQL)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis (auto-set by Railway when you add Redis)
REDIS_URL=${{Redis.REDIS_URL}}
```

### Worker Service Variables

Copy these into Railway worker service → Variables tab:

```bash
# Reference web service secret key
SECRET_KEY=${{web.SECRET_KEY}}

# Production mode
DEBUG=False

# Database connection
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis for Celery
REDIS_URL=${{Redis.REDIS_URL}}
```

---

## How to Generate SECRET_KEY

Run this locally to generate a secure secret key:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Copy the output and use it for `SECRET_KEY` in Railway.

---

## Railway Services Setup

### 1. PostgreSQL Database
- Click "+ New" → Database → PostgreSQL
- Railway will auto-create `DATABASE_URL` variable

### 2. Redis
- Click "+ New" → Database → Redis  
- Railway will auto-create `REDIS_URL` variable

### 3. Web Service
- Already exists
- Add variables listed above
- Railway will use `railway.toml` config

### 4. Worker Service
- Already exists
- Add variables listed above
- Uses same code, different start command (from Procfile)

---

## After Deployment

Once Railway shows both services as "Deployed":

```bash
# Run database migrations
railway run python manage.py migrate

# Create admin user
railway run python manage.py createsuperuser

# Collect static files
railway run python manage.py collectstatic --noinput
```

---

## Testing Your Deployment

Visit these URLs (replace with your actual Railway domain):

- **Homepage:** `https://web-production-11cc.up.railway.app/`
- **Admin:** `https://web-production-11cc.up.railway.app/admin/`
- **API:** `https://web-production-11cc.up.railway.app/api/`

---

## Troubleshooting

### Worker shows "Crashed"
- This is normal! Railway can't health-check background workers
- Check logs - if you see "celery@... ready", it's working

### Web service 502 error
- Check environment variables are set correctly
- Verify `ALLOWED_HOSTS` matches your Railway domain
- Check deploy logs for Python errors

### Database errors
- Make sure you ran migrations: `railway run python manage.py migrate`
- Verify `DATABASE_URL` is set in variables

---

## Summary

**Required:**
- ✅ SECRET_KEY (generate new for production)
- ✅ DEBUG=False
- ✅ ALLOWED_HOSTS (your Railway domain)
- ✅ DATABASE_URL (auto-set)
- ✅ REDIS_URL (auto-set)

**Optional:**
- CELERY_BROKER_URL (defaults to REDIS_URL)
- CELERY_RESULT_BACKEND (defaults to REDIS_URL)
