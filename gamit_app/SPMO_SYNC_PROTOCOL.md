# SPMO Suite: "Sync-First" Operational Protocol
**Version:** 1.0 (Institutionalized May 2026)
**Objective:** Maintain 1:1 environment parity and zero-drift deployment across Local, DEV, and PROD servers.

---

## 🚀 1. The Core Methodology: "Atomic Parity"
Every task must adhere to the **Atomic Parity** rule: No feature is considered "Done" until it is successfully synchronized and verified across all three environments.

### A. Pre-Flight Check (The Audit)
Before modifying code:
1. Run parity audit scripts (e.g., `_audit_workflows.py`) to confirm Local matches DEV/PROD.
2. Verify registry consistency (9-user baseline).

### B. Execution & Deployment
1. **Develop Local:** Build and test the feature in the local container.
2. **Commit & Tag:** Use descriptive commit messages. Create a stable tag (e.g., `v1.x-feature-name`) for critical milestones.
3. **Triggered Sync:** Immediately execute the deployment sequence:
   - `git push origin main`
   - `ssh DEV -> git pull && docker restart`
   - `ssh PROD -> git pull && docker restart`

### C. Post-Deployment Validation
1. Verify the changes are live on the remote servers.
2. Perform a "Smoke Test" (e.g., check `DEBUG` status, verify manual login).

---

## 🛡️ 2. Hardened Infrastructure Standards
*   **Identity:** Always use the dedicated Manual Login path for operational testing.
*   **Security:** `DEBUG=False` must be enforced on PROD at all times.
*   **Registry:** Maintain a strict "Source of Truth" for users. Any unauthorized accounts must be purged immediately.

---

## 🛠️ 3. Command Reference
| Goal | Command Pattern |
| :--- | :--- |
| **Sync All** | `git push && ssh DEV restart && ssh PROD restart` |
| **Rollback** | `git checkout <TAG_NAME> && git push -f` |
| **Audit** | `python _audit_workflows.py` |

---

## 📋 4. Institutional Integration
This protocol is a **MANDATORY** reference during every **Startup Protocol** execution. JARVIS/Antigravity must load this context at the beginning of every session to ensure methodology continuity.

---
*Created by Antigravity AI for the SPMO Suite Platform.*
