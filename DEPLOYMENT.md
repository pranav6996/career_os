# Quick Start Guide - PostgreSQL Deployment

## 🚀 Three Ways to Deploy with PostgreSQL

---

## Option 1: Docker Compose (Easiest for Local)

```bash
# Start everything (PostgreSQL + Redis + Django + Celery)
docker-compose up --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Visit: http://localhost:8000
```

**What this does:**
- ✅ PostgreSQL database (auto-configured)
- ✅ Redis for Celery
- ✅ Django web server
- ✅ Celery worker
- ✅ All connected automatically!

---

## Option 2: Local PostgreSQL (Mac/Linux)

### Step 1: Install PostgreSQL
```bash
# Mac (with Homebrew)
brew install postgresql@15
brew services start postgresql@15

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
```

### Step 2: Create Database
```bash
# Connect to PostgreSQL
psql postgres

# Create database and user
CREATE DATABASE career_os;
CREATE USER career_os_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE career_os TO career_os_user;
\q
```

### Step 3: Configure .env
```bash
# Create .env file
cp .env.example .env

# Edit .env - add this line:
DATABASE_URL=postgres://career_os_user:your_password@localhost:5432/career_os
```

### Step 4: Run Migrations
```bash
# Install dj-database-url
pip install dj-database-url

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

---

## Option 3: Railway.app (Production)

### Method A: GitHub Deploy (Recommended)
```bash
# 1. Push code to GitHub
git add .
git commit -m "Add PostgreSQL support"
git push

# 2. Go to railway.app → Login with GitHub
# 3. Click "New Project" → "Deploy from GitHub"
# 4. Select your career_os repository
# 5. Railway will:
#    - Detect Dockerfile
#    - Build your app
#    - Create a PostgreSQL database
#    - Auto-set DATABASE_URL
# 6. Add Redis:
#    - Click "New" → "Database" → "Add Redis"
# 7. Set environment variables:
#    - SECRET_KEY=<generate-new-key>
#    - DEBUG=False
#    - ALLOWED_HOSTS=<your-app>.up.railway.app
# 8. Deploy! 🚀
```

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

After deploying, run these commands:

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

# For Railway, it auto-provides this
# For local, check your .env file
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

---

## 🎯 Quick Commands Reference

| Task | Docker | Railway | Local |
|------|--------|---------|-------|
| Start | `docker-compose up` | `railway up` | `python manage.py runserver` |
| Migrate | `docker-compose exec web python manage.py migrate` | `railway run python manage.py migrate` | `python manage.py migrate` |
| Shell | `docker-compose exec web python manage.py shell` | `railway run python manage.py shell` | `python manage.py shell` |
| Logs | `docker-compose logs -f` | `railway logs` | N/A |

---

**You're all set!** Your app now supports PostgreSQL for production. 🚀
