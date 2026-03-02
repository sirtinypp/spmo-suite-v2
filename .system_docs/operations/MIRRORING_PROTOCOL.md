# Production to Local Mirroring Protocol
**Last Updated:** February 4, 2026
**Status:** VALIDATED

## Overview
This protocol documents the steps required to achieve a 1:1 mirror of the Production Environment (`172.20.3.91`) to the Local Development Environment. This procedure ensures meaningful code, design assets (static/media), and database records are synchronized.

## Prerequisites
- SSH Access to Production (`172.20.3.91`)
- Docker Desktop installed locally
- PowerShell

## Automated Scripts
We have created scripts to automate most of this workflow.

### 1. `scripts/mirror_production.ps1`
**Purpose:** Archives remote code/media, dumps remote databases, and downloads them to local.
**Key Commands:**
- Connects to `spmo_suite` directory on remote.
- Runs `tar` to archive `gamit_app`, `gfa_app`, `suplay_app`, `spmo_website`, `nginx`.
- Runs `pg_dump` for all databases.
- Downloads files via `scp`.

### 2. `scripts/force_sync_code.ps1` (The "Nuke & Pave")
**Purpose:** Ensures absolute code parity by deleting local app directories and replacing them with the fresh archive.
**Use Case:** Run this if you suspect "ghost files" or design mismatches.
**Actions:**
- `Remove-Item -Recurse` on local app folders.
- `tar -xzf` to extract the production bundle.
- Runs `collectstatic` to regenerate assets.

### 3. `localize_settings.py`
**Purpose:** Patches the production `settings.py` files to work locally.
**Actions:**
- Appends `DEBUG = True`, `ALLOWED_HOSTS = ['*']`, and Local CSRF Trusted Origins to all `settings.py` files.
- **IMPORTANT:** This script must be run after every Code Sync.

---

## Manual Recovery Steps (If Scripts Fail)

### A. Database Restoration
If the automated restore fails, use this manual procedure:

1.  **Drop & Create**:
    ```powershell
    docker exec spmo_shared_db psql -U spmo_admin -d postgres -c "DROP DATABASE IF EXISTS db_name WITH (FORCE);"
    docker exec spmo_shared_db psql -U spmo_admin -d postgres -c "CREATE DATABASE db_name OWNER spmo_admin;"
    ```
2.  **Restore**:
    ```powershell
    Get-Content "db_name_mirror.sql" | docker exec -i spmo_shared_db psql -U spmo_admin -d db_name
    ```

### B. Superuser Access
Restoring the database overwrites the local user table. You must re-create the `grootadmin` superuser locally.
Run the provided `create_superuser.py` script on each container:
```powershell
docker cp create_superuser.py app_gamit:/app/
docker exec -e DJANGO_SETTINGS_MODULE=gamit_core.settings app_gamit python create_superuser.py
```

### C. Migration Fixes
If you encounter `InconsistentMigrationHistory` (specifically in SUPLAY):
1.  **Inject Missing Record**:
    ```powershell
    docker exec spmo_shared_db psql -U spmo_admin -d db_store -c "INSERT INTO django_migrations (app, name, applied) VALUES ('supplies', '0017_alter_annualprocurementplan_options_and_more', NOW());"
    ```
2.  **Fake Migrate**:
    ```powershell
    docker exec app_store python manage.py migrate --fake
    ```

## Stable Checkpoint
**Date:** 2026-02-04
**Git Tag:** `stable-mirror-20260204`
**State:**
- Code: 1:1 with Production `spmo_suite`
- Data: Full Restore
- Design: Parity Confirmed
