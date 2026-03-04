---
description: JARVIS End-of-Day Protocol — session close, git audit, backup, and daily log finalization.
---

# 🌙 JARVIS End-of-Day (EOD) Protocol

**Version**: 2.0.0
**Effective**: 2026-03-04
**Trigger**: User says "end of day", "EOD", "sign off", "logging out", or invokes `/eod`
**Authority**: JARVIS (Prime Orchestrator) → delegates to Vault Guardian

---

## Overview

Execute all phases in order before user signs off. This ensures no work is lost, all changes are committed, and the daily log is finalized for tomorrow's startup review.

---

## Phase 1: Git Audit

### 1.1 Check Working Tree
// turbo
```powershell
git status
```

- If dirty → present uncommitted changes to user
- Recommend staging and committing with descriptive message
- If clean → confirm ✅

### 1.2 Review Today's Commits
// turbo
```powershell
git log --oneline --since="midnight"
```

- List all commits made today with hashes and messages
- Identify the HEAD commit for the daily log

### 1.3 Temp Script Cleanup
Check for any temporary scripts created during the session:
- `patch_*.py`, `fix_*.py`, `vcheck_*.py`, `test_*.py` in root or app directories
- Recommend deletion or archival

---

## Phase 2: Backup Check

### 2.1 Database Status
- Check if `spmo_shared_db` container is running
- Note last known backup timestamp (if available)
- Recommend DB dump if significant data changes were made today

### 2.2 Config Backup
- Verify `.env`, `docker-compose.yml`, `nginx/conf.d/default.conf` are committed
- Flag any Tier 1 file changes made today that need special attention

---

## Phase 3: Daily Log Finalization

### 3.1 Complete Today's Log
Using the template at [`.agent/DAILY_LOG_TEMPLATE.md`](file:///c:/Users/Aaron/spmo-suite%20-%20Copy/.agent/DAILY_LOG_TEMPLATE.md):

- Fill in all `## 5. ✅ Completed Today` items
- Fill in `## 6. 🔁 Pending / In Progress` items
- Add the `## 🔒 END OF DAY` block with:
  - Final git state (branch, HEAD, clean/dirty)
  - Today's commits table
  - Sign-off notes

### 3.2 Save Location
Save to KI daily logs directory:
`spmo_operational_governance/artifacts/daily_logs/DAILY_LOG_YYYY_MM_DD.md`

---

## Phase 4: Status Report

### 4.1 Final Server Check
// turbo
```powershell
docker compose ps -a --format "table {{.Name}}\t{{.Status}}"
```

### 4.2 Deliver EOD Summary
Report to user:
- ✅/❌ Git: clean/committed
- ✅/❌ Backup: DB dump status
- ✅/❌ Daily log: finalized
- ✅/❌ Servers: all environments status
- 📋 Tomorrow's suggested agenda (from pending items)

Close with: *"Vault Guardian protocol complete. Safe to log out. ✅"*

---

## Protocol History
| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-23 | Ad-hoc EOD checks in various sessions |
| **2.0** | **2026-03-04** | **Formalized 4-phase EOD protocol (this document)** |
