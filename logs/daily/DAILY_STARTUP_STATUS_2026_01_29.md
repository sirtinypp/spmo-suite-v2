# 📋 DAILY STARTUP STATUS REPORT

**Date/Time:** 2026-01-29 07:15 PHT
**Overall Health:** 🔴 **CRITICAL INCIDENT (Domain Interchange)**
**Orchestrator:** JARVIS

---

## 1. App & Domain Status (INCIDENT DETECTED)
The system is currently experiencing a "Routing Shift." While the configuration is logically correct, the internal Docker IP mapping has drifted.

| Public Domain | Expected | **CURRENT ACTUAL** | Status |
| :--- | :--- | :--- | :--- |
| **sspmo.up.edu.ph** | SPMO Hub | **LIPAD** | 🔴 Interchanged |
| **gamit-sspmo.up.edu.ph** | GAMIT | **SPMO Hub** | 🔴 Interchanged |
| **lipad-sspmo.up.edu.ph** | LIPAD | **GAMIT** | 🔴 Interchanged |
| **suplay-sspmo.up.edu.ph** | SUPLAY | **OFFLINE** | 🔴 Broken |

**Reason:** Nginx is likely pointing to stale internal container IPs that were reassigned during the Phase 2 restart.

## 2. Filesystem & Configuration Review
- **`docker-compose.yml`:** Correct (verified service names).
- **`nginx/default.conf`:** Correct (verified proxy_pass targets).
- **Anomalies:** Discovered that despite correct config, the 1:1 mapping between Domain and App is broken at the network layer.

## 3. Server Status (172.20.3.91)
- **Uptime:** 15 days.
- **Containers:** 6/6 Running (Healthy).
- **Observation:** `app_store` (SUPLAY) is running but Nginx cannot reach it, or is reaching a dead IP.

## 4. Log & Backup Integrity
- **DB Backup:** ❌ **FAILED (0 bytes)**. We still have NO valid backup of the repaired database.
- **Git Status:** `DIRTY`. Uncommitted hardening changes.

## 5. Agent Roll Call
- **JARVIS:** Active (Orchestrating Assessment)
- **SysOps Sentinel:** Active (Diagnostic scanning)
- **All others:** Idle (Read-only)

---

## 6. Recommended Next Actions (PRIORITY LIST)
1.  **[IMMEDIATE] Fix Domain Swap & Apply Lock:**
    - Modify `docker-compose.yml` to use **Static IP addresses** (172.20.0.x) for all containers.
    - Update Nginx to route to these fixed IPs. This creates the "Lock" requested to prevent future interchanges.
2.  **[CRITICAL] Re-execute Database Backup:** Resolve the 0-byte dump immediately after routing is fixed.
3.  **[PHASE 2 RESUMPTION]** Debug Media serving (images) once routing is locked.

---
**Status:** Assessment complete. Awaiting USER authorization to apply the "Static IP Lock" and restore correct routing.
