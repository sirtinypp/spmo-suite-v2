# 🛠️ Revision Preparation Protocol (Local)

**Purpose**: Standard checklist to ensure the local environment is healthy and ready for new code changes.
**Mandatory Before**: Starting ANY new task or bug fix.

---

## 📋 Step 1: Health Check (The Clean Slate)

Before touching any code, verify the "Golden State" is active.

1.  **Git Status**:
    - [ ] Run `git status`.
    - [ ] Must be on a clean stable tag (e.g., `v1.3.0` or `main`).
    - [ ] No uncommitted changes.

2.  **Container Status**:
    - [ ] Run `docker ps`.
    - [ ] All 5 containers must be `Up`.
        - `spmo_gateway` (Ports 8000-8003)
        - `app_hub`
        - `app_gamit`
        - `app_store` (SUPLAY)
        - `app_gfa` (LIPAD)

3.  **Connectivity Check**:
    - [ ] Open `http://localhost:8000` (Hub) -> Should load 200 OK.
    - [ ] Open `http://localhost:8001` (GAMIT) -> Should load 200 OK.
    - [ ] Open `http://localhost:8002` (LIPAD) -> Should load 200 OK.
    - [ ] Open `http://localhost:8003` (SUPLAY) -> Should load 200 OK.

---

## ⚙️ Step 2: Environment Configuration

To develop locally, `DEBUG` must be ON.

1.  **Check `.env`**:
    - [ ] Run `type .env`.
    - [ ] Ensure `DEBUG=True` exists.
    - [ ] Ensure `DJANGO_DEBUG=True` exists.

2.  **Verify Application Config**:
    - [ ] If containers were running `DEBUG=False` (from a test), RESTART them:
    ```powershell
    docker compose down
    docker compose up -d --build
    ```

---

## 🌿 Step 3: Branching Strategy (Critical)

**NEVER commit directly to `main` or a `stable` tag.**

1.  **Create Revision Branch**:
    - **Naming Convention**: `feature/<version>-<short-description>`
    - **Example**: `feature/v1.3.1-fix-logout-redirect`

    ```powershell
    # 1. Fetch latest
    git fetch origin --tags

    # 2. Checkout base (usually main or specific tag)
    git checkout v1.3.0-stable-verified

    # 3. Create NEW branch
    git checkout -b feature/v1.3.1-fix-logout-redirect
    ```

---

## 🚀 Step 4: Ready for Revision

Only when **Steps 1-3** are ✅ checked, you may proceed to edit code.

---

### 🚨 Emergency Stop
If `git status` shows unexplained changes or containers fail to start:
1.  **STOP**.
2.  Run **Emergency Rollback (Local)**.
3.  Do not debug a broken baseline. Reset it first.
