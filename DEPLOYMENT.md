# Railway Deployment Guide

## Step 1: Add PostgreSQL
1. In Railway dashboard, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Done! Railway auto-connects it

## Step 2: Add Redis
1. Click "+ New" again
2. Select "Database" → "Redis"
3. Done! Railway auto-connects it

## Step 3: Set Environment Variables
Click on your **web** service → **Variables** tab → Add these:

```
SECRET_KEY=your-secret-key-here-make-it-long-and-random
DEBUG=False
ALLOWED_HOSTS=your-app.up.railway.app
```

## Step 4: Run Migrations
After deployment, run these commands:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link your project
railway link

# Run migrations
railway run python manage.py migrate

# Create admin user
railway run python manage.py createsuperuser
```

## Step 5: Visit Your App
Your app will be at: `https://your-app.up.railway.app`

Admin panel: `https://your-app.up.railway.app/admin`

---

## Troubleshooting

**"Module not found" errors:**
- Railway should auto-install from requirements.txt
- Check the build logs

**"Database not found":**
- Make sure PostgreSQL is added
- Check DATABASE_URL is set in variables

**Jobs not scraping:**
- Make sure Redis is added
- Check worker service is running
