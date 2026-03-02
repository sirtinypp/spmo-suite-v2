# 🔒 APPLICATION LOCK POLICY
**Version:** 1.0
**Ratified:** 2026-01-30
**Enforcer:** JARVIS (Prime Orchestrator)
**Scope:** Application Code Preservation

---

## 🎯 PURPOSE
This policy establishes a **STRICT CODE FREEZE** on the **GAMIT** and **SUPLAY** applications. The goal is to preserve their current stable state while development resources are focused on the SPMO Hub Revamp and LIPAD Refinement.

---

## 🛡️ PROTECTED SCOPES (TIER 1 LOCK)
The following directories and all their contents are **LOCKED** and may NOT be modified without explicit USER authorization:

### 1. GAMIT Application
**Directory:** `~/spmo_suite/gamit_app/`
**Status:** ❄️ **FROZEN**
**Allowed Actions:**
- Read-only access (Assessment/Logs)
- Emergency Security Patches (Requires P0 justification)

### 2. SUPLAY Application
**Directory:** `~/spmo_suite/suplay_app/`
**Status:** ❄️ **FROZEN**
**Allowed Actions:**
- Read-only access (Assessment/Logs)
- Emergency Security Patches (Requires P0 justification)

---

## 📋 CHANGE CONTROL PROTOCOL

### Exception Criteria
Modifications are permitted **ONLY** under the following conditions:
1.  **Critical Security Vulnerability (P0):** Immediate threat to system integrity.
2.  **Production Outage:** Service is down and requires immediate remediation.

### Workflow for Exceptions
1.  **Agent Identification:** Agent detects P0 issue or Outage.
2.  **JARVIS Evaluation:** JARVIS confirms severity.
3.  **User Verification:** JARVIS requests explicit UNLOCK authorization from USER.
4.  **Execution:** Upon approval, the specific file is unlocked *temporarily* for the fix, then immediately re-locked.

---

## ⚠️ VIOLATION PROTOCOL
Any attempt by an agent (Logic, Frontend, SysOps, etc.) to modify files in the protected scopes without prior authorization will result in:
1.  **IMMEDIATE OPERATION HALT**
2.  **AUTOMATIC REVERSION** of changes.
3.  **INCIDENT REPORT** filed by JARVIS.

---

## ✅ ACTIVE STATUS
**GAMIT:** 🔒 LOCKED
**SUPLAY:** 🔒 LOCKED
**LIPAD:** 🔓 OPEN (Active Development)
**SPMO HUB:** 🔓 OPEN (Active Development)

---
*Authorized by USER Instruction - Jan 30, 2026*
