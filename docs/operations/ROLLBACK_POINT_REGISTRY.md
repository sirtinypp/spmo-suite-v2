# 📌 SPMO Suite Rollback Point Registry

**Purpose:** Quick reference for all stable checkpoints and rollback points  
**Guardian:** SysOps Sentinel  
**Updated:** 2026-02-06 08:43 PHT

---

## Active Rollback Points

### 1. stable-2026-02-06-local-fixes ⭐ CURRENT (Latest)
**Date**: 2026-02-06 08:43 PHT  
**Commit**: `1b75a43`  
**Branch**: `main`  
**Status**: Local Stable - Ready for Production Deployment

**Fixes Applied**:
- **WhiteNoise Static Files**: Admin panels now serve CSS correctly with DEBUG=False
- **Logout Redirects**: Standardized all logout/timeout redirects to `/login`
- **Session Timeout**: Verified 10-minute timeout across all apps
- **Logo Standardization**: All apps now display consistent UP Logo (353KB)
- **Knowledge Base**: Documented all fixes for future reference

**Git Commits**:
- `1b75a43` - Logo standardization across all apps
- `8b1c355` - Knowledge base documentation
- `370014f` - Logout redirect fix
- `277adbd` - Hub WhiteNoise middleware
- `6596650` - GAMIT/LIPAD WhiteNoise middleware

**Rollback Command**:
```bash
git fetch origin main
git reset --hard 1b75a43
docker compose down && docker compose up -d --build
```

**Verification Checklist**:
- ✅ All admin panels display with CSS
- ✅ Logout buttons redirect to /login
- ✅ Session timeout redirects to /login
- ✅ All logos display UP Logo
- ✅ All 4 apps running (Hub, GAMIT, LIPAD, SUPLAY)

---

### 2. stable-2026-02-05-production-v1.2.0 (Golden)
**Date**: 2026-02-05 11:45 PHT  
**Commit**: `4df3b6f`  
**Branch**: `main`  
**Status**: Production Live, Security Hardened, Nginx DNS Fixed.

**Architecture**:
- **Source**: [spmo-suite-v2](https://github.com/sirtinypp/spmo-suite-v2)
- **Security**: No hardcoded credentials. Nginx Dynamic Resolver active.
- **Backups**: Remote (`~/backups/archive/spmo_suite_pre_deploy_20260205.tar.gz`)

**Rollback Command**:
```bash
git fetch origin main
git reset --hard 4df3b6f
docker compose down && docker compose up -d --build
```

---

### 2. stable-2026-02-02-safety-lock (GitHub v2)
**Date:** 2026-02-02 10:40 PHT  
**Commit:** `a2c2df7`  
**Branch:** `main` (GitHub v2)
**Database:** `db_full_backup_20260202.sql`

**Architecture:**
- **Source of Truth:** [spmo-suite-v2](https://github.com/sirtinypp/spmo-suite-v2)
- **Deployment:** Safety-locked deployment hook (Automated GitHub Sync)
- **Status:** All domains verified and routing locked.

**Rollback Command:**
```bash
# Force the entire suite back to this verified state
git fetch origin main
git reset --hard stable-2026-02-02-safety-lock
git clean -fd
docker compose up -d --build
```

---

### 2. stable-2026-02-02-session-start (Pre-v2 Migration)
@12: **Date:** 2026-02-02 07:55 PHT  
**Commit:** `e32dec1`  
**Branch:** `feature/app-filtered-shop` (Legacy)

### 2. stable-2026-01-29-security-hardening

**Changes:**
- **SUPLAY:** SECRET_KEY to environment, ALLOWED_HOSTS improved, DEBUG prepared
- **GAMIT:** SECRET_KEY to environment, ALLOWED_HOSTS improved
- Zero downtime deployment for both apps

**Rollback Commands:**
```bash
# Code
git checkout stable-2026-01-29-security-hardening

# Database (if needed)
docker exec -i spmo_shared_db psql -U spmo_admin db_store < ~/backups/db_store_backup_2026_01_29_security.sql
```

**Verification:**
- ✅ SUPLAY: HTTP 200, 132 images
- ✅ GAMIT: HTTP 200
- ✅ Security improved (P0 fixes complete)

---

### 2. stable-2026-01-29-security-p0
**Date:** 2026-01-29 10:15 PHT  
**Commit:** TBD (latest)  
**Branch:** `feature/app-filtered-shop`  
**Database:** `db_store_backup_2026_01_29_security.sql`

**Changes:**
- SECRET_KEY moved to environment variable
- ALLOWED_HOSTS improved default
- DEBUG prepared for environment control
- Zero downtime deployment

**Rollback Commands:**
```bash
# Code
git checkout stable-2026-01-29-security-p0

# Database
docker exec -i spmo_shared_db psql -U spmo_admin db_store < ~/backups/db_store_backup_2026_01_29_security.sql
```

**Verification:**
- ✅ Homepage HTTP 200
- ✅ Product images (132)
- ✅ Container healthy
- ✅ Security improved (2 of 3 P0 fixed)

---

### 2. stable-2026-01-29-suplay-fixes
**Date:** 2026-01-29 09:35 PHT  
**Commit:** `3ec41ad`  
**Branch:** `feature/app-filtered-shop`  
**Database:** `db_store_backup_2026_01_29.sql` (1.5MB)

**Changes:**
- SUPLAY product image display fix (339 products populated)
- Out-of-stock filter parameter fix
- Public product browsing enabled
- Django management command: `populate_product_images.py`

**Rollback Commands:**
```bash
# Code
git checkout stable-2026-01-29-suplay-fixes

# Database
docker exec -i spmo_shared_db psql -U spmo_admin db_store < ~/backups/db_store_backup_2026_01_29.sql
```

**Verification:**
- ✅ Product images display (132 images)
- ✅ Stock filter functional
- ✅ All domains routing correctly
- ✅ Infrastructure Lock intact

---

### 2. stable-post-rollback-2026-01-29
**Date:** 2026-01-29 (Morning)  
**Commit:** `4e46b75`  
**Database:** `production_dump_20260129_post_rollback.sql` (1.6MB)

**State:**
- Post-ROLLBACK-PATCH-1 recovery
- Correct domain routing restored
- `DEBUG=True` for all apps
- Infrastructure Lock activated

**Rollback Commands:**
```bash
# Code
git checkout stable-post-rollback-2026-01-29

# Database
docker exec -i spmo_shared_db psql -U spmo_admin -d db_gamit < ~/backups/production_dump_20260129_post_rollback_gamit.sql
docker exec -i spmo_shared_db psql -U spmo_admin -d db_store < ~/backups/production_dump_20260129_post_rollback_store.sql
```

---

### 3. stable-2026-01-28-post-recovery
**Date:** 2026-01-28  
**Commit:** (Prior to rollback)

**State:**
- All applications accessible
- Domain routing correct
- SUPLAY database repaired
- `DEBUG=True`

---

## Rollback Protocol

### Quick Rollback (Code Only)
```bash
cd ~/spmo-suite
git checkout <tag-name>
cd ~/spmo_suite
sudo docker compose down
sudo docker compose up -d --build
```

### Full Rollback (Code + Database)
```bash
# 1. Stop services
cd ~/spmo_suite
sudo docker compose down

# 2. Restore code
cd ~/spmo-suite
git checkout <tag-name>

# 3. Restore database
docker exec -i spmo_shared_db psql -U spmo_admin db_store < ~/backups/<backup-file>

# 4. Restart services
cd ~/spmo_suite
sudo docker compose up -d --build
```

### Verification Checklist
- [ ] All domains route correctly
- [ ] Applications load (HTTP 200)
- [ ] Critical features functional
- [ ] Database integrity verified
- [ ] Infrastructure Lock status checked

---

## Backup Locations

### Production Server
**Path:** `/home/ajbasa/backups/`

**Files:**
- `db_store_backup_2026_01_29.sql` (1.5MB) - SUPLAY (Latest)
- `production_dump_20260129_post_rollback.sql` (1.6MB) - All DBs (Post-Rollback)
- `production_dump_20260128_stabilized.sql` (0B) - **INVALID - Do not use**

### Local Repository
**Branch:** `feature/app-filtered-shop`  
**Tags:** All rollback points tagged with `stable-*` prefix

---

## Emergency Contacts

**Infrastructure Lock Guardian:** SysOps Sentinel  
**Orchestrator:** JARVIS  
**Approval Required:** USER (Aaron)

---
*Registry maintained by SysOps Sentinel*
