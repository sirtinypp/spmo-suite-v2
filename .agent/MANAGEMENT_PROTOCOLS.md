# 📜 JARVIS Management Protocols
**Version**: 1.0.0
**Effective**: 2026-01-27
**Status**: MANDATORY / NON-NEGOTIABLE

---

## 1. 📝 Mandatory Logging Protocol (Double-Entry Ledger)
**Rule**: Every change made by an assigned agent must be logged **twice**.

### Entry 1: Agent-Specific Log
- **Location**: `.agent/logs/[agent-role].md` (e.g., `log-sysops.md`, `log-frontend.md`)
- **Content**: Detailed technical specs, file paths, logic changes, and implementation notes.
- **Audience**: Future agents, technical audit.

### Entry 2: General Ledger (Change Log)
- **Location**: `CHANGELOG.md` (Project Root)
- **Content**: High-level summary of the feature, fix, or change.
- **Audience**: Users, stakeholders, project managers.

**Workflow**:
1. Execute Change.
2. Update `[agent-role].md`.
3. Update `CHANGELOG.md` under `[Unreleased]`.

---

## 2. 🛡️ Post-Change Stability Protocol
**Rule**: After **ANY** modification, JARVIS must **immediately** verify application stability.

### Verification Tier 1 (Light)
*For non-critical UI/Text changes*
- **Action**: Verify file syntax (e.g. `python -m py_compile`, `check_templates`).
- **Check**: Ensure no immediate crash/error logs.

### Verification Tier 2 (Standard)
*For Logic/Feature changes*
- **Action**: Run relevant test script (e.g., `test_monthly_limit.py`).
- **Check**: Confirm feature works as expected.

### Verification Tier 3 (Critical/Infrastructure)
*For Settings/Models/Docker/Nginx changes*
- **Action**: Full Health Check (`production_health_check.ps1`).
- **Check**: Verify all containers running, endpoints accessible 200 OK.

**Failure Protocol**:
- If verification fails -> **IMMEDIATE ROLLBACK** or **Emergency Fix**.
- Alert User.

---

## 3. ⚖️ Jurisdiction Control Protocol
**Rule**: Explicitly monitor agent activity to ensure no agent overlaps duties or modifies files outside their assigned scope.

### Definitions
- **See**: `.agent/AGENT_BOUNDARIES.md` for specific safe zones and forbidden actions.
- **See**: `.agent/JARVIS_LOCK_ENFORCEMENT.md` for production lock rules.

### Monitoring Process
1. **Pre-Execution**: JARVIS reviews the tool call against the active Agent's persona.
2. **Conflict Detection**:
   - IF Agent A tries to modify Agent B's file -> **HALT**.
   - IF Agent A tries to modify Locked File -> **HALT**.
3. **Resolution**:
   - Request User Approval.
   - Or Re-assign task to correct Agent.

---

**JARVIS Signature**: _Protocols Active_
