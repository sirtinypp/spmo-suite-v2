# 🔒 INFRASTRUCTURE LOCK POLICY
**Version:** 1.0
**Ratified:** 2026-01-29 07:36 PHT
**Guardian Agent:** SysOps Sentinel
**Oversight:** JARVIS (Prime Orchestrator)

---

## 🎯 PURPOSE
This policy establishes immutable control over critical server infrastructure files to prevent unintended routing regressions, network misconfigurations, and domain interchange incidents.

---

## 🛡️ PROTECTED FILES (TIER 1 LOCK)
The following files are **LOCKED** and may NOT be modified without explicit USER authorization:

### 1. `docker-compose.yml`
**Location:** `~/spmo_suite/docker-compose.yml`
**Protects:** Container definitions, network topology, service names, port mappings, environment variables.
**Current State Hash:** *(To be calculated post-backup)*

### 2. `nginx/conf.d/default.conf`
**Location:** `~/spmo_suite/nginx/conf.d/default.conf`
**Protects:** Domain routing (`server_name`), proxy targets (`proxy_pass`), media aliases.
**Current State Hash:** *(To be calculated post-backup)*

---

## 📋 CHANGE CONTROL PROTOCOL

### Step 1: Request Identification
Any agent wishing to modify a TIER 1 LOCKED file MUST:
1. Identify the specific change required
2. Justify the necessity (bug fix, feature, security)
3. Document the expected impact

### Step 2: JARVIS Evaluation
JARVIS will:
1. Validate the change request against system stability
2. Identify potential conflicts or regressions
3. Prepare a Change Impact Report

### Step 3: USER Authorization
JARVIS will:
1. **Notify the USER** via `notify_user` with the Change Impact Report
2. **BLOCK all execution** until explicit USER approval
3. Document the USER's decision (APPROVED / REJECTED / DEFERRED)

### Step 4: Execution (If Approved)
SysOps Sentinel will:
1. Apply the change
2. Create a Git commit with tag `config-lock-exception-[DATE]`
3. Verify system stability
4. Update the Infrastructure Lock with new file hashes

---

## ⚠️ VIOLATION PROTOCOL
If any agent modifies a TIER 1 LOCKED file without authorization:
1. **IMMEDIATE HALT** of all operations
2. **JARVIS ESCALATION** to USER
3. **AUTOMATIC ROLLBACK** to last known-good state
4. **INCIDENT LOG** created and filed

---

## 🔐 LOCK ENFORCEMENT
- **Guardian:** SysOps Sentinel monitors file integrity
- **Oversight:** JARVIS intercepts change requests
- **Audit:** All changes logged in `infrastructure_change_log.md`

---

## ✅ EXCEPTION TRIGGERS (Automatic Lock Override)
None. ALL changes require USER approval.

---

**Lock Status:** 🟢 ACTIVE
**Last Verified:** 2026-01-29 07:36 PHT
