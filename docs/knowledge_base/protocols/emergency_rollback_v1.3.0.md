# 🚨 EMERGENCY ROLLBACK PROTOCOL: v1.3.0 (Golden State)

**Trigger Warning**: Execute ONLY in case of critical system failure or data corruption.
**Target State**: Verified Secure State (Feb 6, 2026 - 10:50 AM)
**Reference**: `v1.3.0-stable-verified`

---

## 🤖 JARVIS Activation Prompt

**Paste this into the chat to trigger immediate rollback:**

> JARVIS, initiate **EMERGENCY ROLLBACK PROTOCOL V1.3.0**.
>
> **Authority**: DIRECTIVE-OVERRIDE-ALPHA
> **Objective**: Restore system to `v1.3.0-stable-verified`.
> **Constraints**: NO analysis, NO suggestions, NO revisions. EXECUTE IMMEDIATELY.
>
> **Targets**:
> 1. **CODE**: Reset to git tag `v1.3.0-stable-verified`.
> 2. **DATA**: Restore database from `spmo_suite/backups/db/db_full_backup_20260206_post_vuln_fix.sql`.
>
> Await my specific command below (LOCAL, PROD, or BOTH).

---

## 🛠️ Command Set 1: LOCAL ROLLBACK (Code Only)

**Use when**: Local development environment is broken.

```powershell
# 1. Stop Containers
docker compose down

# 2. Hard Reset Code
git fetch origin --tags
git reset --hard v1.3.0-stable-verified
git clean -fd

# 3. Restart Environment
docker compose up -d --build --force-recreate
```

---

## 🛠️ Command Set 2: PRODUCTION ROLLBACK (Code + Data)

**Use when**: Production server is compromised or corrupt.

```bash
# 1. SSH into Production
ssh -p 9913 ajbasa@172.20.3.91

# 2. Stop Services
cd spmo_suite
docker compose down

# 3. Restore Code
cd ..
cd spmo_suite_repo  # or relevant git directory
git fetch origin --tags
git checkout v1.3.0-stable-verified

# 4. Start Database Only (For Restore)
cd ../spmo_suite
docker compose up -d db
sleep 10  # Wait for DB to wake up

# 5. Restore Database (CRITICAL STEP)
# WARNING: This OVERWRITES existing data
docker exec -i spmo_shared_db psql -U spmo_admin postgres < backups/db/db_full_backup_20260206_post_vuln_fix.sql

# 6. Full Restart
docker compose down
docker compose up -d --build --force-recreate
```

---

## 🛠️ Command Set 3: TOTAL SYSTEM RESTORE (Both)

**Use when**: Complete synchronization is required.

```powershell
# STEP 1: RESTORE LOCAL
docker compose down
git fetch origin --tags
git reset --hard v1.3.0-stable-verified
docker compose up -d --build

# STEP 2: RESTORE PRODUCTION (via SSH)
ssh -p 9913 ajbasa@172.20.3.91 "cd spmo_suite && docker compose down"
ssh -p 9913 ajbasa@172.20.3.91 "cd spmo_suite && git fetch origin --tags && git checkout v1.3.0-stable-verified"
ssh -p 9913 ajbasa@172.20.3.91 "cd spmo_suite && docker compose up -d db && sleep 15"
# Restore Data
ssh -p 9913 ajbasa@172.20.3.91 "docker exec -i spmo_shared_db psql -U spmo_admin postgres < spmo_suite/backups/db/db_full_backup_20260206_post_vuln_fix.sql"
# Restart All
ssh -p 9913 ajbasa@172.20.3.91 "cd spmo_suite && docker compose down && docker compose up -d --build"
```

---

**Protocol End.**
