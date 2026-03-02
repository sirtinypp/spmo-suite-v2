# 🧪 Test Server Deployment Strategy & Guidelines
**SPMO Suite - Staging Environment Setup**  
**Date**: 2026-02-12  
**Status**: ✅ IT APPROVED - READY FOR DEPLOYMENT

---

## ✅ IT Approval Received

### Approved Domains
- `sspmo-dev.up.edu.ph` (SPMO Hub - Dev/Test)
- `gamit-sspmo-dev.up.edu.ph` (GAMIT - Dev/Test)
- `lipad-sspmo-dev.up.edu.ph` (LIPAD - Dev/Test)
- `suplay-sspmo-dev.up.edu.ph` (SUPLAY - Dev/Test)

### Server Details
- **Public IP**: `202.92.140.157`
- **Private IP**: `172.20.3.92`
- **SSH Port**: `9913` (assumed same as production)
- **Credentials**: Same as production server
  - Username: `ajbasa`
  - Password: `YuPDaDg5Jd06vTB`

### VPN Access (if needed)
- Username: `ajbasa`
- Password: `UdpGigaVPNspmo`

---

## 📋 Executive Summary

This document outlines the deployment strategy for the SPMO Suite test/staging server, including Git workflow, domain configuration, and deployment practices.

**Note**: IT provided `-dev` suffix instead of `-staging`. This is acceptable and follows the same principles.

---

## 🎯 Deployment Architecture

### Three-Tier Environment Strategy

| Environment | Purpose | Git Branch | Server | Database | Access |
|:------------|:--------|:-----------|:-------|:---------|:-------|
| **Local** | Development | `feature/*`, `develop` | Developer machine | Local PostgreSQL | Developer only |
| **Staging/Test** | Pre-production testing | `staging` | Test server (pending) | Test PostgreSQL | Internal/VPN |
| **Production** | Live system | `main` | 172.20.3.91:9913 | Production PostgreSQL | Public |

---

## 🌳 Git Branching Strategy

### Recommended Branch Structure

**DO NOT create a separate Git repository.** Use a single repository with multiple branches:

```
Repository: spmo-suite (single repo)
├── main (or master) ← Production-ready code
├── staging ← Test server deployment branch
├── develop ← Active development integration
└── feature/* ← Individual feature branches
```

### Deployment Flow

```
Local Development → develop branch → staging branch (Test Server) → main branch (Production)
```

### Branch Workflow

#### Daily Development
```bash
# 1. Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# 2. Develop and commit
git add .
git commit -m "feat: implement new feature"

# 3. Merge to develop
git checkout develop
git merge feature/new-feature
git push origin develop

# 4. When ready for testing, merge to staging
git checkout staging
git merge develop
git push origin staging
# Deploy to test server

# 5. After testing passes, merge to main
git checkout main
git merge staging
git tag -a v2.1.0 -m "Release v2.1.0"
git push origin main --tags
# Deploy to production
```

#### Hotfix Workflow (Emergency Production Fixes)
```bash
# 1. Create hotfix from main
git checkout main
git checkout -b hotfix/critical-bug

# 2. Fix and commit
git add .
git commit -m "fix: critical bug"

# 3. Merge to main
git checkout main
git merge hotfix/critical-bug
git tag -a v2.0.1 -m "Hotfix v2.0.1"
git push origin main --tags

# 4. Backport to develop and staging
git checkout develop
git merge hotfix/critical-bug
git push origin develop

git checkout staging
git merge hotfix/critical-bug
git push origin staging
```

---

## 🌐 Domain Configuration

### ✅ IT-Approved Domain Structure

```
Production Domains:
├── sspmo.up.edu.ph (Hub)
├── gamit-sspmo.up.edu.ph (GAMIT)
├── lipad-sspmo.up.edu.ph (LIPAD)
└── suplay-sspmo.up.edu.ph (SUPLAY)

Development/Test Domains (APPROVED):
├── sspmo-dev.up.edu.ph (Hub)
├── gamit-sspmo-dev.up.edu.ph (GAMIT)
├── lipad-sspmo-dev.up.edu.ph (LIPAD)
└── suplay-sspmo-dev.up.edu.ph (SUPLAY)
```

**Note**: IT provided `-dev` suffix instead of `-staging`. This is acceptable and follows the same naming principles.

### Why Separate Domains Are Required

1. **Environment Isolation**: Prevents confusion between test and production
2. **Security & Access Control**: Different SSL certificates, IP restrictions
3. **Configuration Management**: Environment-specific Django settings
4. **Testing Realism**: Test with real domain names, not IP addresses
5. **Professional Standards**: Industry best practice

---

## 📝 IT Request Template

### Formal Domain Request

```
Subject: Domain Request for SPMO Suite Test/Staging Server

Dear IT Team,

I am requesting domain setup for a new test/staging server for the SPMO Suite 
to enable proper testing before production deployments.

REQUESTED DOMAINS:
1. staging.sspmo.up.edu.ph (SPMO Hub - Test)
2. gamit-staging.sspmo.up.edu.ph (GAMIT - Test)
3. lipad-staging.sspmo.up.edu.ph (LIPAD - Test)
4. suplay-staging.sspmo.up.edu.ph (SUPLAY - Test)

SERVER REQUIREMENTS:
- Operating System: Ubuntu 20.04 LTS or newer
- Docker & Docker Compose support
- Minimum Specs: 4GB RAM, 2 CPU cores, 50GB storage
- Port Access: 80 (HTTP), 443 (HTTPS), 9913 (SSH)
- PostgreSQL 15 (via Docker)

DOMAIN CONFIGURATION:
- SSL Certificate: Required for all domains
- DNS: Point to test server IP (to be provided)

ACCESS RESTRICTIONS (Recommended):
- Restrict access to UP network IPs only
- Or require VPN connection for external access

TIMELINE: [Your preferred timeline]

PURPOSE:
This test server will enable proper quality assurance and user acceptance 
testing before deploying changes to the production environment, reducing 
the risk of production incidents.

Thank you.
```

---

## 🔧 Environment Configuration

### Environment Variables Strategy

Each environment should have its own `.env` file:

```bash
# Local: .env (committed as .env.example, actual .env in .gitignore)
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
SECRET_KEY=local-dev-secret-key
DB_HOST=localhost

# Test: .env.staging (on test server, NOT committed to Git)
DEBUG=True
ALLOWED_HOSTS=staging.sspmo.up.edu.ph,gamit-staging.sspmo.up.edu.ph,...
SECRET_KEY=staging-unique-secret-key
DB_HOST=db
ENVIRONMENT=staging

# Production: .env.production (on production server, NOT committed to Git)
DEBUG=False
ALLOWED_HOSTS=sspmo.up.edu.ph,gamit-sspmo.up.edu.ph,...
SECRET_KEY=production-unique-secret-key
DB_HOST=db
ENVIRONMENT=production
SECURE_SSL_REDIRECT=True
SECURE_COOKIES=True
```

**CRITICAL**: Never commit `.env` files to Git. Use `.env.example` as a template.

---

## 🗄️ Database Strategy

### Database Isolation

- **Local**: SQLite or local PostgreSQL with dummy/development data
- **Test Server**: PostgreSQL with **sanitized copy** of production data (anonymized PII)
- **Production**: PostgreSQL with live data

### Important Rules

1. **Never connect test server to production database**
2. **Anonymize sensitive data** in test database (names, emails, phone numbers)
3. **Regular data refresh**: Copy production data to test monthly (anonymized)
4. **Separate credentials**: Different database passwords for each environment

### Data Sanitization Script (Future)

```python
# scripts/sanitize_test_data.py
# Anonymize PII before copying to test server
# - Replace real names with fake names
# - Replace real emails with test emails
# - Mask phone numbers
# - Remove sensitive documents
```

---

## 🚀 Deployment Workflow

### Local → Test Server Deployment

```bash
# 1. Develop locally on feature branch
git checkout -b feature/new-dashboard
# ... make changes ...
git commit -m "feat: add new dashboard"

# 2. Merge to develop
git checkout develop
git merge feature/new-dashboard
git push origin develop

# 3. Merge to staging
git checkout staging
git merge develop
git push origin staging

# 4. Deploy to test server (SSH into test server)
ssh -p 9913 user@test-server-ip
cd ~/spmo_suite
git pull origin staging
docker-compose down
docker-compose up -d --build
docker-compose exec app_hub python manage.py migrate
docker-compose exec app_hub python manage.py collectstatic --noinput

# 5. Run automated tests
docker-compose exec app_hub python manage.py test

# 6. Notify team for UAT (User Acceptance Testing)
```

### Test Server → Production Deployment

```bash
# 1. After UAT passes on staging
git checkout main
git merge staging
git tag -a v2.1.0 -m "Release v2.1.0: New dashboard feature"
git push origin main --tags

# 2. Create deployment backup on production
ssh -p 9913 ajbasa@172.20.3.91
cd ~/spmo_suite
tar -czf backups/spmo_suite_$(date +%Y%m%d_%H%M%S).tar.gz .
pg_dumpall -U spmo_admin > backups/db_backup_$(date +%Y%m%d_%H%M%S).sql

# 3. Deploy to production
git pull origin main
docker-compose down
docker-compose up -d --build
docker-compose exec app_hub python manage.py migrate
docker-compose exec app_hub python manage.py collectstatic --noinput

# 4. Smoke tests
curl -I https://sspmo.up.edu.ph
curl -I https://gamit-sspmo.up.edu.ph
# ... test critical paths ...

# 5. Monitor for 24-48 hours
docker-compose logs -f --tail=100
```

---

## 🔒 Security Considerations

### Access Control

**Test Server Recommendations:**
- Restrict to UP network IPs only (initially)
- Require VPN for external access
- Use strong SSH keys (disable password authentication)
- Different admin passwords than production

### SSL/TLS

- Request SSL certificates for all staging domains
- Use Let's Encrypt or institutional certificates
- Configure HTTPS redirect in Nginx

### Secrets Management

- Never commit secrets to Git
- Use different `SECRET_KEY` for each environment
- Rotate secrets regularly
- Use environment variables for all sensitive data

---

## ⚠️ What NOT to Do

### ❌ Anti-Patterns to Avoid

1. **Don't create separate Git repositories**
   - Causes code divergence and merge conflicts
   - Duplicate maintenance effort
   - Version control nightmares

2. **Don't share databases between environments**
   - Risk of test data corrupting production
   - Accidental production data deletion
   - Security vulnerabilities

3. **Don't deploy directly from local to production**
   - Always go through staging first
   - No testing = high risk of bugs

4. **Don't use production domains for testing**
   - Confuses users
   - Risk of accidental production changes
   - SSL certificate conflicts

5. **Don't skip the staging branch**
   - Defeats the purpose of having a test server
   - Increases production incident risk

---

## 📊 Implementation Checklist

### Phase 1: Git Repository Setup (Do Now)
- [ ] Standardize production branch name (`main` or `master`)
- [ ] Create `staging` branch from current production state
- [ ] Create `develop` branch from `staging`
- [ ] Update local repository to track all branches
- [ ] Document branch strategy in `README.md`

### Phase 2: IT Request (Pending)
- [ ] Submit formal domain request to IT
- [ ] Request test server provisioning
- [ ] Request SSL certificates for staging domains
- [ ] Clarify access control requirements (VPN/IP restrictions)

### Phase 3: Test Server Configuration (After IT Approval)
- [ ] SSH access to test server
- [ ] Clone repository and checkout `staging` branch
- [ ] Configure `.env.staging` file
- [ ] Set up Docker and Docker Compose
- [ ] Configure Nginx with staging domains
- [ ] Set up PostgreSQL database
- [ ] Import sanitized test data
- [ ] Configure SSL certificates
- [ ] Test all applications

### Phase 4: Deployment Scripts (After Test Server Ready)
- [ ] Create `scripts/deploy_staging.sh`
- [ ] Create `scripts/deploy_production.sh`
- [ ] Create `scripts/sanitize_test_data.py`
- [ ] Create `scripts/run_tests.sh`
- [ ] Document deployment procedures

### Phase 5: Team Training (After Setup Complete)
- [ ] Document deployment workflow
- [ ] Train team on Git branching strategy
- [ ] Establish code review process
- [ ] Define UAT procedures
- [ ] Create deployment checklist

---

## 🎯 Success Criteria

A successful test server implementation will provide:

1. **Risk Reduction**: All changes tested before production
2. **Quality Assurance**: Automated and manual testing in production-like environment
3. **User Acceptance**: Stakeholders can test features before go-live
4. **Rollback Safety**: Easy rollback if issues found in staging
5. **Team Confidence**: Developers confident in deployment process

---

## 📚 Additional Resources

### Related Documentation
- [Production Lock Protocol](../knowledge_base/protocols/production_lock.md)
- [Deployment Synchronization Protocol](../knowledge_base/protocols/deployment_sync.md)
- [Git-Based Deployment Protocol](../GIT_BASED_DEPLOYMENT_PROTOCOL.md)

### External References
- [Git Flow Workflow](https://nvie.com/posts/a-successful-git-branching-model/)
- [The Twelve-Factor App](https://12factor.net/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)

---

## 📝 Notes & Updates

### 2026-02-12
- Initial document created
- IT request pending
- Awaiting test server provisioning and domain approval

---

**Status**: PENDING IT APPROVAL  
**Next Steps**: Wait for IT response, then proceed with Phase 3 implementation

**JARVIS** - Prime Orchestrator  
*"Proper preparation prevents poor performance, sir."*
