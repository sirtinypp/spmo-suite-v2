# STARTUP.md
**The Daily Boot Protocol**
**Goal: Establish environmental parity and recover mission context.**

## Phase 1: Internalization
1. **Read AGENTS.md:** Re-align mindset to the Surgical Execution Protocol.
2. **Read Project Context:** Review `.env.local`, `package.json`, or `requirements.txt` to confirm the stack.

## Phase 2: Context Recovery
1. **Review Daily Logs:** Read the last 3-5 entries in `daily_logs/` to understand the current "battlefield."
2. **Audit Workspace:** Run `ls -R` (or equivalent) on key directories (`src/`, `app/`, `models/`) to refresh filesystem memory.
3. **Check Git Status:** Confirm branch synchronization and identify any uncommitted "ghost" changes.

## Phase 3: Environment Validation
1. **Verify Services:** Check database connectivity and start the local development server.
2. **Check Port Shifts:** Confirm the exact URL/port where the app is running.

## Phase 4: The Startup Report
Present a brief report to the user including:
- **Executive Summary:** 1-paragraph summary of the current project state.
- **System Status:** Server port, DB status, Git branch.
- **Continuation Plan:** List of pending tasks from the previous session.
- **Initial Proposal:** The immediate next step to be taken.

**DO NOT proceed with code changes until the Startup Report is delivered.**
