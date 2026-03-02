# 🔒 Production Lock Protocol
**Version**: 1.0.0  
**Effective Date**: January 23, 2026  
**Status**: ENFORCED

---

## 🎯 PURPOSE

This document establishes **immutable configuration standards** for the SPMO Suite production server (172.20.3.91) to prevent service disruption from unauthorized or accidental configuration changes.

---

## 🚨 CRITICAL - PRODUCTION-LOCKED FILES

The following files are **LOCKED** and must NOT be modified without explicit user approval:

### Tier 1: System Infrastructure (DO NOT TOUCH)
These files control server-wide routing and deployment:

| File | Purpose | Lock Level |
|------|---------|------------|
| `.env` | Environment variables, ALLOWED_HOSTS | 🔴 CRITICAL |
| `docker-compose.yml` | Container orchestration | 🔴 CRITICAL |
| `nginx/conf.d/default.conf` | Domain routing (Cloudflare) | 🔴 CRITICAL |

**Modification Rule**: Requires explicit user approval + SysOps Sentinel oversight

---

### Tier 2: Application Security Settings
These settings control domain access and CSRF protection:

| File | Purpose | Lock Level |
|------|---------|------------|
| `spmo_website/config/settings.py` | Hub CSRF_TRUSTED_ORIGINS | 🟠 PROTECTED |
| `gamit_app/gamit_core/settings.py` | GAMIT CSRF_TRUSTED_ORIGINS | 🟠 PROTECTED |
| `gfa_app/config/settings.py` | LIPAD CSRF_TRUSTED_ORIGINS | 🟠 PROTECTED |
| `suplay_app/office_supplies_project/settings.py` | SUPLAY CSRF_TRUSTED_ORIGINS | 🟠 PROTECTED |

**Modification Rule**: Only Security Shield can propose changes, requires user approval

---

## ⚙️ PRODUCTION CONFIGURATION STANDARDS

### Current Production Values (LOCKED)

#### Domain Configuration
```bash
# .env - ALLOWED_HOSTS (DO NOT MODIFY)
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,172.20.3.91,spmo.up.edu.ph,.spmo.up.edu.ph,sspmo.up.edu.ph,.sspmo.up.edu.ph,gamit-sspmo.up.edu.ph,suplay-sspmo.up.edu.ph,lipad-sspmo.up.edu.ph
```

#### CSRF Trusted Origins (HYPHENATED FORMAT REQUIRED)
```python
# ALL APPS - Use hyphenated format (DO NOT MODIFY)
CSRF_TRUSTED_ORIGINS = [
    'https://gamit-sspmo.up.edu.ph',  # ✅ CORRECT
    'http://gamit-sspmo.up.edu.ph',   # ✅ CORRECT
    # ...
]

# ❌ WRONG FORMAT - DO NOT USE:
# 'https://gamit.sspmo.up.edu.ph'  # Missing hyphen!
```

---

## 🛡️ AGENT RESPONSIBILITIES & BOUNDARIES

### SysOps Sentinel
**Authority**: EXCLUSIVE control over Tier 1 files  
**Restrictions**: 
- Must log all Tier 1 changes in `log-sysops.md`
- Requires user approval before modifying production
- Must verify container health after any change

### Security Shield
**Authority**: Can PROPOSE changes to Tier 2 files  
**Restrictions**:
- Must flag conflicts with production lock
- Requires user approval for CSRF/domain changes
- Must coordinate with SysOps for deployment

### Frontend Architect
**Authority**: Templates, static files, UI/UX  
**Restrictions**:
- ❌ FORBIDDEN: Cannot modify settings.py files
- ❌ FORBIDDEN: Cannot modify nginx config
- Safe zone: `templates/`, `static/`, CSS only

### Data Weaver
**Authority**: Database operations, data migrations  
**Restrictions**:
- ❌ FORBIDDEN: Cannot modify ALLOWED_HOSTS or CSRF settings
- Safe zone: Models, migrations, data scripts

### Logic Specialists (GAMIT/SUPLAY/LIPAD)
**Authority**: App-specific views, models, business logic  
**Restrictions**:
- ❌ FORBIDDEN: Cannot modify CSRF_TRUSTED_ORIGINS
- ❌ FORBIDDEN: Cannot modify ALLOWED_HOSTS
- Safe zone: views.py, models.py, urls.py (non-security)

### Vault Guardian
**Authority**: Git operations, backups  
**Restrictions**:
- Must verify production lock compliance before commits
- Must flag any Tier 1/2 file changes in commit messages

---

## 🚨 VIOLATION PROTOCOL

If any agent attempts to modify locked files:

### Detection
```markdown
⚠️ PRODUCTION LOCK VIOLATION DETECTED
Agent: [Agent Name]
File: [Locked File Path]
Action: [Proposed Change]
Lock Level: [CRITICAL/PROTECTED]
```

### Escalation
1. **IMMEDIATE HALT** - Stop the modification
2. **FLAG TO JARVIS** - Report violation
3. **ESCALATE TO USER** - Request explicit approval
4. **LOG VIOLATION** - Document in agent's log file

---

## ✅ PRE-DEPLOYMENT CHECKLIST

Before deploying ANY changes to production:

### SysOps Sentinel Verification
- [ ] Verify `.env` has correct hyphenated domains
- [ ] Verify nginx config uses correct server_name directives
- [ ] Verify all 4 apps have hyphenated CSRF_TRUSTED_ORIGINS
- [ ] Test domain routing with browser agent
- [ ] Verify all 6 containers running (`docker ps`)

### Production Health Check
```bash
# Run on remote server
ssh -p 9913 ajbasa@172.20.3.91 << 'EOF'
echo "=== Container Status ==="
docker ps --format "table {{.Names}}\t{{.Status}}"

echo ""
echo "=== Domain Verification ==="
for domain in sspmo.up.edu.ph gamit-sspmo.up.edu.ph suplay-sspmo.up.edu.ph lipad-sspmo.up.edu.ph; do
  echo -n "$domain: "
  curl -s -o /dev/null -w "%{http_code}" http://$domain
  echo ""
done
EOF
```

Expected Output:
```
Container Status:
spmo_gateway     Up XX minutes
app_hub          Up XX minutes
app_gamit        Up XX minutes
app_gfa          Up XX minutes
app_store        Up XX minutes
spmo_shared_db   Up XX minutes

Domain Verification:
sspmo.up.edu.ph: 200
gamit-sspmo.up.edu.ph: 200
suplay-sspmo.up.edu.ph: 200
lipad-sspmo.up.edu.ph: 200
```

---

## 📊 MONITORING & ALERTS

### Continuous Monitoring (SysOps Sentinel)
- Monitor container uptime every session
- Verify domain accessibility before major changes
- Check for unauthorized configuration drift

### Alert Conditions
1. **Container Down** - Any of the 6 containers stopped
2. **Domain Inaccessible** - HTTP errors on public domains
3. **Config Drift** - Production files differ from locked standards

---

## 🔄 CHANGE MANAGEMENT

### Approved Change Process
1. **User Approval** - Explicit directive only
2. **SysOps Planning** - Document change plan
3. **Backup First** - Create rollback point
4. **Deploy & Test** - Apply change, verify health
5. **Document** - Log in `log-sysops.md`

### Emergency Rollback
```bash
# If production breaks, immediate rollback:
ssh -p 9913 ajbasa@172.20.3.91 "cd spmo_suite && docker compose down && docker compose up -d"
```

---

## 📝 CHANGE LOG

| Date | Agent | Change | Approval | Status |
|------|-------|--------|----------|--------|
| 2026-01-23 | SysOps Sentinel | Fixed hyphenated domains | User Approved | ✅ Success |
| Future | - | - | - | - |

---

## 🎯 SUCCESS CRITERIA

Production is considered **LOCKED and STABLE** when:
- ✅ All 6 containers running continuously
- ✅ All 4 public domains accessible (200 OK)
- ✅ No unauthorized configuration changes
- ✅ Agents respect file lock boundaries
- ✅ All changes logged and approved

---

**Last Updated**: 2026-01-23 @ 14:27 PHT  
**Maintained By**: SysOps Sentinel  
**Enforcement**: JARVIS Prime Orchestrator
