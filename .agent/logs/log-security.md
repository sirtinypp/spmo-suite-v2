# Log: Security Shield

## Historical Background (Synthesized from History)
The Security Shield has focused on remediating vulnerabilities found during DAST scans and ensuring administrative access across the suite.

### Key Milestones
- **Superuser Sync (Jan 2026)**: Successfully synchronized `grootadmin` credentials across GAMIT, SUPLAY, LIPAD, and Hub databases.
- **DAST Remediation (Jan 13, 2026)**: Hardened Django `settings.py` for all apps.
    - Enforced `SECURE_SSL_REDIRECT = True` (in prod).
    - Enabled `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE`.
    - Configured HSTS (Strict-Transport-Security) headers.
- **CSRF Configuration**: Resolved `DisallowedHost` and CSRF failures by correctly configuring `CSRF_TRUSTED_ORIGINS` for remote deployment subdomains.
- **Agent System Protocol (Jan 22, 2026)**: Joined the Security Shield division under JARVIS oversight.

### Security State
- **HTTPS**: Ready but pending SSL certificate installation on Nginx.
* **Credentials**: Centralized superuser access established.
- **Headers**: Production-ready security headers implemented.

### Recent Operations
- **Session Timeout Analysis (Jan 23, 2026 @ 14:43 PHT)**:
  - **Issue**: Staff tester unable to login after logout in SUPLAY
  - **Root Cause**: Inconsistent timeout configurations across apps
  - **Current State**:
    - Hub: 2 weeks (Django default) ❌ Too long
    - GAMIT: 2 minutes ❌ Too short
    - LIPAD: 30 minutes ✅ Acceptable
    - SUPLAY: 50 minutes ⚠️ Moderate
  - **Proposed Solution**:
    - Hub: 30 minutes (informational)
    - GAMIT: 60 minutes (transactional)
    - LIPAD: 45 minutes (booking workflows)
    - SUPLAY: 60 minutes (requisitions)
  - **Additional Feature**: Auto-logout warning system
    - Warning modal 5 minutes before timeout
    - User can extend +5 minutes
    - Auto-logout after 1 minute if no response
  - **Status**: Proposal created, awaiting user approval

- **Session Timeout Implementation (Jan 23, 2026 @ 14:57 PHT)**: ✅ **COMPLETED**
  - **User Decision**: Uniform 10-minute timeout across all apps
  - **Backend Changes**:
    - Hub: 600 seconds (added, was Django default 2 weeks)
    - GAMIT: 600 seconds (changed from 120 seconds)
    - LIPAD: 600 seconds (changed from 1800 seconds)
    - SUPLAY: 600 seconds (changed from 3000 seconds)
  - **Configuration**: All apps set to `SESSION_COOKIE_AGE = 600` with `SESSION_SAVE_EVERY_REQUEST = True`
  - **Behavior**: Timer resets on any activity, 10 minutes of inactivity triggers warning
  - **Frontend Integration**: Coordinated with Frontend Architect for warning modal
  - **Status**: Backend configuration complete, awaiting frontend implementation and testing
- **Cart Security Hardening (Jan 27, 2026)**: ✅ **COMPLETED**
  - **Issue**: Users could bypass monthly limits by manually updating cart quantities or forcing checkout.
  - **Implementation**: 
    - Created `check_monthly_allocation` as a central security gatekeeper.
    - Patched `update_cart` to block unauthorized quantity increases.
    - Patched `checkout_init` as a final server-side validation before order creation.
  - **Verification**: Confirmed via `test_cart_security.py` that both loopholes are closed.
  - **Status**: Backend security hardened for all purchasing workflows.
