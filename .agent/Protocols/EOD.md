# EOD.md
**The Sunset & Archival Protocol**
**Goal: Persist learnings and secure the day's work.**

## Phase 1: Performance Review
1. **Review Status:** Compare the day's output against the morning's objectives.
2. **Identify Deltas:** What was accomplished? What was deferred? Why?

## Phase 2: Long-Term Memory (Knowledgebase)
1. **Update knowledgebase.md:**
    - **Successful Fixes:** Document non-obvious solutions or specific SDK quirks.
    - **Failed Executions:** Log the "Gotchas" and "Dead Ends" to prevent future agents from repeating them.
    - **Architectural Notes:** Document any new patterns established during the session.

## Phase 3: Session Archival
1. **Final Daily Log:** Ensure the entry in `daily_logs/` for today is comprehensive.
2. **Summary:** Provide a 3-bullet point summary of the session.

## Phase 4: Final Gating
1. **Commit/Push Check:** Ask the user: *"Should I commit and push these changes to the server?"*
2. **Final Go Signal:** **NEVER** terminate the session or perform final git actions without an explicit "Go Signal."
3. **Sign-off:** Once approved, greet the user professionally and terminate.

**Protocol strictly enforced: No "silent" commits or unlogged learnings.**
