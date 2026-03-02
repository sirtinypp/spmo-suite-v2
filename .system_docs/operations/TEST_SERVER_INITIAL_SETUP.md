# 🚀 Test Server Initial Setup Guide

**Server**: 202.92.140.157 (172.20.3.92)  
**Domains**: sspmo-dev.up.edu.ph (and app-specific subdomains)  
**Status**: Ready for initial deployment

---

## ✅ Pre-Deployment Checklist

Before deploying to the test server, complete these steps locally:

### 1. Create Git Branches

```bash
# Navigate to your local repository
cd "C:\Users\Aaron\spmo-suite - Copy"

# Ensure you're on the latest production code
git checkout main
git pull origin main

# Create staging branch (for test server)
git checkout -b staging
git push -u origin staging

# Create develop branch (for daily development)
git checkout -b develop
git push -u origin develop

# Verify branches
git branch -a
```

### 2. Verify Server Connectivity

```bash
# Test SSH connection to dev server
ssh -p 9913 ajbasa@172.20.3.92

# If successful, you should see the server prompt
# Type 'exit' to disconnect
```

---

## 🔧 Initial Server Setup (One-Time)

### Step 1: SSH into Test Server

```bash
ssh -p 9913 ajbasa@172.20.3.92
```

### Step 2: Clone Repository

```bash
# Clone the repository
git clone https://github.com/[YOUR-ORG]/spmo-suite.git spmo_suite
cd spmo_suite

# Checkout staging branch
git checkout staging
```

### Step 3: Configure Environment

```bash
# Create environment file
cp .env.example .env

# Edit the environment file
nano .env
```

**Update `.env` with these values:**

```bash
ENVIRONMENT=staging
DEBUG=True
SECRET_KEY=dev-unique-secret-key-GENERATE-NEW-ONE
SECURE_SSL_REDIRECT=False
SECURE_COOKIES=False

DJANGO_ALLOWED_HOSTS=sspmo-dev.up.edu.ph,gamit-sspmo-dev.up.edu.ph,lipad-sspmo-dev.up.edu.ph,suplay-sspmo-dev.up.edu.ph,localhost,127.0.0.1,172.20.3.92,202.92.140.157

CSRF_TRUSTED_ORIGINS=https://sspmo-dev.up.edu.ph,https://gamit-sspmo-dev.up.edu.ph,https://lipad-sspmo-dev.up.edu.ph,https://suplay-sspmo-dev.up.edu.ph

DB_NAME=postgres
DB_USER=spmo_admin
DB_PASSWORD=secret_password
DB_HOST=db
DB_PORT=5432

SSPMO_HUB_URL=https://sspmo-dev.up.edu.ph
```

**Save and exit** (Ctrl+X, then Y, then Enter)

### Step 4: Start Docker Containers

```bash
# Start all services
docker-compose up -d

# Check container status
docker-compose ps

# All 6 containers should be running:
# - app_hub
# - app_gamit
# - app_gfa
# - app_store
# - spmo_gateway (nginx)
# - spmo_shared_db (postgres)
```

### Step 5: Run Database Migrations

```bash
# Run migrations for all apps
docker-compose exec app_hub python manage.py migrate
docker-compose exec app_gamit python manage.py migrate
docker-compose exec app_gfa python manage.py migrate
docker-compose exec app_store python manage.py migrate
```

### Step 6: Collect Static Files

```bash
docker-compose exec app_hub python manage.py collectstatic --noinput
```

### Step 7: Create Superuser (Optional)

```bash
# Create admin user for each app
docker-compose exec app_hub python manage.py createsuperuser
docker-compose exec app_gamit python manage.py createsuperuser
docker-compose exec app_gfa python manage.py createsuperuser
docker-compose exec app_store python manage.py createsuperuser
```

### Step 8: Verify Deployment

```bash
# Check if apps are responding
curl -I http://localhost:8000  # Hub
curl -I http://localhost:8001  # GAMIT
curl -I http://localhost:8002  # LIPAD
curl -I http://localhost:8003  # SUPLAY

# Check nginx
docker exec spmo_gateway nginx -t

# View logs if needed
docker-compose logs -f --tail=50
```

---

## 🌐 Configure Nginx for Dev Domains

### Update Nginx Configuration

```bash
# Edit nginx config
nano nginx/conf.d/default.conf
```

**Update server_name directives to include dev domains:**

```nginx
# Hub
server {
    listen 80;
    server_name sspmo-dev.up.edu.ph;
    # ... rest of config
}

# GAMIT
server {
    listen 80;
    server_name gamit-sspmo-dev.up.edu.ph;
    # ... rest of config
}

# LIPAD
server {
    listen 80;
    server_name lipad-sspmo-dev.up.edu.ph;
    # ... rest of config
}

# SUPLAY
server {
    listen 80;
    server_name suplay-sspmo-dev.up.edu.ph;
    # ... rest of config
}
```

**Restart nginx:**

```bash
docker-compose restart nginx
```

---

## ✅ Verification

### Test Public Access

From your local machine or browser:

```
https://sspmo-dev.up.edu.ph
https://gamit-sspmo-dev.up.edu.ph
https://lipad-sspmo-dev.up.edu.ph
https://suplay-sspmo-dev.up.edu.ph
```

All should load successfully.

---

## 🔄 Daily Deployment Workflow

After initial setup, use this workflow for daily deployments:

### From Local Machine

```bash
# 1. Make changes locally and commit to develop
git checkout develop
git add .
git commit -m "feat: your changes"
git push origin develop

# 2. Merge to staging when ready to test
git checkout staging
git merge develop
git push origin staging

# 3. Deploy to test server (use the script)
./scripts/deploy_dev.sh

# Or manually:
ssh -p 9913 ajbasa@172.20.3.92
cd ~/spmo_suite
git pull origin staging
docker-compose restart
```

---

## 🆘 Troubleshooting

### Containers Not Starting

```bash
# Check logs
docker-compose logs app_hub
docker-compose logs app_gamit
docker-compose logs app_gfa
docker-compose logs app_store

# Rebuild if needed
docker-compose down
docker-compose up -d --build
```

### Database Connection Issues

```bash
# Check database container
docker-compose logs spmo_shared_db

# Restart database
docker-compose restart spmo_shared_db
```

### Nginx Issues

```bash
# Test nginx config
docker exec spmo_gateway nginx -t

# Check nginx logs
docker-compose logs spmo_gateway

# Restart nginx
docker-compose restart nginx
```

---

## 📝 Next Steps

1. ✅ Complete initial setup on test server
2. Test all applications are accessible
3. Import sanitized test data (if available)
4. Set up automated deployment script
5. Train team on deployment workflow

---

**Status**: Ready for initial deployment  
**Last Updated**: 2026-02-12
