# Deployment Synchronization Protocol
**Version:** 1.0.0  
**Last Updated:** January 21, 2026

## 🎯 Purpose
Ensure all local changes are properly synchronized to the production server (172.20.3.91) with zero discrepancies.

---

## 📋 Pre-Deployment Checklist

### Local Environment
- [ ] All changes committed to Git
- [ ] Git status shows clean working directory
- [ ] Version number updated (if needed)
- [ ] CHANGELOG.md updated
- [ ] Local tests passed
- [ ] Health check runs successfully

### Production Server
- [ ] Database backup created
- [ ] Current deployment archived
- [ ] Sufficient disk space available
- [ ] No active users (if breaking changes)

---

## 🔄 Synchronization Steps

### 1. Verify Git Status
```bash
cd "c:\Users\Aaron\spmo-suite - Copy"
git status
git log --oneline -5
```

### 2. Critical Files to Sync
These files MUST be synchronized to production:

#### Configuration Files
- `docker-compose.yml` ⚠️ Critical
- `.env` ⚠️ Critical
- `VERSION` ✅ Required
- `CHANGELOG.md` ✅ Required

#### Nginx Configuration
- `nginx/conf.d/default.conf` ⚠️ Critical

#### Application Settings
- `spmo_website/config/settings.py`
- `gamit_app/config/settings.py`
- `gfa_app/config/settings.py`
- `suplay_app/office_supplies_project/settings.py`

#### Documentation
- `README.md`
- `docs/VERSION_CONTROL_PROTOCOL.md`

### 3. Deployment Command Sequence

```powershell
# Step 1: Upload changed files
scp -P 9913 "c:\Users\Aaron\spmo-suite - Copy\VERSION" ajbasa@172.20.3.91:/home/ajbasa/spmo_suite/
scp -P 9913 "c:\Users\Aaron\spmo-suite - Copy\CHANGELOG.md" ajbasa@172.20.3.91:/home/ajbasa/spmo_suite/
scp -P 9913 "c:\Users\Aaron\spmo-suite - Copy\nginx\conf.d\default.conf" ajbasa@172.20.3.91:/home/ajbasa/spmo_suite/nginx/conf.d/

# Step 2: Upload application changes (if any)
# Only upload specific changed files, not entire directories
scp -P 9913 "c:\Users\Aaron\spmo-suite - Copy\gfa_app\config\settings.py" ajbasa@172.20.3.91:/home/ajbasa/spmo_suite/gfa_app/config/

# Step 3: Restart affected containers
ssh -p 9913 ajbasa@172.20.3.91 "cd spmo_suite && docker restart spmo_gateway"
ssh -p 9913 ajbasa@172.20.3.91 "cd spmo_suite && docker restart app_gfa"

# Step 4: Verify containers restarted
ssh -p 9913 ajbasa@172.20.3.91 "docker ps"
```

### 4. Verification Steps

```bash
# Check nginx config is valid
ssh -p 9913 ajbasa@172.20.3.91 "docker exec spmo_gateway nginx -t"

# Test applications respond
ssh -p 9913 ajbasa@172.20.3.91 "curl -I http://localhost:8000"
ssh -p 9913 ajbasa@172.20.3.91 "curl -I http://localhost:8001"
ssh -p 9913 ajbasa@172.20.3.91 "curl -I http://localhost:8002"
ssh -p 9913 ajbasa@172.20.3.91 "curl -I http://localhost:8003"

# Check for errors in logs
ssh -p 9913 ajbasa@172.20.3.91 "docker logs app_hub --tail 20"
```

---

## 📊 Synchronization Matrix

| File/Directory | Local | Remote | Sync Method | Priority |
|----------------|-------|--------|-------------|----------|
| VERSION | ✅ | ✅ | SCP | Critical |
| CHANGELOG.md | ✅ | ✅ | SCP | Critical |
| nginx/conf.d/default.conf | ✅ | ✅ | SCP | Critical |
| gfa_app/config/settings.py | ✅ | ✅ | SCP | Critical |
| scripts/*.ps1 | ✅ | ❌ | N/A (local only) | N/A |
| docs/*.md | ✅ | ⚠️ | SCP (optional) | Low |

---

## 🚨 Critical Changes Requiring Special Handling

### Database Changes (Migrations)
```bash
# 1. Backup first
ssh -p 9913 ajbasa@172.20.3.91 "docker exec spmo_shared_db pg_dumpall -U spmo_admin > ~/backups/pre_migration_$(date +%Y%m%d).sql"

# 2. Run migration
ssh -p 9913 ajbasa@172.20.3.91 "docker exec app_hub python manage.py migrate"

# 3. Verify
ssh -p 9913 ajbasa@172.20.3.91 "docker exec app_hub python manage.py showmigrations"
```

### Docker Compose Changes
```bash
# 1. Stop containers
ssh -p 9913 ajbasa@172.20.3.91 "cd spmo_suite && docker compose down"

# 2. Upload new docker-compose.yml
scp -P 9913 docker-compose.yml ajbasa@172.20.3.91:/home/ajbasa/spmo_suite/

# 3. Rebuild and restart
ssh -p 9913 ajbasa@172.20.3.91 "cd spmo_suite && docker compose up -d --build"
```

### Environment Variable Changes (.env)
```bash
# 1. Backup current .env
ssh -p 9913 ajbasa@172.20.3.91 "cp spmo_suite/.env spmo_suite/.env.bak.$(date +%Y%m%d)"

# 2. Upload new .env
scp -P 9913 .env ajbasa@172.20.3.91:/home/ajbasa/spmo_suite/

# 3. Restart all containers
ssh -p 9913 ajbasa@172.20.3.91 "cd spmo_suite && docker compose restart"
```

---

## 🔍 Post-Deployment Verification

### Automated Checks
```bash
# Run on remote server
ssh -p 9913 ajbasa@172.20.3.91 << 'EOF'
echo "=== Deployment Verification ==="
echo "1. Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}"

echo ""
echo "2. Application Health:"
for port in 8000 8001 8002 8003; do
  status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port)
  echo "  Port $port: $status"
done

echo ""
echo "3. Nginx Config:"
docker exec spmo_gateway nginx -t

echo ""
echo "4. Recent Errors:"
docker logs app_hub --since 5m 2>&1 | grep -i error | wc -l

echo "=== Verification Complete ==="
EOF
```

### Manual Verification
1. Open browser to http://172.20.3.91
2. Test each application:
   - SPMO Hub: http://172.20.3.91:8000
   - GAMIT: http://172.20.3.91:8001
   - LIPAD: http://172.20.3.91:8002
   - SUPLAY: http://172.20.3.91:8003
3. Verify login works
4. Check admin panel access

---

## 📝 Deployment Log Template

```markdown
## Deployment - [DATE]

### Version: [X.Y.Z]

### Changes Deployed:
- [ ] File 1
- [ ] File 2
- [ ] File 3

### Containers Restarted:
- [ ] app_hub
- [ ] app_gamit
- [ ] app_gfa
- [ ] app_store
- [ ] spmo_gateway

### Verification:
- [ ] All containers running
- [ ] All applications respond
- [ ] No errors in logs
- [ ] Manual testing passed

### Rollback Plan (if needed):
```bash
# Restore from backup
```

### Deployed By: [NAME]
### Deployment Time: [TIME]
### Status: ✅ SUCCESS / ❌ FAILED
```

---

## 🔄 Quick Sync Command

For minor changes (config files only):

```bash
# Save as: quick_deploy.ps1
$files = @(
    "VERSION",
    "CHANGELOG.md",
    "nginx/conf.d/default.conf"
)

foreach ($file in $files) {
    Write-Host "Uploading $file..."
    scp -P 9913 "c:\Users\Aaron\spmo-suite - Copy\$file" "ajbasa@172.20.3.91:/home/ajbasa/spmo_suite/$file"
}

Write-Host "Restarting nginx..."
ssh -p 9913 ajbasa@172.20.3.91 "docker restart spmo_gateway"

Write-Host "Done!"
```

---

## ⚠️ Common Pitfalls to Avoid

1. **Forgetting to backup** before deployment
2. **Not testing locally** before deploying
3. **Deploying without committing** to Git first
4. **Not verifying** containers restarted successfully
5. **Skipping changelog** updates
6. **Direct edits on server** (always edit locally, then deploy)

---

## 📞 Rollback Procedure

If deployment fails:

```bash
# 1. Stop failed containers
ssh -p 9913 ajbasa@172.20.3.91 "cd spmo_suite && docker compose down"

# 2. Restore from archive
ssh -p 9913 ajbasa@172.20.3.91 "cd ~ && tar -xzf archive/spmo_suite_[BACKUP_DATE].tar.gz"

# 3. Restart with previous version
ssh -p 9913 ajbasa@172.20.3.91 "cd spmo_suite && docker compose up -d"

# 4. Verify
ssh -p 9913 ajbasa@172.20.3.91 "docker ps"
```

---

## ✅ Best Practices

1. **Always commit locally first** before deploying
2. **Update VERSION and CHANGELOG** for every deployment
3. **Test in local environment** before production
4. **Deploy during low-traffic hours** if possible
5. **Monitor logs** for 10-15 minutes after deployment
6. **Keep deployment windows short** (< 5 minutes)
7. **Document everything** in deployment log

---

**Last Deployment:** January 21, 2026  
**Current Production Version:** 1.0.0  
**Status:** ✅ Synchronized
