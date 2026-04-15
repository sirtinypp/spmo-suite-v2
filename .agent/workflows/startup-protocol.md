---
description: JARVIS Daily Startup Protocol — single trigger to execute the full morning boot sequence across all environments.
---

# 🤖 JARVIS Daily Startup Protocol

**Version**: 2.0.0
**Effective**: 2026-03-04
**Trigger**: User says "initiate startup protocol", "good morning", "startup", or invokes `/startup`
**Authority**: JARVIS (Prime Orchestrator)

---

## Overview

This is the **single source of truth** for the JARVIS morning startup sequence. When triggered, execute all 5 phases **in order**, then deliver a unified startup report to the user. Do NOT skip phases. Do NOT ask for permission between phases — execute the full sequence and report at the end.

---

## Phase 1: Server Status Check

**Goal**: Verify all environments are operational.

### 1.1 Local Environment (Docker Desktop)
// turbo
```powershell
docker compose ps -a --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
```

**Expected containers (6 total):**

| Container | Service | Port |
|-----------|---------|------|
| `spmo_gateway` | Nginx reverse proxy | `:80` |
| `spmo_shared_db` | PostgreSQL 15 | `:5432` |
| `app_hub` | SPMO Hub | `:8000` |
| `app_gamit` | GAMIT | `:8001` |
| `app_gfa` | LIPAD | `:8002` |
| `app_store` | SUPLAY | `:8003` |

- If any container is DOWN → **ACTION**: Immediately run `docker compose up -d` to restore services.
- If all 6 are UP → report 🟢 6/6

### 1.2 Dev / Staging Server (`172.20.3.92`)
// turbo
```powershell
ssh -o ConnectTimeout=5 -p 9913 ajbasa@172.20.3.92 "docker ps --format 'table {{.Names}}\t{{.Status}}' && git -C /home/ajbasa/spmo_repo.git log --oneline -1"
```

- If SSH succeeds → report container count + current commit
- If SSH fails → report "⚠️ UNREACHABLE" and cite last known state from most recent daily log

### 1.3 Production Server (`172.20.3.91`)
// turbo
```powershell
ssh -o ConnectTimeout=5 -p 9913 ajbasa@172.20.3.91 "docker ps --format 'table {{.Names}}\t{{.Status}}' && git -C /home/ajbasa/spmo_repo.git log --oneline -1"
```

- Same logic as 1.2
- Include public domain status if reachable: `sspmo.up.edu.ph`, `gamit-sspmo.up.edu.ph`, `lipad-sspmo.up.edu.ph`, `suplay-sspmo.up.edu.ph`

### 1.4 Output Format
```markdown
| Environment | Containers | Commit | Status |
|-------------|-----------|--------|--------|
| **Local** | 🟢 6/6 | `abc1234` | ✅ Healthy |
| **Dev (172.20.3.92)** | 🟢 6/6 | `def5678` | ✅ Healthy |
| **Prod (172.20.3.91)** | 🟢 6/6 | `def5678` | ✅ Healthy |
```

---

## Phase 2: Internalize Knowledge Base, Personas & Protocols

**Goal**: Load all governance rules and agent personas into active context.

### 2.1 Governance Protocols (MUST READ)
- [`.agent/MANAGEMENT_PROTOCOLS.md`](file:///c:/Users/Aaron/spmo-suite%20-%20Copy/.agent/MANAGEMENT_PROTOCOLS.md) — Logging, stability, jurisdiction
- [`.agent/AGENT_BOUNDARIES.md`](file:///c:/Users/Aaron/spmo-suite%20-%20Copy/.agent/AGENT_BOUNDARIES.md) — Per-agent safe zones and forbidden actions
- [`.agent/JARVIS_LOCK_ENFORCEMENT.md`](file:///c:/Users/Aaron/spmo-suite%20-%20Copy/.agent/JARVIS_LOCK_ENFORCEMENT.md) — Production lock, violation detection
- [`.agent/JARVIS_KNOWLEDGE_BASE_PROTOCOL.md`](file:///c:/Users/Aaron/spmo-suite%20-%20Copy/.agent/JARVIS_KNOWLEDGE_BASE_PROTOCOL.md) — KB management rules
- [`.agent/TEMPLATE_TAG_PREVENTION.md`](file:///c:/Users/Aaron/spmo-suite%20-%20Copy/.agent/TEMPLATE_TAG_PREVENTION.md) — Django template rendering safeguards
- [`.agent/EXECUTION_STANDARD.md`](file:///c:/Users/Aaron/spmo-suite%20-%20Copy/.agent/EXECUTION_STANDARD.md) — The Surgical Protocol (Gold Standard for task execution)
- [`.PERSONA_PROTOCOL.md`](file:///C:/Users/Aaron/.gemini/antigravity/brain/ced3c0e6-db52-4c9c-a142-419bcb84fc7e/PERSONA_PROTOCOL.md) — **CRITICAL**: SPMO Suite Context Isolation

### 2.2 Agent Personas (MUST READ)
- [`.agent/workflows/role-manager.md`](file:///c:/Users/Aaron/spmo-suite%20-%20Copy/.agent/workflows/role-manager.md) — JARVIS
- [`.agent/workflows/role-frontend.md`](file:///c:/Users/Aaron/spmo-suite%20-%20Copy/.agent/workflows/role-frontend.md) — Frontend Architect
- [`.agent/workflows/role-hub.md`](file:///c:/Users/Aaron/spmo-suite%20-%20Copy/.agent/workflows/role-hub.md) — Hub Master Admin
- [`.agent/workflows/role-logic.md`](file:///c:/Users/Aaron/spmo-suite%20-%20Copy/.agent/workflows/role-logic.md) — App Logic Specialist
- [`.agent/workflows/role-security.md`](file:///c:/Users/Aaron/spmo-suite%20-%20Copy/.agent/workflows/role-security.md) — Security Shield
- [`.agent/workflows/role-sysops.md`](file:///c:/Users/Aaron/spmo-suite%20-%20Copy/.agent/workflows/role-sysops.md) — SysOps Sentinel
- [`.agent/workflows/role-data.md`](file:///c:/Users/Aaron/spmo-suite%20-%20Copy/.agent/workflows/role-data.md) — Data Weaver
- [`.agent/workflows/role-backup.md`](file:///c:/Users/Aaron/spmo-suite%20-%20Copy/.agent/workflows/role-backup.md) — Vault Guardian

### 2.3 Knowledge Items (from Antigravity KI store)
- Read latest artifacts from **SPMO Suite Operational Governance Protocols** KI
- Read latest artifacts from **SPMO Suite Technical Implementation and Architecture** KI
- Specifically: `agent_decision_delegation.md`, `overview.md`, `security_hardening_standards.md`

### 2.4 Confirmation
After reading, silently confirm these rules are active:
- ✅ Production Lock (Tier 1/2/3 file protection)
- ✅ User-Driven Authority (no unilateral decisions)
- ✅ No Rabbit Holes (stay on task)
- ✅ Verification First (check before fixing)
- ✅ Double-Entry Logging (agent log + CHANGELOG)
- ✅ **Persona Lock** (Strict focus: GAMIT, LIPAD, SUPLAY)
- ✅ **Execution Guardrails** (No automated simulations or complex scripts without explicit user validation; seek simple UI/DB fixes first)

---

## Phase 3: Daily Log Review (Last 5 Days)

**Goal**: Establish continuity — know where we left off.

### 3.1 Locate Logs
Read the **5 most recent** `DAILY_LOG_*.md` files from:
- KI path: `spmo_operational_governance/artifacts/daily_logs/`
- Sort by date descending, read all 5

### 3.2 Extract from Each Log
For each log, extract:
- **Date** and **session status** (Active/Complete/Offline)
- **Key accomplishments** (bullet summary)
- **Pending items** (incomplete checkboxes `- [ ]`)
- **EOD sign-off status** (was Vault Guardian protocol completed?)
- **Git state at EOD** (branch, commit, clean/dirty)

### 3.3 Build Continuity Summary
Compile a "Where We Left Off" narrative:
- What was the last completed feature/fix?
- What items are still pending?
- Are there any deferred deployments?
- What was the user's stated "tomorrow's agenda"?

---

## Phase 4: Agent Roll Call

**Goal**: Confirm all agents are accounted for and their workflow files exist.

### 4.1 Agent Roster

| # | Agent | Role | Workflow File | Activation |
|---|-------|------|---------------|------------|
| 1 | **JARVIS** | Prime Orchestrator | `role-manager.md` | Always active |
| 2 | **Frontend Architect** | UI/UX, CSS, Templates | `role-frontend.md` | `/role-frontend` |
| 3 | **Hub Master Admin** | Landing page, cross-app | `role-hub.md` | `/role-hub` |
| 4 | **App Logic Specialist** | GAMIT / SUPLAY / LIPAD | `role-logic.md` | `/role-logic` |
| 5 | **Security Shield** | Security, auth, hardening | `role-security.md` | `/role-security` |
| 6 | **SysOps Sentinel** | Server, deployment, backups | `role-sysops.md` | `/role-sysops` |
| 7 | **Data Weaver** | Data migrations, imports | `role-data.md` | `/role-data` |
| 8 | **Vault Guardian** | Git, backups, recovery | `role-backup.md` | `/role-backup` |

### 4.2 Verification
- Confirm each workflow file exists in `.agent/workflows/`
- Report any missing files as 🔴

### 4.3 Output Format
```markdown
| # | Agent | Status |
|---|-------|--------|
| 1 | JARVIS | 🟢 ONLINE |
| 2 | Frontend Architect | 🟡 STANDBY |
| ... | ... | ... |
```

---

## Phase 5: Executive Summary & Recommendations

**Goal**: Deliver a concise, actionable morning briefing.

### 5.1 Git Status
// turbo
```powershell
git status --short
git log --oneline -5
git branch --list
```

Report:
- Current branch + HEAD commit
- Working tree status (clean/dirty/unstaged)
- Branch list with active branch highlighted

### 5.2 Environment Sync Assessment
Compare local vs dev vs prod:
- Are they on the same commit? If not, how many commits ahead/behind?
- Any undeployed features on local?
- Any pending merges?

### 5.3 Risk Flags
Check and flag:
- ⚠️ Disk space (C: drive was 96% used as of Mar 3)
- ⚠️ Container health (any containers restarting frequently?)
- ⚠️ Pending deployments (features built locally but not pushed)
- ⚠️ Stale branches (feature branches older than 2 weeks)

### 5.4 Recommendations
Provide a prioritized list:
1. **Immediate** — things that need attention now (containers down, servers unreachable)
2. **Today** — suggested priorities based on pending items from daily logs
3. **Deferred** — maintenance items (disk cleanup, branch pruning, etc.)

### 5.5 Final Output
Deliver the complete startup report to the user via `notify_user`, including:
- Server status table (Phase 1)
- Agent roll call table (Phase 4)
- "Where We Left Off" narrative (Phase 3)
- Git + sync status (Phase 5.1–5.2)
- Risk flags (Phase 5.3)
- Prioritized recommendations (Phase 5.4)

Close with: *"JARVIS Startup Protocol: COMPLETE ✅ — Awaiting orders."*

---

## Daily Log Creation

After the startup report is delivered and the user provides direction, create today's daily log using the template at [`.agent/DAILY_LOG_TEMPLATE.md`](file:///c:/Users/Aaron/spmo-suite%20-%20Copy/.agent/DAILY_LOG_TEMPLATE.md) and save it to the KI daily logs directory as `DAILY_LOG_YYYY_MM_DD.md`.

---

## Protocol History
| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-23 | Original 4-step session start in `JARVIS_LOCK_ENFORCEMENT.md` |
| 1.1 | 2026-02-12 | First formal startup report (`01_JARVIS_STARTUP_REPORT.md`) |
| 2.0 | 2026-03-04 | Unified 5-phase protocol (this document) |
| **2.1** | **2026-03-19** | **Added Execution & Assumption Guardrails to Phase 2.4 Confirmation** |
