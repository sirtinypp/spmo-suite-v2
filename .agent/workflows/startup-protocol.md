---
description: JARVIS Surgical Startup Protocol (v3.2) — Unified engine for environment parity, context recovery, and security hardening.
---

# 🤖 JARVIS Surgical Startup Protocol (v3.2)

**Goal**: Establish 1:1 environmental parity, recover mission context, and detect technical drift.
**Trigger**: "initiate startup protocol", "good morning", "startup", or `/startup`

---

## 🟢 PHASE 1: The Pulse (Infrastructure & Version Control)
**Goal**: Single-batch verification of the entire technical landscape.

// turbo
```powershell
# 1.1 Docker & Remote Status
Write-Host "--- Environment Pulse ---" -ForegroundColor Cyan
docker compose ps -a --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
ssh -o ConnectTimeout=3 -p 9913 ajbasa@172.20.3.92 "docker ps --format 'table {{.Names}}\t{{.Status}}' && git -C /home/ajbasa/spmo_repo.git log --oneline -1"
ssh -o ConnectTimeout=3 -p 9913 ajbasa@172.20.3.91 "docker ps --format 'table {{.Names}}\t{{.Status}}' && git -C /home/ajbasa/spmo_repo.git log --oneline -1"

# 1.2 Git & GitHub Connectivity
Write-Host "`n--- Git & Pipeline Pulse ---" -ForegroundColor Cyan
$gitPath = (Resolve-Path "C:\Users\Aaron\AppData\Local\GitHubDesktop\app-*\resources\app\git\cmd\git.exe" | Select-Object -First 1).Path
& $gitPath status --short
& $gitPath log --oneline -3
& $gitPath remote -v
ssh -o ConnectTimeout=3 -T git@github.com

# 1.3 App Path Verification
Write-Host "`n--- App Verification ---" -ForegroundColor Cyan
Test-Path "C:\Users\Aaron\AppData\Local\GitHubDesktop\app-3.5.8\GitHubDesktop.exe"
```

---

## 📚 PHASE 2: Continuity (Context Recovery)
**Goal**: Read the **3 most recent** `DAILY_LOG_*.md` files to bridge the session gap.

### 2.1 Extraction Checklist
- **Key Accomplishments**: What was finalized?
- **Pending Tasks**: What are the active `- [ ]` items?
- **Sync Status**: Were the servers updated at EOD?
- **Surgical Guardrails**: Confirm AGENTS.md boundaries are active.

---

## 🛡 PHASE 3: Hardening (Surgical Audit)
**Goal**: Detect security holes and environment drift.

### 3.1 Security Gate 1
- **Grep Audit**: Scan `settings.py` and `.env` for `DEBUG=True` (in PROD) or hardcoded secrets.
- **Sync Drift**: Compare timestamps of `suplay_app/views/admin_views.py` on Local vs Server. If Local is newer but Git is same -> **FLAG DRIFT**.

### 3.2 Health Ping
- Attempt to hit `http://localhost:8003/health/` (or equivalent) to verify logic-integrity beyond container uptime.

---

## 📊 PHASE 4: Executive Briefing
Deliver a consolidated report:
1. **Status Table**: Local, Dev, and Prod health.
2. **"Where We Left Off"**: 1-paragraph narrative from the 3 logs.
3. **Drift & Risk Flags**: Highlight any unsynced files or security risks.
4. **Today's Agenda**: Prioritized list based on pending log items.

---
**Authority**: JARVIS Prime Orchestrator
**Institutionalized**: 2026-05-14
