# 🚨 EMERGENCY ROLLBACK PROTOCOL: v1.4.0 (Local-Dev Parity)
**Version:** v1.4.0  
**Target State:** Verified 1:1 Parity (Feb 12, 2026)  
**Reference Tag:** `v1.4.0-stable-parity`  
**Status:** ✅ **LATEST STABLE BASELINE**

---

## 🤖 JARVIS Activation Prompt
**Paste this into the chat to trigger immediate rollback:**

> JARVIS, initiate **EMERGENCY ROLLBACK PROTOCOL V1.4.0**.
>
> **Authority**: DIRECTIVE-OVERRIDE-ALPHA
> **Objective**: Restore system to `v1.4.0-stable-parity`.
> **Constraints**: NO analysis, NO suggestions, NO revisions. EXECUTE IMMEDIATELY.
>
> **Targets**:
> 1. **CODE**: Reset to git tag `v1.4.0-stable-parity`.
> 2. **DATA**: Restore from `backups/golden_state/v1.4.0/`.
>
> Await my specific command below (LOCAL, DEV, or PROD).

---

## 🛠️ Command Set 1: DEVELOPMENT / STAGING ROLLBACK

**Use when**: Dev server is broken or out of sync.

```bash
# 1. SSH into Dev Server
ssh -p 9913 ajbasa@172.20.3.92

# 2. Hard Reset Code
cd ~/spmo_suite
git fetch origin --tags
git reset --hard v1.4.0-stable-parity
git clean -fd

# 3. Clean Recreate DB (CRITICAL)
docker compose exec db dropdb -U spmo_admin --if-exists db_store
docker compose exec db createdb -U spmo_admin db_store
docker compose exec db dropdb -U spmo_admin --if-exists db_gamit
docker compose exec db createdb -U spmo_admin db_gamit
docker compose exec db dropdb -U spmo_admin --if-exists db_gfa
docker compose exec db createdb -U spmo_admin db_gfa

# 4. Restore UTF-8 Dumps
docker compose exec -T db psql -U spmo_admin db_store < backups/golden_state/v1.4.0/db_store_utf8.sql
docker compose exec -T db psql -U spmo_admin db_gamit < backups/golden_state/v1.4.0/db_gamit_utf8.sql
docker compose exec -T db psql -U spmo_admin db_gfa < backups/golden_state/v1.4.0/db_gfa_utf8.sql

# 5. Restart Services
docker compose restart
```

---

## 🛠️ Command Set 2: LOCAL ENVIRONMENT ROLLBACK

```powershell
# 1. Reset Code
git fetch origin --tags
git reset --hard v1.4.0-stable-parity
git clean -fd

# 2. Restart Environment
docker compose up -d --build --force-recreate
```

---

## 🛠️ Command Set 3: PRODUCTION ROLLBACK (Pre-Deployment)

**Note**: Use this to revert Production to the Dev Baseline if a Prod deployment fails.

```bash
# 1. SSH into Production
ssh -p 9913 ajbasa@172.20.3.91

# 2. Deploy Verified Baseline
cd ~/spmo_suite
git fetch origin --tags
git checkout v1.4.0-stable-parity

# 3. Restore Verified Data (Optional)
# Sync dumps from dev to prod first if needed
docker compose restart
```

---

**Protocol End.**
