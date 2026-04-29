# DEPLOY.md
**The Surgical Deployment Protocol (SDP)**
**Version**: 2.0.0
**Goal**: Ensure zero-downtime releases, zero data disruption, and rapid UI/UX updates from Local to Dev/Production servers.

This protocol dictates the strict "Code flows UP, Data flows DOWN" philosophy.

---

## Phase 1: Local Pre-Flight (The Sandbox Validation)
*Never deploy untested code. The local environment must be pristine.*
1. **Syntax Audit**: Run `python manage.py check` to verify Django health.
2. **Asset Compilation**: Run `python manage.py collectstatic --noinput` to ensure CSS/JS assets are properly bundled.
3. **Template Verification**: Ensure all HTML templates have their `{% load static %}` tags and no split tags (single-line compliance).

## Phase 2: Atomic Commit (The GitKraken Stage)
*Avoid "Catch-All" commits. Target only what was surgically altered.*
1. **Review**: Open GitKraken. Audit "Unstaged Changes".
2. **Stage**: Select ONLY the specific `.html`, `.py`, or `.css` files modified in the session. Do NOT stage local database dumps (`.sqlite3`) or `.env` files.
3. **Commit**: Use the standard semantic commit format:
   - `feat(gamit): [Description of UI/logic upgrade]`
   - `fix(hub): [Description of bug resolution]`

## Phase 3: The Push (Code Only)
*Push the logic, preserve the remote data.*
1. **Push**: Execute the Push in GitKraken to the target branch (e.g., `feature/suplay-core-expansion` or `main`).
2. **Data Preservation Guarantee**: Because no local database files or destructive migrations are pushed, the active test data on the Dev/Production server remains 100% intact.

## Phase 4: Server Sync & Cache Purge (The Execution)
*Apply the code to the live environment instantly.*
1. **Pull**: SSH into the target server (Dev/Prod) and pull the latest Git changes. *(If using a CI/CD pipeline, confirm the webhook triggered successfully).*
2. **Migrate (If Applicable)**: If `models.py` was altered, run `docker-compose exec gamit_app python manage.py migrate`.
3. **Cache Purge**: Django caches templates in memory. To force the new UI to load, restart the application container:
   - `docker-compose restart gamit_app` (or respective app container).

## Phase 5: Post-Deployment Smoke Test
*Trust, but verify.*
1. **Visual Confirmation**: The deploying agent/user must visit the live URL (e.g., `https://gamit-sspmo-dev.up.edu.ph/`).
2. **Hard Refresh**: Press `Ctrl + Shift + R` to bypass local browser caches.
3. **Critical Path Check**: 
   - Verify the newly modified UI renders correctly.
   - Test one "Write" action (e.g., submitting a dummy form or applying a filter) to ensure backend views are stable.
   - Verify the Activity Log/Audit Trail captured the action.

**Protocol Status**: A deployment is only considered COMPLETE when the Smoke Test is passed. If 500 Errors occur, immediately initiate the Panic Button protocol.

## Phase 6: The Panic Button (Rollback Strategy)
*Never deploy without a confirmed escape route. The current state is your anchor.*
1. **Locking the Anchor**: Before pushing to Dev/Prod, create a Tag in GitKraken (e.g., `v1.2.0-stable`) on your final pre-deployment commit. This designates the "Known Good" state.
2. **Emergency Revert**: If the Smoke Test fails (Phase 5), immediately open GitKraken or SSH into the server.
3. **The Rollback Command**: 
   - Execute `git reset --hard v1.2.0-stable` (or your anchor tag/commit hash).
4. **Cache Purge**: Restart the application container immediately (`docker-compose restart gamit_app`) to flush the broken code from memory.
5. **Post-Mortem**: Once the system is stabilized back to the anchor state, download the error logs (`docker logs app_gamit > error.log`) to diagnose the failure locally. Do NOT attempt to debug live on the server.
