# ⚡ Execution Standard: The Surgical Protocol
**Version**: 1.0.0  
**Effective**: 2026-04-15  
**Authority**: Executive Directive  
**Status**: MANDATORY — Gold Standard for all task execution

---

## Mission Statement

Every task — no matter how small — is executed with the discipline of a surgical operation. No wasted motion, no collateral damage, no surprises. The goal is not just to complete the task, but to complete it in a way that the user never has to worry about what might break.

---

## The 5-Phase Execution Pipeline

### Phase 1: BRAINSTORM
**"What are we actually solving?"**

- Clarify the user's intent. Ask if ambiguous — never assume.
- Explore options and tradeoffs openly with the user.
- Present choices as clear, labeled options (Option A / Option B) with pros and cons.
- Let the user make the strategic decision. The agent proposes, the user disposes.

**Output**: A shared understanding of WHAT we're building and WHY.

---

### Phase 2: ANALYZE
**"What does the battlefield look like?"**

- Map every file that will be touched.
- Map every file that will NOT be touched (scope lock).
- Trace all references and dependencies (grep for URL names, template tags, imports, redirects).
- Identify the blast radius of every change.

**Rules**:
- Read before you write. Always.
- If a file has 50 references, find all 50 before proposing a rename.
- If you don't know the full picture, you're not ready to execute.

**Output**: A complete file-level change map.

---

### Phase 3: ANTICIPATE
**"What could go wrong?"**

- For every change, ask: "What breaks if this fails?"
- Check for:
  - Naming collisions (URL names, template blocks, CSS classes)
  - Import chain breakage
  - Redirect loops
  - Template tag corruption (see `TEMPLATE_TAG_PREVENTION.md`)
  - Database schema drift (does this need a migration?)
  - Encoding corruption (never use PowerShell `Set-Content` on templates)
- Document risks and mitigations in the implementation plan.

**Rules**:
- Accidents are unacceptable. Period.
- If you can't prove it won't break, you're not ready to execute.
- Every risk must have a mitigation or rollback path.

**Output**: A risk checklist with zero unaddressed items.

---

### Phase 4: EXECUTE
**"One shot. Clean."**

- Write all changes in parallel when files are independent.
- Never modify the same file in parallel.
- Use additive patterns over destructive ones:
  - ADD a new view, don't rewrite the existing one.
  - ADD a new URL path, don't rename the old one.
  - ADD a new template, don't gut the existing one.
- Keep the diff minimal. If a 3-line change achieves the goal, don't write 30 lines.
- No speculative code. Every line must serve the stated objective.

**Token Economy**:
- Be swift. Don't narrate what you're about to do — just do it.
- Don't read the same file twice unless the content has changed.
- Batch independent operations into parallel tool calls.
- If a verification loop fails twice, STOP. Report to user. Don't spiral.

**Rules**:
- Zero tolerance for "I'll fix that in the next commit."
- The first execution IS the final execution.
- If unsure about a line of code, verify before writing — not after.

**Output**: Clean diffs. No regressions. No follow-up fixes.

---

### Phase 5: VERIFY
**"Prove it works."**

- Run `manage.py check` (or equivalent) immediately after changes.
- Verify imports resolve.
- Verify URL routing resolves.
- Confirm existing functionality is unbroken (redirects, links, template references).
- Report results concisely: ✅ or ❌ with specifics.

**Rules**:
- Never tell the user "it should work." Prove it.
- If verification fails, fix immediately — don't move on.
- Pre-existing warnings (e.g., allauth deprecations) are acknowledged but not confused with new errors.

**Output**: Verified, working code. Ready for presentation.

---

## Behavioral Principles

### 1. Precision Over Speed
Fast is good. Correct is mandatory. Never sacrifice correctness for velocity.

### 2. Additive Over Destructive
Prefer creating new files/functions alongside existing ones. This preserves rollback paths and eliminates reference breakage.

### 3. Token Modesty
Respect the user's time and token budget:
- Don't over-explain what you're about to do. Execute and summarize.
- Don't re-read files you've already analyzed in this session.
- Don't generate implementation plans for trivial changes (< 10 lines).
- Do generate plans for structural changes (new views, new models, multi-file edits).

### 4. Scope Lock
Define what you WILL NOT touch before you start. This is non-negotiable. Scope creep during execution is the #1 cause of regressions.

### 5. The "Presentation Test"
Before marking any task complete, ask: "Would I be confident showing this live in a presentation right now?" If the answer is anything less than an absolute yes — you're not done.

---

## When to Apply This Standard

| Scenario | Apply Full Pipeline? |
| :--- | :--- |
| Structural change (new views, URL rewiring, model changes) | ✅ All 5 phases |
| Multi-file edit (3+ files) | ✅ All 5 phases |
| Single-file bug fix (< 10 lines, clear root cause) | Phases 4-5 only (Execute + Verify) |
| Cosmetic/text change (typo, label rename) | Phase 4 only (Execute) |
| User says "brainstorm first" | ✅ Phases 1-3, then pause for approval |
| User says "just do it" | Phases 2-5 (silent analysis, then execute) |

---

## Anti-Patterns (Strictly Forbidden)

| ❌ Anti-Pattern | ✅ Correct Approach |
| :--- | :--- |
| "Let me try this and see if it works" | Analyze first. Know it will work before writing. |
| Modifying 8 files when 3 would suffice | Minimize blast radius. |
| Renaming a URL name used in 20 templates | Keep the old name. Add an alias if needed. |
| Writing a 200-line view when 80 lines is sufficient | Be concise. Every line earns its place. |
| Running into an error loop and trying 5 variations | Stop after 2 failures. Report to user. |
| Explaining for 3 paragraphs what you're about to do | Summarize in 3 bullet points, then execute. |
| Asking the user "should I verify?" | Always verify. It's not optional. |

---

## Protocol History
| Version | Date | Changes |
| :--- | :--- | :--- |
| 1.0 | 2026-04-15 | Initial codification based on the Transaction History implementation session |
