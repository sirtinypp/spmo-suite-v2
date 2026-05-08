# DEPLOYMENT PLAYBOOK
**SPMO Suite — Verified Deployment Reference**  
**Last Verified:** May 8, 2026  
**Status:** ✅ Proven on DEV (.92) deployment

---

## 1. Infrastructure Map

| Property | DEV Server | PROD Server |
|---|---|---|
| **Internal IP** | `172.20.3.92` | `172.20.3.91` |
| **Public URL** | `https://gamit-sspmo-dev.up.edu.ph/` | `https://gamit-sspmo.up.edu.ph/` |
| **SSH Command** | `ssh -p 9913 ajbasa@172.20.3.92` | `ssh -p 9913 ajbasa@172.20.3.91` |
| **SSH User** | `ajbasa` | `ajbasa` |
| **SSH Port** | `9913` | `9913` |
| **Working Dir** | `~/spmo_suite/` | `~/spmo_suite/` |
| **Git Branch** | `main` (pulls from `origin/main`) | `main` (pulls from `origin/main`) |
| **Docker Compose** | `~/spmo_suite/docker-compose.yml` | `~/spmo_suite/docker-compose.yml` |

### Container Names (Both Servers)
| Service Name (compose) | Container Name (docker) | App |
|---|---|---|
| `gamit_app` | `app_gamit` | GAMIT Asset Manager |
| `spmo_website` | `app_hub` | SPMO Hub / Landing |
| `gfa_app` | `app_gfa` | GFA |
| `virtual_store` | `app_store` | Virtual Store |
| `db` | `spmo_shared_db` | PostgreSQL 15 |
| `nginx` | `spmo_gateway` | Nginx Reverse Proxy |

> **IMPORTANT:** When using `docker compose exec`, use the **service name** (e.g., `gamit_app`).  
> When using `docker exec`, use the **container name** (e.g., `app_gamit`).

### Full Suite URLs

| App | DEV | PROD |
|---|---|---|
| Hub | `https://sspmo-dev.up.edu.ph` | `https://sspmo.up.edu.ph` |
| GAMIT | `https://gamit-sspmo-dev.up.edu.ph` | `https://gamit-sspmo.up.edu.ph` |
| LIPAD | `https://lipad-sspmo-dev.up.edu.ph` | `https://lipad-sspmo.up.edu.ph` |
| SUPLAY | `https://suplay-sspmo-dev.up.edu.ph` | `https://suplay-sspmo.up.edu.ph` |

---

## 2. Local Environment

| Property | Value |
|---|---|
| **Project Root** | `c:\Users\Aaron\spmo-suite - Copy` |
| **Git Binary** | `C:\Users\Aaron\AppData\Local\GitHubDesktop\app-3.5.8\resources\app\git\cmd\git.exe` |
| **Git Alias** | Use `& "C:\Users\Aaron\AppData\Local\GitHubDesktop\app-3.5.8\resources\app\git\cmd\git.exe"` in PowerShell |
| **Local GAMIT URL** | `http://localhost:8001/` |
| **Local Superuser** | `grootadmin` / `xiarabasa12` |

### Git Remotes

| Remote | URL | Purpose |
|---|---|---|
| `origin` | `git@github.com:sirtinypp/spmo-suite-v2.git` | GitHub — Cloud backup & source of truth |
| `deploy` | `ssh://ajbasa@172.20.3.91:9913/home/ajbasa/spmo_repo.git` | PROD bare repo (legacy, prefer origin) |
| `production` | `ssh://ajbasa@172.20.3.91:9913/home/ajbasa/spmo_repo.git` | Duplicate of deploy |
| `staging` | `ssh://ajbasa@172.20.3.92:9913/home/ajbasa/spmo_repo.git` | DEV bare repo (added May 8) |

> **Source of Truth:** Always push to `origin` first. Both servers pull FROM `origin`.

---

## 3. Deployment Steps

### Pre-Flight (Local)

```powershell
# 1. Django health check
docker exec app_gamit python manage.py check

# 2. Verify template integrity
docker exec app_gamit python manage.py check --tag templates

# 3. Stage and commit (semantic format)
& "<git-path>" add -A
& "<git-path>" commit -m "feat(gamit): description"

# 4. Create rollback anchor tag
& "<git-path>" tag -a <tag-name> -m "description"

# 5. Push to GitHub (source of truth)
& "<git-path>" push origin main
```

### Deploy to DEV (.92)

```bash
# 1. SSH into DEV
ssh -p 9913 ajbasa@172.20.3.92

# 2. Pull latest from GitHub
cd ~/spmo_suite
git fetch origin
git reset --hard origin/main
git clean -fd

# 3. Restart the target app container
docker compose restart gamit_app

# 4. Run migrations (if models changed)
docker compose exec -T gamit_app python manage.py migrate

# 5. Run management commands (if needed)
docker compose exec -T gamit_app python manage.py seed_institutional

# 6. Collect static files (if CSS/JS changed)
docker compose exec -T gamit_app python manage.py collectstatic --noinput
```

### Deploy to PROD (.91)

Same steps as DEV, but target `.91`:

```bash
# 1. SSH into PROD
ssh -p 9913 ajbasa@172.20.3.91

# 2. Pull latest from GitHub
cd ~/spmo_suite
git fetch origin
git reset --hard origin/main
git clean -fd

# 3. Restart + Migrate
docker compose restart gamit_app
docker compose exec -T gamit_app python manage.py migrate

# 4. Collect static (if needed)
docker compose exec -T gamit_app python manage.py collectstatic --noinput
```

### One-Liner (Copy-Paste Ready)

**DEV:**
```powershell
ssh -p 9913 ajbasa@172.20.3.92 "cd ~/spmo_suite && git fetch origin && git reset --hard origin/main && git clean -fd && docker compose restart gamit_app && docker compose exec -T gamit_app python manage.py migrate"
```

**PROD:**
```powershell
ssh -p 9913 ajbasa@172.20.3.91 "cd ~/spmo_suite && git fetch origin && git reset --hard origin/main && git clean -fd && docker compose restart gamit_app && docker compose exec -T gamit_app python manage.py migrate"
```

---

## 4. Post-Deployment Smoke Test

1. Visit the public URL (DEV or PROD)
2. Hard refresh: `Ctrl + Shift + R`
3. Verify:
   - Dashboard loads with KPI cards
   - Asset Registry search works
   - Activity Pulse tab renders (no 500 error)
   - One write action (e.g., filter or form submit)
4. Deployment is **COMPLETE** only when smoke test passes

---

## 5. Rollback Procedure

```bash
# On the target server:
cd ~/spmo_suite
git fetch origin
git reset --hard <tag-name>
docker compose restart gamit_app
```

Verify with: `docker compose exec -T gamit_app python manage.py check`

---

## 6. Available Management Commands

| Command | App | Purpose |
|---|---|---|
| `seed_institutional` | `workflow` | Seeds Roles, 64 Ghost Army Personas, and Signatory Slots |
| `migrate` | Django core | Applies database schema changes |
| `collectstatic` | Django core | Bundles CSS/JS for WhiteNoise serving |
| `check` | Django core | System health check |
| `createsuperuser` | Django core | Creates admin user |

---

## 7. Known Pitfalls

### Management Commands
- Must be placed inside an **installed app's** directory (e.g., `workflow/management/commands/`)
- Placing at project root (`gamit_app/management/`) will NOT be discovered by Django

### Settings & Config
- **NEVER** copy `settings.py` between environments — each server has its own via `.env` and `docker-compose.yml`
- **NEVER** insert `socialaccount_socialapp` DB records — allauth reads from `settings.py`
- `DJANGO_SECRET_KEY_GAMIT` is the env var name on servers (not `DJANGO_SECRET_KEY`)

### Docker
- `docker compose` commands use **service names**: `gamit_app`, `gfa_app`, etc.
- `docker exec` commands use **container names**: `app_gamit`, `app_gfa`, etc.
- After code pull, always `restart` the container to flush Django's template cache

### Git / GitHub
- Never commit `.sqlite3`, `.env`, or `media/` files
- If GitHub blocks push due to secret scanning, use the unblock URL from the error message
- The `post-receive` hooks on both servers pull from `origin/main` — do NOT modify them

### Server Directory Structure
- Both servers have legacy directories (`~/spmo-suite/`, `~/gamit_app/`). **Ignore them.**
- The active working directory is always `~/spmo_suite/`
- Docker Compose on DEV (.92) has a **root-level** `~/docker-compose.yml` that is NOT the active one. Always `cd ~/spmo_suite` first.
