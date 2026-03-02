# Environment Parity Protocol
**SPMO Suite - Configuration Management**  
**Version**: 1.0  
**Effective Date**: 2026-02-12

---

## 🎯 Purpose

Ensure consistency and parity across Local, Dev, and Production environments while maintaining appropriate differences for each tier.

---

## 🔧 Configuration Management

### Environment Variables

**Shared Across All Environments**:
```bash
# Database configuration structure (values differ)
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=5432

# Application structure
SSPMO_HUB_URL=
```

**Environment-Specific Values**:

| Variable | Local | Dev Server | Production |
|:---------|:------|:-----------|:-----------|
| `DEBUG` | True | True | **False** |
| `ENVIRONMENT` | local | staging | production |
| `SECRET_KEY` | local-key | staging-key | **prod-key** |
| `ALLOWED_HOSTS` | localhost,127.0.0.1 | sspmo-dev.up.edu.ph,... | sspmo.up.edu.ph,... |
| `DB_HOST` | localhost or db | db | db |
| `SSPMO_HUB_URL` | http://localhost:8000 | https://sspmo-dev.up.edu.ph | https://sspmo.up.edu.ph |

**Critical Rules**:
1. Each environment MUST have unique `SECRET_KEY`
2. Production MUST have `DEBUG=False`
3. Never commit `.env` files to Git
4. Use `.env.example` as template

---

## 🗄️ Database Management

### Database Strategy

**Local**:
- SQLite or local PostgreSQL
- Development/dummy data
- Can be reset frequently

**Dev Server**:
- PostgreSQL (shared container)
- **Sanitized copy** of production data
- Refreshed monthly from production

**Production**:
- PostgreSQL (shared container)
- Live user data
- Regular backups (daily)

### Data Sanitization

When copying production data to dev server:

```python
# scripts/sanitize_for_dev.py
# Anonymize PII before copying to dev server

# Replace real names
UPDATE auth_user SET 
  first_name = 'Test',
  last_name = CONCAT('User', id),
  email = CONCAT('testuser', id, '@example.com');

# Mask phone numbers
UPDATE user_profile SET
  phone = '0900-000-0000';

# Remove sensitive documents
DELETE FROM uploaded_documents WHERE is_sensitive = true;
```

**Refresh Schedule**: Monthly (first Monday of each month)

---

## 📦 Dependency Management

### Python Dependencies

**File**: `requirements.txt`

**Rule**: All environments use the **same** `requirements.txt`

**Process**:
```bash
# Add new dependency locally
pip install django-import-export
pip freeze > requirements.txt

# Commit to Git
git add requirements.txt
git commit -m "chore: add django-import-export dependency"

# Deploy to dev server
ssh -p 9913 ajbasa@172.20.3.92
cd ~/spmo_suite
git pull origin staging
docker-compose exec app_hub pip install -r requirements.txt
docker-compose restart

# After UAT, deploy to production
ssh -p 9913 ajbasa@172.20.3.91
cd ~/spmo_suite
git pull origin main
docker-compose exec app_hub pip install -r requirements.txt
docker-compose restart
```

---

## 🐳 Docker Configuration

### docker-compose.yml

**Rule**: Same `docker-compose.yml` across all environments

**Environment-Specific Behavior**: Controlled via `.env` file

**Example**:
```yaml
# docker-compose.yml (same everywhere)
services:
  app_hub:
    environment:
      - DEBUG=${DEBUG}
      - ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS}
      - SECRET_KEY=${DJANGO_SECRET_KEY}
```

**Differences Managed Via**:
- `.env` (local)
- `.env` (dev server - different values)
- `.env` (production - different values)

---

## 🌐 Nginx Configuration

### Configuration Files

**File**: `nginx/conf.d/default.conf`

**Strategy**: Single file with all environments configured

**Example**:
```nginx
# Hub - Production
server {
    listen 80;
    server_name sspmo.up.edu.ph;
    location / {
        proxy_pass http://app_hub:8000;
    }
}

# Hub - Dev
server {
    listen 80;
    server_name sspmo-dev.up.edu.ph;
    location / {
        proxy_pass http://app_hub:8000;
    }
}
```

**Deployment**: Same file deployed to both servers, Nginx serves based on domain

---

## 🔐 Secret Management

### Secret Types

| Secret Type | Storage | Rotation |
|:------------|:--------|:---------|
| `SECRET_KEY` | `.env` (not committed) | Annually |
| Database passwords | `.env` (not committed) | Quarterly |
| API keys | `.env` (not committed) | As needed |
| SSH keys | Server only | Annually |

### Secret Rotation Process

1. Generate new secret
2. Update `.env` on target server
3. Restart containers
4. Verify functionality
5. Document rotation in `docs/security/secret_rotation_log.md`

---

## 📊 Parity Checklist

Before deploying to production, verify:

- [ ] Same Python version across all environments
- [ ] Same Django version across all environments
- [ ] Same `requirements.txt` deployed
- [ ] Same `docker-compose.yml` structure
- [ ] Database migrations tested on dev server
- [ ] Static files collected successfully
- [ ] Environment variables configured correctly
- [ ] Nginx configuration updated (if changed)

---

## 🚨 Parity Violations

### Common Violations

1. **Different Python versions**: Can cause dependency issues
2. **Different Django versions**: Can cause migration issues
3. **Missing environment variables**: Can cause runtime errors
4. **Outdated dependencies**: Can cause security vulnerabilities

### Detection

```bash
# Check Python version
python --version

# Check Django version
python -c "import django; print(django.get_version())"

# Check installed packages
pip freeze

# Compare environments
diff <(ssh -p 9913 ajbasa@172.20.3.92 "cd ~/spmo_suite && pip freeze") \
     <(ssh -p 9913 ajbasa@172.20.3.91 "cd ~/spmo_suite && pip freeze")
```

---

## 🔄 Synchronization Schedule

| Task | Frequency | Responsibility |
|:-----|:----------|:---------------|
| Dev data refresh | Monthly | Developer |
| Dependency updates | As needed | Developer |
| Secret rotation | Quarterly | SysOps |
| Configuration audit | Quarterly | SysOps |

---

**Approved By**: User (ajbasa)  
**Next Review**: 2026-05-12
