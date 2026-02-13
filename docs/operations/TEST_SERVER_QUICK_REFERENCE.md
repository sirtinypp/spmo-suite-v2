# 🔄 Quick Reference: Test Server Deployment

**For when IT approves the test server**

---

## 🎯 What You Requested from IT

### Domains
- `staging.sspmo.up.edu.ph`
- `gamit-staging.sspmo.up.edu.ph`
- `lipad-staging.sspmo.up.edu.ph`
- `suplay-staging.sspmo.up.edu.ph`

### Server Requirements
- Ubuntu 20.04+ with Docker support
- 4GB RAM, 2 CPU cores, 50GB storage
- Ports: 80, 443, 9913 (SSH)
- SSL certificates for all domains

---

## 🌳 Git Setup (Do This First)

```bash
# 1. Standardize branch names (choose one)
# If keeping 'master' for production:
git checkout master
git branch -m master main  # Rename to main
git push -u origin main
git push origin --delete master

# 2. Create staging branch
git checkout main
git checkout -b staging
git push -u origin staging

# 3. Create develop branch
git checkout staging
git checkout -b develop
git push -u origin develop

# 4. Set default branch on GitHub/GitLab to 'main'
```

---

## 🚀 When Test Server is Ready

### Initial Setup (One-time)

```bash
# SSH into test server
ssh -p [PORT] [USER]@[TEST-SERVER-IP]

# Clone repository
git clone [YOUR-REPO-URL] spmo_suite
cd spmo_suite
git checkout staging

# Copy environment template
cp .env.example .env.staging

# Edit .env.staging with test server values
nano .env.staging
# Set: DEBUG=True, staging domains, unique SECRET_KEY

# Start services
docker-compose up -d

# Run migrations
docker-compose exec app_hub python manage.py migrate
docker-compose exec app_gamit python manage.py migrate
docker-compose exec app_gfa python manage.py migrate
docker-compose exec app_store python manage.py migrate

# Collect static files
docker-compose exec app_hub python manage.py collectstatic --noinput
```

---

## 📋 Daily Workflow

### Deploying to Test Server

```bash
# 1. Local: Merge your changes to staging
git checkout staging
git merge develop
git push origin staging

# 2. Test Server: Pull and restart
ssh -p [PORT] [USER]@[TEST-SERVER-IP]
cd ~/spmo_suite
git pull origin staging
docker-compose restart

# 3. Test at: https://staging.sspmo.up.edu.ph
```

### Deploying to Production (After Testing)

```bash
# 1. Merge staging to main
git checkout main
git merge staging
git tag -a v2.1.0 -m "Release v2.1.0"
git push origin main --tags

# 2. Production: Pull and restart
ssh -p 9913 ajbasa@172.20.3.91
cd ~/spmo_suite
git pull origin main
docker-compose restart
```

---

## ⚠️ Remember

- ✅ Always test on staging first
- ✅ Never commit `.env` files
- ✅ Use different SECRET_KEY for each environment
- ❌ Never connect test server to production database
- ❌ Never skip staging and deploy directly to production

---

**Full Documentation**: [TEST_SERVER_DEPLOYMENT_STRATEGY.md](./TEST_SERVER_DEPLOYMENT_STRATEGY.md)
