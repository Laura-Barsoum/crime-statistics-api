# Deployment Guide

This guide provides step-by-step instructions for deploying the US Crime Statistics REST API to production environments.

## Deployment Options

1. **Railway.app** (Easiest - Recommended for coursework)
2. **Render.com** (Easy - Free tier available)
3. **AWS Elastic Beanstalk** (Professional - Bonus points)
4. **DigitalOcean App Platform** (Professional - Bonus points)
5. **PythonAnywhere** (Beginner-friendly)

---

## Option 1: Railway.app (RECOMMENDED - Fastest)

**Time: ~10 minutes**

### Prerequisites
- GitHub account
- Railway.app account (sign up free at https://railway.app)

### Steps

1. **Prepare the Project**

Create a `Procfile` in project root:
```bash
web: gunicorn rest_api.wsgi --log-file -
```

Create `runtime.txt` in project root:
```
python-3.11.0
```

Add to `requirements.txt`:
```
gunicorn==21.2.0
psycopg2-binary==2.9.9
whitenoise==6.6.0
dj-database-url==2.1.0
```

2. **Update Django Settings**

Add to bottom of `rest_api/settings.py`:
```python
import os
import dj_database_url

# Production settings
if not DEBUG:
    ALLOWED_HOSTS = ['*']  # Configure with your domain

    # Database
    DATABASES['default'] = dj_database_url.config(
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600
    )

    # Static files
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    # Security
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

3. **Push to GitHub**

```bash
git init
git add .
git commit -m "Initial commit for deployment"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

4. **Deploy on Railway**

- Go to https://railway.app/
- Click "New Project" → "Deploy from GitHub repo"
- Select your repository
- Railway will auto-detect Django
- Add environment variable: `DEBUG=False`
- Click "Deploy"

5. **Setup Database**

```bash
# Railway CLI (install from https://docs.railway.app/develop/cli)
railway run python manage.py migrate
railway run python manage.py createsuperuser
railway run python manage.py load_crime_data data/state_crime.csv
```

**Done!** Your API is live at `https://your-app.railway.app`

---

## Option 2: Render.com (Free Tier)

**Time: ~15 minutes**

### Steps

1. **Create render.yaml**

Create `render.yaml` in project root:
```yaml
services:
  - type: web
    name: crime-api
    env: python
    buildCommand: pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate
    startCommand: gunicorn rest_api.wsgi:application
    envVars:
      - key: DEBUG
        value: "False"
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: crime-db
          property: connectionString

databases:
  - name: crime-db
    databaseName: crime_stats
    user: crime_user
```

2. **Update requirements.txt**

Add:
```
gunicorn==21.2.0
psycopg2-binary==2.9.9
whitenoise==6.6.0
dj-database-url==2.1.0
```

3. **Update settings.py** (same as Railway option)

4. **Deploy**

- Push to GitHub
- Go to https://render.com
- Click "New" → "Blueprint"
- Connect your GitHub repo
- Render will detect `render.yaml` and deploy

5. **Load Data**

In Render dashboard → Shell:
```bash
python manage.py createsuperuser
python manage.py load_crime_data data/state_crime.csv
```

---

## Option 3: AWS Elastic Beanstalk (BONUS POINTS)

**Time: ~30 minutes**

### Prerequisites
- AWS Account
- AWS CLI installed
- EB CLI installed: `pip install awsebcli`

### Steps

1. **Create .ebextensions/django.config**

```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: rest_api.wsgi:application
  aws:elasticbeanstalk:application:environment:
    DJANGO_SETTINGS_MODULE: rest_api.settings
    DEBUG: "False"
```

2. **Create .ebignore**

```
venv/
*.pyc
__pycache__/
db.sqlite3
.env
.git/
```

3. **Update requirements.txt**

Add:
```
gunicorn==21.2.0
psycopg2-binary==2.9.9
whitenoise==6.6.0
dj-database-url==2.1.0
boto3==1.34.0
```

4. **Initialize EB**

```bash
eb init -p python-3.11 crime-api --region us-east-1
```

5. **Create environment and deploy**

```bash
eb create crime-api-env
eb deploy
```

6. **Set environment variables**

```bash
eb setenv DEBUG=False SECRET_KEY=your-secret-key
```

7. **Setup RDS Database (Optional)**

```bash
eb create crime-api-env --database
```

8. **Load data**

```bash
eb ssh
source /var/app/venv/*/bin/activate
cd /var/app/current
python manage.py migrate
python manage.py createsuperuser
python manage.py load_crime_data data/state_crime.csv
exit
```

**Cost**: ~$10-20/month for t2.micro instance

---

## Option 4: DigitalOcean App Platform (BONUS POINTS)

**Time: ~20 minutes**

### Steps

1. **Create .do/app.yaml**

```yaml
name: crime-statistics-api
services:
  - name: web
    github:
      repo: YOUR_USERNAME/YOUR_REPO
      branch: main
    build_command: pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate
    run_command: gunicorn rest_api.wsgi:application
    envs:
      - key: DEBUG
        value: "False"
      - key: DATABASE_URL
        scope: RUN_TIME
        type: SECRET
    http_port: 8000

databases:
  - name: crime-db
    engine: PG
    version: "15"
```

2. **Update requirements.txt** (same as above)

3. **Deploy**

- Go to https://cloud.digitalocean.com/apps
- Click "Create App" → "GitHub"
- Select repository
- DigitalOcean will detect `.do/app.yaml`
- Click "Next" → "Deploy"

4. **Load data via console**

In App Console:
```bash
python manage.py createsuperuser
python manage.py load_crime_data data/state_crime.csv
```

**Cost**: $5/month for basic app + $7/month for database

---

## Option 5: PythonAnywhere (Beginner-Friendly)

**Time: ~25 minutes**

### Steps

1. **Sign up** at https://www.pythonanywhere.com (free account)

2. **Upload code**

In PythonAnywhere dashboard → Files:
- Upload your project zip
- Extract files

3. **Create virtual environment**

In Bash console:
```bash
cd django_proj
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Configure Web App**

- Go to Web tab → "Add a new web app"
- Choose "Manual configuration"
- Python 3.11
- Set source code: `/home/yourusername/django_proj`
- Set working directory: `/home/yourusername/django_proj`

5. **Configure WSGI file**

Edit `/var/www/yourusername_pythonanywhere_com_wsgi.py`:
```python
import os
import sys

path = '/home/yourusername/django_proj'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'rest_api.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

6. **Setup static files**

In Web tab:
- URL: `/static/`
- Directory: `/home/yourusername/django_proj/staticfiles`

Run:
```bash
python manage.py collectstatic
```

7. **Load data**

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py load_crime_data data/state_crime.csv
```

8. **Reload web app** in Web tab

---

## Production Checklist

Before deploying, ensure:

- [ ] `DEBUG = False` in production
- [ ] `SECRET_KEY` uses environment variable
- [ ] `ALLOWED_HOSTS` configured with your domain
- [ ] Database backups configured
- [ ] Static files served correctly (Whitenoise/CDN)
- [ ] HTTPS enabled (most platforms handle this automatically)
- [ ] Environment variables for sensitive data
- [ ] Database migrations applied
- [ ] Admin user created
- [ ] Data loaded successfully
- [ ] All API endpoints tested in production

## Post-Deployment Testing

Test all endpoints:

```bash
# Replace with your deployed URL
export API_URL="https://your-app.railway.app"

# Test home page
curl $API_URL/

# Test API endpoints
curl $API_URL/api/crime/
curl "$API_URL/api/crime/?state=California"
curl "$API_URL/api/high-crime-states/?year=2015"
curl "$API_URL/api/crime-trends/California/"
curl "$API_URL/api/safest-states/?year=2015"

# Test Swagger UI
open $API_URL/api/docs/
```

## Troubleshooting

### Issue: Static files not loading

**Solution:**
```bash
python manage.py collectstatic --no-input
```

Ensure `STATIC_ROOT` and `STATICFILES_STORAGE` configured.

### Issue: Database connection errors

**Solution:**
- Check `DATABASE_URL` environment variable
- Ensure database service is running
- Verify connection string format

### Issue: 502 Bad Gateway

**Solution:**
- Check application logs
- Verify `gunicorn` is running
- Check `ALLOWED_HOSTS` setting

### Issue: No data loaded

**Solution:**
```bash
python manage.py load_crime_data data/state_crime.csv --clear
```

## Video Demonstration Script

For your coursework video (5 marks), record:

1. **Introduction (30 seconds)**
   - Show your name
   - Project title
   - Technologies used

2. **Home Page Tour (1 minute)**
   - Navigate to deployed URL
   - Show system information
   - Click API documentation link

3. **Swagger UI Demo (2 minutes)**
   - Open Swagger UI
   - Show all endpoints
   - Test one endpoint live (e.g., "Compare States")

4. **Admin Interface (1 minute)**
   - Login to admin
   - Show crime data records
   - Show filters and search

5. **API Testing (2 minutes)**
   - Test high-crime-states endpoint
   - Test crime-trends endpoint
   - Show JSON responses

6. **Code Walkthrough (2 minutes)**
   - Show models.py (database design)
   - Show views.py (endpoints)
   - Show tests.py (unit tests)

7. **Conclusion (30 seconds)**
   - Summary of features
   - Thank you

**Total: ~9 minutes** (under 10-minute typical limit)

## Getting Bonus Points

To maximize your deployment bonus (8 marks):

1. ✅ **Deploy to a real platform** (AWS/DigitalOcean/Render)
2. ✅ **Use a proper database** (PostgreSQL, not SQLite)
3. ✅ **Enable HTTPS** (automatic on most platforms)
4. ✅ **Include deployment URL in README**
5. ✅ **Document deployment process** (this file!)
6. ✅ **Show it running in your video**

## Recommended: Railway.app

For maximum points with minimum hassle:
- **Deploy on Railway.app** (free tier, no credit card needed)
- **Add PostgreSQL database** (free tier includes it)
- **Takes 10 minutes** from start to finish
- **Automatic HTTPS** included
- **Easy to show in video**

Good luck with your deployment! 🚀
