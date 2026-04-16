---
description: LIPAD Operational Protocol — enforces clean execution, pre-flight validation, and proactive risk mitigation for all LIPAD development work.
---

# LIPAD Operational Protocol

## Rule 1: No Loopholes — Validate Before Presenting

1. **Pre-flight Check**: Before reporting any feature as "done", run `python manage.py check travel` and confirm **0 errors**.
2. **Browser Smoke Test**: Load the affected page in the browser and confirm it renders without 500/404 errors.
3. **Migration Discipline**:
   - Never rename fields that have existing data without a **two-phase migration** (add new → copy data → drop old).
   - If a migration fails, **diagnose the exact SQL error** before retrying. Do not re-run blindly.
   - Always run `makemigrations` → inspect the generated file → then `migrate`.
4. **Rollback Plan**: Before destructive schema changes, note the last good migration number so we can `migrate travel <number>` to revert.

## Rule 2: Quick, Clean, Efficient Execution

1. **One-shot file writes** over iterative edits when modifying >50% of a file.
2. **Batch commands** into single `run_command` calls (e.g., `makemigrations; migrate; seed` in one line).
3. **No redundant reads** — cache file contents mentally; re-read only if >20 steps have passed.
4. **Script files for complex shell logic** — avoid multi-line PowerShell strings; write `.py` scripts, run, then delete.
5. **Minimal token updates** — use `%SAME%` for unchanged task_boundary fields.

## Rule 3: Anticipate Problems — Think 5-10 Steps Ahead

Before recommending any change, evaluate these risk vectors:

| Risk | Mitigation |
|------|------------|
| FK migration breaks existing data | Use nullable FK + data migration script, then enforce NOT NULL |
| Template references old field names | Grep all `.html` files for the old field name before renaming |
| Admin site breaks after model change | Update `admin.py` in the **same commit** as `models.py` |
| Forms crash on missing queryset | Always set `queryset` in `__init__` for FK fields |
| CSV import creates orphan records | Validate all FK lookups exist before `bulk_create` |
| Docker container uses cached code | Restart container after model changes if running in Docker |
| Views reference removed constants | Grep `views.py` for any removed constant before deleting |

### Pre-Change Checklist (Mandatory)
// turbo-all
```
1. grep all templates for affected field names
2. grep views.py + forms.py + admin.py for affected field/constant names
3. note current migration number (rollback target)
4. make the change
5. makemigrations → inspect → migrate
6. system check (0 errors)
7. browser smoke test on affected pages
8. report to user
```
