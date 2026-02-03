# Quick Start Guide - PostgreSQL Deployment

Railway.app (Production)

###  GitHub Deploy 
```bash
# 1. Push code to GitHub
git add .
git commit -m "Add PostgreSQL support"
git push

### Method B: Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Add PostgreSQL
railway add postgresql

# Add Redis
railway add redis

# Set environment variables
railway variables set SECRET_KEY=your-secret-key
railway variables set DEBUG=False
railway variables set ALLOWED_HOSTS=yourapp.up.railway.app

# Deploy
railway up

# Run migrations
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser
```

---

## 🔧 Environment Variables Reference

### Required for Production:
```bash
SECRET_KEY=<generate-new-secret-key>
DEBUG=False
ALLOWED_HOSTS=yourapp.up.railway.app,yourdomain.com
DATABASE_URL=<auto-provided-by-railway>
REDIS_URL=<auto-provided-by-railway>
```

### Optional:
```bash
CELERY_BROKER_URL=<redis-url>
CELERY_RESULT_BACKEND=<redis-url>
```

---

## 📋 Post-Deployment Checklist



```bash
# On Railway:
railway run python manage.py migrate
railway run python manage.py createsuperuser
railway run python manage.py collectstatic --noinput

# On Docker:
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --noinput
```

---

## 🧪 Testing PostgreSQL Locally

```bash
# With Docker Compose (easiest)
docker-compose up

# Visit:
# - App: http://localhost:8000
# - Admin: http://localhost:8000/admin

# Check database connection:
docker-compose exec web python manage.py dbshell
```

---

## 🔍 Troubleshooting

### "No module named 'dj_database_url'"
```bash
pip install dj-database-url
```

### "Could not connect to database"
```bash
# Check DATABASE_URL is set correctly
echo $DATABASE_URL

```

### Migrations not applying
```bash
# Railway:
railway run python manage.py migrate

# Docker:
docker-compose exec web python manage.py migrate

# Local:
python manage.py migrate
```

##  Quick Commands Reference

| Task | Docker | Railway | Local |
|------|--------|---------|-------|
| Start | `docker-compose up` | `railway up` | `python manage.py runserver` |
| Migrate | `docker-compose exec web python manage.py migrate` | `railway run python manage.py migrate` | `python manage.py migrate` |
| Shell | `docker-compose exec web python manage.py shell` | `railway run python manage.py shell` | `python manage.py shell` |
| Logs | `docker-compose logs -f` | `railway logs` | N/A |
