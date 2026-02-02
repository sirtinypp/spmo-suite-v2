# SPMO Suite - Version Control & Monitoring Protocol

**Effective Date:** January 21, 2026  
**Version:** 1.0.0 Baseline  
**Status:** ACTIVE - STRICT ENFORCEMENT

---

## 🔒 Version Control Policy

### Git Workflow - MANDATORY

#### 1. Current Baseline (v1.0.0)
All changes from this point forward MUST be tracked in Git with proper commits and tags.

#### 2. Branching Strategy
```
main (protected) - Production-ready code only
├── develop - Integration branch for features
├── feature/* - New features
├── bugfix/* - Bug fixes
└── hotfix/* - Emergency production fixes
```

#### 3. Commit Message Format - REQUIRED
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding tests
- `chore`: Maintenance tasks

**Example:**
```
fix(lipad): resolve CSRF token validation error

Updated CSRF_TRUSTED_ORIGINS to include localhost
addresses for development environment.

Fixes #123
```

#### 4. Version Tagging - STRICT
- **Major** (X.0.0): Breaking changes, major features
- **Minor** (x.X.0): New features, backwards compatible
- **Patch** (x.x.X): Bug fixes only

**Tag format:** `vX.Y.Z`
**Tag command:**
```bash
git tag -a v1.0.1 -m "Bugfix release: CSRF configuration"
git push origin --tags
```

---

## 📊 Monitoring System

### 1. Application Health Checks

#### Daily Checks (Automated)
- [ ] All containers running
- [ ] Database connectivity
- [ ] Disk space > 20% free
- [ ] Memory usage < 80%
- [ ] No critical errors in logs

#### Weekly Checks (Manual)
- [ ] Application response times
- [ ] Database backup verification
- [ ] Security updates available
- [ ] Log review for anomalies
- [ ] User access audit

### 2. Log Management

#### Log Locations
```
logs/
├── nginx/
│   ├── access.log
│   └── error.log
├── spmo_hub/
│   └── django.log
├── gamit/
│   └── django.log
├── lipad/
│   └── django.log
├── suplay/
│   └── django.log
└── database/
    └── postgresql.log
```

#### Log Retention Policy
- **Access logs**: 30 days
- **Error logs**: 90 days
- **Database logs**: 60 days
- **Rotate**: Weekly

#### Log Monitoring Commands
```bash
# Check all container logs
docker logs app_hub --tail 100
docker logs app_gamit --tail 100
docker logs app_gfa --tail 100
docker logs app_store --tail 100

# Check for errors
docker logs app_hub 2>&1 | grep -i error | tail -20
```

### 3. Performance Monitoring

#### Metrics to Track
| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| CPU Load | < 0.5 | > 1.0 | > 2.0 |
| Memory Usage | < 50% | > 70% | > 85% |
| Disk Usage | < 60% | > 75% | > 85% |
| Response Time | < 500ms | > 1s | > 2s |

#### Monitoring Commands
```bash
# Server resources
ssh -p 9913 ajbasa@172.20.3.91 "uptime; free -h; df -h"

# Docker stats
ssh -p 9913 ajbasa@172.20.3.91 "docker stats --no-stream"

# Application health
curl -I http://172.20.3.91:8000
curl -I http://172.20.3.91:8001
curl -I http://172.20.3.91:8002
curl -I http://172.20.3.91:8003
```

---

## 📋 Change Management Procedure

### For ALL Changes - NO EXCEPTIONS

#### 1. Before Making Changes
- [ ] Create feature/bugfix branch
- [ ] Document the change purpose
- [ ] Test locally first
- [ ] Review impact on other apps

#### 2. Testing Requirements
- [ ] Local environment tested
- [ ] No errors in logs
- [ ] All existing features still work
- [ ] Database migrations tested
- [ ] Docker containers rebuild successfully

#### 3. Deployment Checklist
- [ ] Changes committed with proper message
- [ ] Local tests passed
- [ ] Remote backup created
- [ ] Deployment window scheduled
- [ ] Rollback plan documented

#### 4. Post-Deployment
- [ ] Verify all containers running
- [ ] Check application logs
- [ ] Test critical functionality
- [ ] Monitor for 30 minutes
- [ ] Update CHANGELOG.md
- [ ] Update version if needed

---

## 🚨 Emergency Response Protocol

### Critical Issues (Production Down)
1. **Assess**: Check container status immediately
2. **Notify**: Document the issue
3. **Rollback**: Revert to last known good state
4. **Fix**: Debug in isolated environment
5. **Deploy**: Apply fix with testing
6. **Document**: Update incident log

### Rollback Procedure
```bash
# Stop containers
docker compose down

# Restore from backup (if database affected)
docker exec spmo_shared_db psql -U spmo_admin -d postgres < backup.sql

# Revert code changes
git reset --hard v1.0.0  # or last known good tag

# Restart containers
docker compose up -d

# Verify
docker ps
curl -I http://172.20.3.91:8000
```

---

## 📁 File Change Tracking

### Protected Files - Review Required
Changes tothe following require extra scrutiny:
- `docker-compose.yml`
- `nginx/conf.d/default.conf`
- `.env`
- `*/settings.py` (any application)
- `*/urls.py` (any application)
- Database migration files

### Backup Before Modifying
```bash
# Before changing critical files
cp <file> <file>.backup.$(date +%Y%m%d)
```

---

## 🗃️ Backup Strategy

### Database Backups - DAILY
```bash
# Production database backup
ssh -p 9913 ajbasa@172.20.3.91 "docker exec spmo_shared_db \
  pg_dumpall -U spmo_admin > /home/ajbasa/backups/db_$(date +%Y%m%d).sql"
```

### Code Backups - WEEKLY
```bash
# Archive current codebase
ssh -p 9913 ajbasa@172.20.3.91 "cd /home/ajbasa && \
  tar -czf backups/spmo_suite_$(date +%Y%m%d).tar.gz spmo_suite/"
```

### Retention
- Daily backups: Keep 7 days
- Weekly backups: Keep 4 weeks
- Monthly backups: Keep 3 months
- Version releases: Keep indefinitely

---

## 📊 Status Reporting

### Daily Status Check (Run Every Morning)
```bash
#!/bin/bash
# save as: check_status.sh

echo "=== SPMO Suite Status $(date) ==="
echo ""
echo "Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}"
echo ""
echo "Resource Usage:"
free -h | grep Mem
df -h / | tail -1
echo ""
echo "Recent Errors:"
docker logs app_hub 2>&1 | grep -i error | tail -5
echo "=== End of Status Report ==="
```

### Weekly Status Report Template
```markdown
## Week of [DATE]

### System Health: [GREEN/YELLOW/RED]
- Uptime: [X] days
- CPU: [X]%
- Memory: [X]%
- Disk: [X]%

### Issues Encountered:
- [Issue 1]
- [Issue 2]

### Changes Made:
- [Change 1]
- [Change 2]

### Planned for Next Week:
- [Plan 1]
- [Plan 2]
```

---

## 🔐 Security Monitoring

### Weekly Security Checks
- [ ] Review user access logs
- [ ] Check for unauthorized access attempts
- [ ] Verify SSL certificates (when implemented)
- [ ] Update system packages
- [ ] Review firewall rules

### Security Incident Response
1. Isolate affected system
2. Assess damage
3. Preserve evidence
4. Notify stakeholders
5. Remediate
6. Document and review

---

## 📝 Documentation Requirements

### Every Change Must Include:
1. **What** changed
2. **Why** it changed
3. **How** to test it
4. **Rollback** procedure
5. **Impact** assessment

### Update These Files:
- `CHANGELOG.md` - For all changes
- `README.md` - If setup/deployment changes
- `docs/` - For new features or procedures

---

## ✅ Compliance Checklist

### Before ANY Production Deployment:
- [ ] Code reviewed
- [ ] Tests passed locally
- [ ] Backup created
- [ ] Change documented in CHANGELOG
- [ ] Git commit with proper message
- [ ] Deployment window scheduled
- [ ] Rollback plan ready
- [ ] Monitoring enabled
- [ ] Post-deployment verification plan

---

## 🎯 Version 1.0.0 Baseline

### Current State (LOCKED)
- **Applications**: All 4 working
- **Configuration**: Stable
- **Database**: Migrated and operational
- **Git Commit**: [Will be created]
- **Git Tag**: v1.0.0

### Any Changes from This Point:
1. MUST go through version control
2. MUST be documented
3. MUST be tested
4. MUST have rollback plan
5. MUST update version number

---

## 📞 Emergency Contacts

### System Administrator
- Name: ajbasa
- Server: 172.20.3.91:9913

### Escalation Path
1. Check logs
2. Attempt rollback
3. Contact administrator
4. Document incident

---

## 📖 Quick Reference

### Most Common Commands
```bash
# Check status
docker ps
docker stats --no-stream

# View logs
docker logs <container> --tail 50

# Restart container
docker restart <container>

# Backup database
docker exec spmo_shared_db pg_dumpall -U spmo_admin > backup.sql

# Check version
cat VERSION
```

---

**This protocol is MANDATORY starting v1.0.0.**  
**All team members must comply. No exceptions.**

**Last Updated:** January 21, 2026  
**Next Review:** February 21, 2026
