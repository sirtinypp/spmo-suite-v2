# SPMO Suite: Operations Manual
**Version:** 2.0 (Stable Mirror)
**Last Updated:** February 4, 2026

## 1. Daily Startup Protocol
**Run this every morning to ensure your environment is healthy.**

```powershell
./scripts/daily_startup.ps1
```
*Checks:* Docker status, Port availability, Application Health.

---

## 2. Dealing with "Drift" (Production vs Local)
If you suspect the Local Environment is broken or out of sync with Production:

### The "Mirror Check"
Before doing anything drastic, check if verify parity:
1.  Check `http://localhost:8001` (GAMIT).
2.  Check `https://gamit-sspmo.up.edu.ph` (Production).
3.  If they differ, proceed to **Rescue**.

### The Rescue Protocol (Nuclear Option)
This will delete local data and code, and replace it with a fresh copy from Production.
**Use with caution.**

1.  Run the Mirror Script:
    ```powershell
    ./scripts/mirror_production.ps1
    ```
2.  **Wait.** This takes ~15 minutes (Database dumps + Media download).
3.  **Restore Databases** (If script fails locally):
    See `MIRRORING_PROTOCOL.md` for manual restore steps.
4.  **Inject Settings**:
    ```powershell
    python localize_settings.py
    ```

---

## 3. "Safe Deployment" Protocol (Local -> Production)
**Goal:** Push your cosmetic/code changes to Production WITHOUT breaking security settings or deleting data.

### When to use:
- You changed a CSS file.
- You updated an HTML template.
- You fixed a Python Logic bug (views.py, models.py).

### How to use:
1.  **Commit your changes** to Git first (Safety Net).
2.  Run the Safe Deploy script:
    ```powershell
    ./scripts/deploy_safe.ps1
    ```
3.  **Approve the Restart**.
4.  **Verify** on the live site.

**What this protects:**
- `settings.py` (Production Security) - **SAFE**
- `db.sqlite3` / `postgres` (User Data) - **SAFE**
- `media/` (User Uploads) - **SAFE**

---

## 4. Emergency Contacts
- **System Admin**: root@172.20.3.91 (Access via SSH)
- **Database**: `spmo_shared_db` container.
- **Superuser**: `grootadmin` / `xiarabasa12`

---

## 5. Agent Roles & Orchestration (The "Check & Balance" System)
To ensure stability, we operate using a **Role-Based Workflow**. "JARVIS" acts as the Project Manager, ensuring no single agent acts without verification.

### 🤖 The Manager
*   **JARVIS (The Orchestrator)**:
    *   **Role**: Strategy, Delegation, and Final Review.
    *   **Responsibility**: Does not touch code directly. Reviews plans from Architects and logs from Sentinels before approving deployment.
    *   **Trigger**: "Jarvis, what is the plan?" or "Jarvis, verify this."

### 🛠️ The Specialists
*   **SysOps Sentinel**:
    *   **Role**: Server & Infrastructure reliability.
    *   **Responsibility**: Restarts containers, checks logs, manages Docker, ensures ports are open. **Guardian of `deploy_safe.ps1`**.
*   **Data Weaver**:
    *   **Role**: Database Integrity & Migration.
    *   **Responsibility**: Handles SQL dumps, restoration, and troubleshooting `InconsistentMigrationHistory`. **Guardian of `mirror_production.ps1`**.
*   **Frontend Architect**:
    *   **Role**: Design & UX.
    *   **Responsibility**: Edits CSS/HTML. Ensures design parity between Local and Production.
*   **Vault Guardian**:
    *   **Role**: Backup & Source Control.
    *   **Responsibility**: Manages Git commits, checkpoints, and safe rollbacks.

---

## 6. Protocol: How to Add Features or Change Databases
**Question:** "We want to add a new column to a table, or a new feature. How do we do it safely?"

**The "Safe Expansion" Workflow:**

### Phase 1: Local Development (The Laboratory)
1.  **Frontend/Logic**: Edit your code locally.
2.  **Database**:
    *   Modify `models.py`.
    *   Run `makemigrations`.
    *   Run `migrate`.
3.  **Verify**: Test it extensively on `localhost`.

### Phase 2: The Checkpoint
1.  **Commit**: `git add .` and `git commit -m "New Feature X"`.
2.  **Backup**: Ensure you have a recent dump of production (just in case).

### Phase 3: Agent-Mediated Deployment (The "Safe Push")
**CRITICAL:** To prevent human error, **User DO NOT run deployment scripts directly.**

1.  **Request Deployment**:
    *   **User Action**: Tell Jarvis: *"Jarvis, please deploy the new [Feature Name] to production."*
    *   **Jarvis Action**: Jarvis will verify the `git status` and deployment plan.
2.  **Delegation (SysOps Sentinel)**:
    *   Jarvis delegating to **SysOps Sentinel**.
    *   **SysOps Action**: Runs `./scripts/deploy_safe.ps1`.
3.  **Database Migration (If needed)**:
    *   **User Action**: Check with Jarvis if migration is needed.
    *   **SysOps Action**: SSH triggers `python manage.py migrate` on the remote container.

**Why this rule?**
Agents checking `deploy_safe.ps1` ensures checking of the *Blocklist* (excluding settings.py) is never skipped.

**Rule of Thumb**: Code moves via Script. Database moves via Migration Command.
