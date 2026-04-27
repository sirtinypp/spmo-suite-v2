# DEPLOY.md
**The Deployment & Maintenance Protocol**
**Goal: Ensure Zero-Downtime releases and long-term application health.**

## Phase 1: The Final Gate (Pre-Deployment)
- **Validation:** Run the production build command locally (`npm run build`, `collectstatic`, etc.). No deployment if the build fails.
- **Sync:** Verify that the Production Environment Variables match the local `.env.local`.
- **Migration Audit:** Test database migrations locally against a copy of production data. Destructive migrations (dropping columns) are strictly forbidden without an explicit backup.

## Phase 2: The Push (The Execution)
- **Deployment Ritual:** Use atomic deployment tools (Vercel, Docker, etc.) whenever possible.
- **Maintenance Overlay:** If a deployment takes > 30 seconds, trigger a "System Updating" overlay for users.
- **Asset Integrity:** Verify that static files (images, CSS) are correctly served from the CDN/Edge.

## Phase 3: The Panic Button (Rollback Strategy)
- **Rule:** Never deploy without a confirmed rollback path.
- **Procedure:** Define the exact command or dashboard action to revert to the previous "Known Good" version in < 60 seconds.
- **Database Rollback:** Maintain a pre-deployment DB snapshot for emergency restoration.

## Phase 4: Post-Deployment Smoke Test
- **Manual Verification:** The agent must visit the live URL and verify:
    1. Login/Auth flows still work.
    2. Critical "Writes" (Forms/Submissions) succeed.
    3. AI features respond without latency spikes.
- **Log Watch:** Monitor production logs for 10 minutes post-push for any surge in `500 errors`.

## Phase 5: Long-Term Maintenance
- **Log Rotation:** Ensure system logs don't exhaust server disk space.
- **Security Patching:** Monthly audit of dependencies (`npm audit`) to apply security patches to the live app.
- **Health Checks:** Periodic "Pulse Checks" to ensure the database and APIs are responsive.

**Protocol: A deployment is not complete until the Smoke Test is passed and logs are clean.**
