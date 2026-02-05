# 📑 ROLLBACK LOG: ROLLBACK-PATCH-1

**Date & Time:** 2026-01-29 07:30 PHT
**Rollback Version:** ROLLBACK-PATCH-1
**Status:** 🟡 AUTHORIZED (Pending Execution)
**Executor:** SysOps Sentinel (Under JARVIS)

---

## 1. Trigger Reason
- **Issue:** Critical Domain Interchange regression and subnet overlap outage.
- **Impact:** Production applications misrouted and partially unreachable.
- **Trigger State:** `AUTHORIZED` (by USER).

## 2. Target Identification
- **Rollback Target Commit:** `4e46b75`
- **Original Deployment Version:** Hardening Phase 2 (Experimental/Dirty)
- **Target Description:** "fix(nginx): Correct domain routing - reverse incorrect swap" (Jan 28).

## 3. Scope & Apps Affected
- **Apps:** Hub, GAMIT, LIPAD, SUPLAY.
- **Infras:** Nginx (Routing), Docker Network (Static IP removal).
- **Data:** No database rollback required. Schema is stable.

## 4. Execution Plan (Section F)
1.  `git checkout 4e46b75 -- docker-compose.yml nginx/conf.d/default.conf`
2.  `scp` configs to production server.
3.  `ssh ajbasa@172.20.3.91 "cd ~/spmo_suite && sudo docker compose down && sudo docker compose up -d"`
4.  Verification of all 4 domains.

## 5. Post-Rollback Validation
- [x] SPMO Hub (sspmo.up.edu.ph) -> Hub Home (Title: 'UP SSPMO')
- [x] GAMIT (gamit-sspmo.up.edu.ph) -> GAMIT Login (Title: 'GAMIT System')
- [x] LIPAD (lipad-sspmo.up.edu.ph) -> LIPAD Portal (Title: 'LIPAD Portal')
- [x] SUPLAY (suplay-sspmo.up.edu.ph) -> SUPLAY Home (Title: 'System SSPMO | SUPLAY')

---
**Status:** SUCCESS
*(Verified via programmatic source inspection)*
