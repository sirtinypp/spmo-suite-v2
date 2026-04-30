# DEPLOYMENT REGISTRY
**SPMO Suite — Comprehensive Deployment & Rollback Anchor Log**  
**Last Updated:** April 30, 2026 — 12:06 PM PHT

> [!IMPORTANT]
> This is the single source of truth for all deployment anchors across DEV and PROD.  
> To rollback: `git reset --hard <tag-name>` → `docker restart <container>`

---

## Active Gold State

| Property | Value |
|---|---|
| **Tag** | `stable-branding-2026-04-30` |
| **Commit** | `1334a46` |
| **Date** | April 30, 2026 |
| **Description** | Institutional branding (UP Logo + Full Title) + Chunked Bulk Media Uploads with Progress Bar. |
| **Environments** | LOCAL ✅ · DEV ✅ · PROD ✅ |

---

## Deployment History

### April 2026

| # | Tag | Commit | Date | Target | Description |
|---|---|---|---|---|---|
| 1 | `stable-branding-2026-04-30` | `1334a46` | Apr 30 | DEV + PROD | Institutional branding refactor + Chunked Bulk Uploads verified |
| 2 | `golden-stable-2026-04-30` | `235da8b` | Apr 30 | DEV + PROD | Gold State — Bulk Media Manager, Persona Switcher, production-hardened settings |
| 3 | `v2.2.0-presentation-stable` | `9b2a993` | Apr 30 | LOCAL | Institutional Audit Interface Hardening — Final Stabilization |
| 4 | `pre-dev-deployment-apr29` | `15ea07c` | Apr 29 | LOCAL | Pre-deployment anchor — Action Center & Command Center UX |
| 5 | `stable-pre-mirror` | `9ff74e8` | Apr 29 | LOCAL | Stable baseline before Dev-to-Local DB mirroring |

### March 2026

| # | Tag | Commit | Date | Target | Description |
|---|---|---|---|---|---|
| 5 | `checkpoint-2026-03-24-eod` | `d1108af` | Mar 24 | LOCAL | PAR v2, workflow timeline fix, transaction nav routing |
| 6 | `checkpoint-2026-03-12-eod` | `f87e785` | Mar 12 | LOCAL | Unified Menu & Workflow Research |
| 7 | `golden-gamit-stable-2026-03-10-v2` | `9710f70` | Mar 10 | DEV + PROD | fix_labels management command for case-insensitive DB sync |
| 8 | `golden-gamit-stable-2026-03-10` | `e150446` | Mar 10 | DEV + PROD | CHANGELOG update for stabilization and label polish |
| 9 | `checkpoint-gamit-staging-sync-2026-03-09` | `85b88fc` | Mar 9 | DEV | GAMIT staging synced with fresh standard PAR data imported |
| 10 | `golden-gamit-stable-2026-03-09` | `9f01003` | Mar 9 | DEV + PROD | Stabilized GAMIT templates and standardized choices |
| 11 | `gamit-inventory-stabilized-2026-03-09` | `6453dfb` | Mar 9 | DEV | Stabilized GAMIT Asset Inventory with sorting and pagination |
| 12 | `golden-sso-v1` | `a5c438e` | Mar 2 | DEV + PROD | Google SSO integrated & verified across all 4 apps |
| 13 | `v2.2.0-sso` | `2ff54a2` | Mar 2 | DEV + PROD | Release v2.2.0 — Google SSO Integration |
| 14 | `v2.2.0` | `f51a8c6` | Mar 2 | DEV + PROD | Release v2.2.0 — Google SSO Integration |

### February 2026

| # | Tag | Commit | Date | Target | Description |
|---|---|---|---|---|---|
| 15 | `sso-stable-locked` | `7e5703b` | Feb 26 | LOCAL | Hard lock — Local Google SSO working perfectly |
| 16 | `checkpoint-google-sso-bypass-2026-02-26` | `e0702b9` | Feb 26 | LOCAL | Intermediary login bypassed, direct Google OAuth active |
| 17 | `checkpoint-google-sso-2026-02-26` | `71d4445` | Feb 26 | LOCAL | Google SSO integration complete, pending live test |
| 18 | `stable-vapt-plus-suplay-fix-2026-02-25` | `358199e` | Feb 25 | DEV + PROD | SUPLAY search fix + LIPAD template recovery + KB reorganization |
| 19 | `stable-vapt-remediated-2026-02-25` | `e82218f` | Feb 25 | DEV + PROD | Stable checkpoint after VAPT remediation and health checks |
| 20 | `v2.1.0-prod-final` | `8803aee` | Feb 12 | PROD | Emergency rollback protocol updated to v1.4.0 |
| 21 | `v1.4.0-stable-parity` | `290babe` | Feb 12 | DEV + PROD | Latest stable checkpoint — CSRF sync fix |
| 22 | `v1.2.0-stable` | `6ca3f5c` | Feb 5 | PROD | Official Production Release v1.2.0 — Verified & Hardened |
| 23 | `checkpoint-local-v1.3.1` | `b8c658e` | Feb 3 | LOCAL | Local state with GAMIT fix |
| 24 | `lipad-polish-pre-deploy-202602030930` | `ae2d75c` | Feb 3 | DEV | LIPAD unified Django tags fix |
| 25 | `prod-hub-pre-deploy-202602030756` | `fb2fc0c` | Feb 3 | PROD | Unified anchor IDs and synced navigation menus |
| 26 | `stable-2026-02-02-hub-production` | `df5c307` | Feb 2 | PROD | Hub deployed with correct leadership images and formatting |
| 27 | `stable-2026-02-02-safety-lock` | `e531f38` | Feb 2 | PROD | Verified production nginx routing configuration lock |
| 28 | `stable-2026-02-02-session-start` | `b7cb1cf` | Feb 2 | ALL | Initial commit — SPMO Suite v2 Stable Baseline |

### January 2026

| # | Tag | Commit | Date | Target | Description |
|---|---|---|---|---|---|
| 29 | `lipad-ui-fix-v1.1` | `4a48cd3` | Jan 30 | DEV | Stable LIPAD Release — Form Fixes |
| 30 | `stable-2026-01-30-lipad-ui-polish` | `05ce593` | Jan 30 | DEV | LIPAD polish — UP Logo in form header + landing page |
| 31 | `stable-2026-01-30-lipad-security-hardening` | `d450efd` | Jan 30 | DEV + PROD | LIPAD P0 hardening — SECRET_KEY to env var, DEBUG default False |
| 32 | `stable-2026-01-30-pre-lipad-revamp` | `2206a46` | Jan 29 | LOCAL | Finalize GAMIT acronym update |
| 33 | `gamit-dashboard-final-v2.0` | `7adf183` | Jan 29 | DEV + PROD | GAMIT Dashboard v2.0 — Complete and Verified |
| 34 | `gamit-dashboard-v2.0` | `e77ed7e` | Jan 29 | DEV | JARVIS Daily Role Anchor and Startup Protocol |
| 35 | `stable-2026-01-29-security-hardening` | `85cf362` | Jan 29 | DEV + PROD | Security Hardening Complete — SUPLAY + GAMIT P0 Fixes |
| 36 | `stable-2026-01-29-security-p0` | `6683389` | Jan 29 | DEV + PROD | SECRET_KEY & ALLOWED_HOSTS fixes |
| 37 | `stable-2026-01-29-suplay-fixes` | `ba27aa9` | Jan 29 | DEV | SUPLAY Media & Filter Fixes |
| 38 | `stable-post-rollback-2026-01-29` | `f642662` | Jan 29 | PROD | Post-rollback — All domains verified, Infrastructure Lock active |
| 39 | `v1.2.0-production-live` | `cc0421c` | Jan 28 | PROD | Incident recovery and SSL rollback |
| 40 | `v1.2.0-production` | `52b3cb9` | Jan 27 | PROD | SUPLAY Admin restoration and version sync |
| 41 | `v1.2.0` | `13f07a5` | Jan 27 | DEV + PROD | Latest Stable Version — Product UI and Session Refinements |
| 42 | `v1.1.0` | `5752ed8` | Jan 16 | DEV + PROD | News Archive & UI Overhaul |
| 43 | `v1.0.0` | `a9df9cb` | Jan 21 | PROD | First stable production release |

---

## Naming Convention

| Prefix | Meaning | Example |
|---|---|---|
| `golden-*` | Verified Gold State — safe for production rollback | `golden-stable-2026-04-30` |
| `v*.*.*` | Semantic version release | `v2.2.0-sso` |
| `stable-*` | Confirmed stable checkpoint | `stable-vapt-remediated-2026-02-25` |
| `checkpoint-*` | Session-level savepoint (may not be deployment-ready) | `checkpoint-2026-03-24-eod` |
| `pre-*-deployment-*` | Anchor created before a deployment push | `pre-dev-deployment-apr29` |

---

## Rollback Procedure (SDP Phase 6)

```bash
# 1. SSH into the target server
ssh -p 9913 ajbasa@<server-ip>

# 2. Navigate to the project directory
cd /home/ajbasa/spmo_suite

# 3. Reset to the desired anchor
git fetch origin
git reset --hard <tag-name>

# 4. Restart the affected container
docker restart app_gamit   # or app_hub, app_gfa, app_store

# 5. Verify
docker exec app_gamit python manage.py check
```
