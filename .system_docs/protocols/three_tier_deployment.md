# Three-Tier Deployment Protocol
**SPMO Suite - Git-Based Deployment Workflow**  
**Version**: 2.0  
**Effective Date**: 2026-02-12  
**Status**: ACTIVE

---

## 🎯 Purpose

This protocol establishes the deployment workflow for the SPMO Suite across three environments: Local Development, Development/Test Server, and Production Server. It ensures quality, stability, and traceability through Git-based version control.

---

## 🏗️ Environment Architecture

### Three-Tier Structure

```
┌─────────────────────────────────────────────────────────────┐
│  LOCAL DEVELOPMENT                                          │
│  - Developer machines                                       │
│  - Feature branches, develop branch                         │
│  - DEBUG=True, local database                               │
│  - Rapid iteration, no approval required                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
              Git push to staging branch
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  DEV/TEST SERVER (172.20.3.92)                              │
│  - staging branch deployment                                │
│  - sspmo-dev.up.edu.ph domains                              │
│  - DEBUG=True, test database                                │
│  - User Acceptance Testing (UAT)                            │
│  - Quality gate before production                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
         UAT approval + Git merge to main
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  PRODUCTION SERVER (172.20.3.91)                            │
│  - main branch deployment                                   │
│  - sspmo.up.edu.ph domains                                  │
│  - DEBUG=False, production database                         │
│  - Live user traffic                                        │
│  - Strict change control                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🌳 Git Branch Strategy

### Branch Structure

```
main (production)
  ├── Tagged releases: v2.0.0, v2.1.0, etc.
  ├── Protected: Requires UAT approval
  └── Deployed to: Production (172.20.3.91)

staging (test server)
  ├── Integration point for testing
  ├── Protected: Requires PR from develop
  └── Deployed to: Dev Server (172.20.3.92)

develop (integration)
  ├── Active development integration
  ├── Open for feature merges
  └── Not deployed (local testing only)

feature/* (individual work)
  ├── Created from: develop
  ├── Merged to: develop
  └── Naming: feature/description-of-work
```

### Branch Protection Rules

| Branch | Protection Level | Merge Requirements | Who Can Merge |
|:-------|:-----------------|:-------------------|:--------------|
| `main` | 🔴 CRITICAL | UAT approval + tag | User only |
| `staging` | 🟡 PROTECTED | PR from develop | Developer + User |
| `develop` | 🟢 OPEN | Feature complete | Developer |
| `feature/*` | 🟢 OPEN | None | Developer |

---

## 🚀 Deployment Workflows

### Workflow 1: Feature Development (Local → Dev Server)

**Objective**: Deploy new feature to dev server for testing

```bash
# 1. Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/new-dashboard

# 2. Develop locally
# ... make changes, test locally ...
git add .
git commit -m "feat(hub): add new dashboard with analytics"

# 3. Merge to develop
git checkout develop
git merge feature/new-dashboard
git push origin develop

# 4. Merge to staging when ready for UAT
git checkout staging
git pull origin staging
git merge develop
git push origin staging

# 5. Deploy to dev server
ssh -p 9913 ajbasa@172.20.3.92
cd ~/spmo_suite
git pull origin staging
docker-compose restart

# Or use automated script:
./scripts/deploy_dev.sh

# 6. Notify team for UAT
# Post in team channel: "Feature X deployed to dev server for testing"
```

**Approval Gate**: None (automatic deployment to dev)

---

### Workflow 2: Production Deployment (Dev Server → Production)

**Objective**: Promote tested changes from dev to production

**Prerequisites**:
- ✅ All features tested on dev server
- ✅ UAT approval received
- ✅ No critical bugs reported
- ✅ Database migrations reviewed

```bash
# 1. Merge staging to main
git checkout main
git pull origin main
git merge staging

# 2. Tag the release
git tag -a v2.1.0 -m "Release v2.1.0: New dashboard and bug fixes"
git push origin main --tags

# 3. Create production backup
ssh -p 9913 ajbasa@172.20.3.91
cd ~/spmo_suite
tar -czf backups/spmo_suite_$(date +%Y%m%d_%H%M%S).tar.gz .
pg_dumpall -U spmo_admin > backups/db_backup_$(date +%Y%m%d_%H%M%S).sql

# 4. Deploy to production
git pull origin main
docker-compose down
docker-compose up -d --build

# 5. Run migrations (if any)
docker-compose exec app_hub python manage.py migrate
docker-compose exec app_gamit python manage.py migrate
docker-compose exec app_gfa python manage.py migrate
docker-compose exec app_store python manage.py migrate

# 6. Collect static files
docker-compose exec app_hub python manage.py collectstatic --noinput

# 7. Smoke tests
curl -I https://sspmo.up.edu.ph
curl -I https://gamit-sspmo.up.edu.ph
curl -I https://lipad-sspmo.up.edu.ph
curl -I https://suplay-sspmo.up.edu.ph

# 8. Monitor logs for 30 minutes
docker-compose logs -f --tail=100
```

**Approval Gate**: 🔴 **USER APPROVAL REQUIRED**

**Approval Criteria**:
- UAT completed successfully on dev server
- No critical bugs reported
- Database migrations reviewed and safe
- Rollback plan documented

---

### Workflow 3: Hotfix (Emergency Production Fix)

**Objective**: Deploy critical fix directly to production, bypassing dev server

**Use Only For**:
- Security vulnerabilities
- Data corruption issues
- Service outages
- Critical bugs affecting all users

```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-security-fix

# 2. Implement fix
# ... make minimal changes ...
git add .
git commit -m "fix(security): patch XSS vulnerability in forms"

# 3. Merge to main
git checkout main
git merge hotfix/critical-security-fix
git tag -a v2.0.1 -m "Hotfix v2.0.1: Security patch"
git push origin main --tags

# 4. Deploy to production (follow Workflow 2 steps 3-8)

# 5. Backport to staging and develop
git checkout staging
git merge hotfix/critical-security-fix
git push origin staging

git checkout develop
git merge hotfix/critical-security-fix
git push origin develop

# 6. Deploy to dev server to maintain parity
ssh -p 9913 ajbasa@172.20.3.92
cd ~/spmo_suite
git pull origin staging
docker-compose restart
```

**Approval Gate**: 🔴 **USER APPROVAL REQUIRED** (but expedited)

**Post-Deployment**: Document incident and fix in `docs/incidents/`

---

## 🧪 Testing Requirements

### Local Development
- ✅ Code runs without errors
- ✅ Manual testing of changed functionality
- ✅ No hardcoded credentials or secrets

### Dev Server (Before Production)
- ✅ All automated tests pass (if available)
- ✅ Manual UAT by stakeholders
- ✅ Cross-browser testing (Chrome, Firefox, Edge)
- ✅ Mobile responsiveness verified
- ✅ No console errors in browser
- ✅ Database migrations tested

### Production (After Deployment)
- ✅ Smoke tests (all apps accessible)
- ✅ Critical user flows verified
- ✅ Monitor logs for 30 minutes
- ✅ Monitor for 24-48 hours

---

## 🔒 Environment-Specific Lock Rules

### Local Development
- **Lock Level**: 🟢 OPEN
- **Restrictions**: None
- **Rationale**: Rapid iteration required

### Dev Server
- **Tier 1 (CAUTION)**: `.env`, `docker-compose.yml`, `nginx/conf.d/default.conf`
  - Rule: SysOps notification (not blocking)
  - Rationale: Track infrastructure changes
  
- **Tier 2 (OPEN)**: `settings.py`, all application code
  - Rule: Standard workflow
  - Rationale: Testing environment, permissive

### Production Server
- **Tier 1 (CRITICAL)**: `.env`, `docker-compose.yml`, `nginx/conf.d/default.conf`
  - Rule: User approval + SysOps oversight REQUIRED
  - Rationale: Prevent service disruption
  
- **Tier 2 (PROTECTED)**: `settings.py` security sections
  - Rule: Security Shield proposal + User approval
  - Rationale: Security implications

- **Tier 3 (OPEN)**: Templates, static files, views, models
  - Rule: Standard workflow (via staging)
  - Rationale: Low risk, tested on dev

---

## 🔄 Rollback Procedures

### Dev Server Rollback

```bash
# If dev deployment fails, rollback to previous commit
ssh -p 9913 ajbasa@172.20.3.92
cd ~/spmo_suite
git log --oneline -5  # Find previous commit
git checkout <previous-commit-hash>
docker-compose restart
```

**Impact**: Low (only affects testing)

### Production Rollback

```bash
# If production deployment fails, rollback to previous tag
ssh -p 9913 ajbasa@172.20.3.91
cd ~/spmo_suite

# Option 1: Git rollback
git tag  # List tags
git checkout v2.0.0  # Previous stable version
docker-compose down
docker-compose up -d --build

# Option 2: Archive restore (if Git rollback insufficient)
cd ~/spmo_suite
docker-compose down
rm -rf ./*
tar -xzf backups/spmo_suite_YYYYMMDD_HHMMSS.tar.gz
docker-compose up -d

# Option 3: Database restore (if data corruption)
psql -U spmo_admin < backups/db_backup_YYYYMMDD_HHMMSS.sql
```

**Impact**: High (affects live users)  
**Approval**: User approval required  
**Communication**: Notify users of rollback

---

## 📋 Pre-Deployment Checklists

### Dev Server Deployment Checklist

- [ ] Feature branch merged to develop
- [ ] Develop merged to staging
- [ ] Local testing completed
- [ ] No merge conflicts
- [ ] Commit messages follow standards
- [ ] No hardcoded secrets

### Production Deployment Checklist

- [ ] UAT completed on dev server
- [ ] UAT approval received
- [ ] No critical bugs reported
- [ ] Database migrations reviewed
- [ ] Rollback plan documented
- [ ] Production backup created
- [ ] Team notified of deployment window
- [ ] User approval obtained

---

## 🎯 Approval Gates

### Gate 1: Dev Server Deployment
- **Approver**: Developer (self-approval)
- **Criteria**: Feature complete, local testing passed
- **Blocking**: No

### Gate 2: Production Deployment
- **Approver**: User (ajbasa)
- **Criteria**: UAT passed, no critical bugs, backup created
- **Blocking**: Yes (deployment cannot proceed without approval)

### Gate 3: Hotfix Deployment
- **Approver**: User (ajbasa)
- **Criteria**: Critical issue, minimal changes, tested locally
- **Blocking**: Yes (but expedited process)

---

## 📊 Environment Comparison

| Aspect | Local | Dev Server | Production |
|:-------|:------|:-----------|:-----------|
| **Branch** | feature/*, develop | staging | main |
| **Domain** | localhost | sspmo-dev.up.edu.ph | sspmo.up.edu.ph |
| **DEBUG** | True | True | False |
| **Database** | Local/SQLite | Test PostgreSQL | Production PostgreSQL |
| **SSL** | No | Yes (recommended) | Yes (required) |
| **Approval** | None | None | User required |
| **Backup** | Optional | Optional | Mandatory |
| **Monitoring** | None | Optional | Mandatory |

---

## 🔐 Security Standards

### Secret Management

- **Local**: `.env` (gitignored, example in `.env.example`)
- **Dev Server**: `.env` (unique SECRET_KEY, not committed)
- **Production**: `.env` (unique SECRET_KEY, not committed)

**Rule**: Each environment MUST have a unique `SECRET_KEY`

### Database Access

- **Local**: Full access
- **Dev Server**: Full access (test data only)
- **Production**: Restricted access, backup-only exposure

### Domain Standards

- **Production**: `*-sspmo.up.edu.ph` (hyphenated)
- **Dev**: `*-sspmo-dev.up.edu.ph` (hyphenated + dev suffix)

---

## 📈 Monitoring & Logging

### Dev Server
- **Logging**: DEBUG level
- **Monitoring**: Optional
- **Alerts**: None

### Production
- **Logging**: INFO level (ERROR for sensitive operations)
- **Monitoring**: Mandatory (24-48 hours post-deployment)
- **Alerts**: Critical errors, service outages

---

## 🆘 Incident Response

### Severity Levels

| Level | Description | Response Time | Workflow |
|:------|:------------|:--------------|:---------|
| **P0** | Service outage | Immediate | Hotfix workflow |
| **P1** | Critical bug affecting all users | < 4 hours | Hotfix workflow |
| **P2** | Major bug affecting some users | < 24 hours | Standard workflow |
| **P3** | Minor bug, cosmetic issue | Next release | Standard workflow |

### Escalation Path

1. Developer identifies issue
2. Assess severity (P0-P3)
3. If P0/P1: Notify user immediately, initiate hotfix
4. If P2/P3: Document in issue tracker, schedule for next release

---

## 📝 Documentation Requirements

### Per Deployment

- **Changelog**: Update `CHANGELOG.md` with changes
- **Tag Message**: Descriptive tag message with version number
- **Deployment Log**: Record in `logs/DEPLOYMENT_LOG_YYYY_MM_DD.md`

### Per Incident

- **Incident Report**: Document in `docs/incidents/YYYY-MM-DD_description.md`
- **Root Cause Analysis**: Include in incident report
- **Prevention Measures**: Document lessons learned

---

## ✅ Success Metrics

- **Dev Server Uptime**: > 95% (testing environment, downtime acceptable)
- **Production Uptime**: > 99.9% (critical)
- **Failed Deployments**: < 5% (rollback rate)
- **Hotfix Frequency**: < 1 per month (indicates quality issues)
- **UAT Pass Rate**: > 90% (first-time pass)

---

## 🔄 Protocol Review

This protocol should be reviewed and updated:
- After every major incident
- Quarterly (every 3 months)
- When infrastructure changes significantly

**Next Review**: 2026-05-12

---

## 📚 Related Protocols

- [Production Lock Protocol](../knowledge_base/protocols/production_lock.md)
- [Version Control Protocol](../knowledge_base/protocols/version_control.md)
- [Agent Decision-Making Protocol](../knowledge_base/protocols/agent_decision_delegation.md)

---

**Version History**:
- v2.0 (2026-02-12): Added three-tier deployment workflow
- v1.0 (2026-01-15): Initial two-tier protocol

**Approved By**: User (ajbasa)  
**Effective Date**: 2026-02-12
