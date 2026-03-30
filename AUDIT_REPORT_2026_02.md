# Audit Report - February 2026

## 1. Static Code Analysis (Flake8)

Performed static analysis on `spmo_website`, `gfa_app`, and `suplay_app`.
Found numerous style violations (PEP 8), primarily:
- **E261**: At least two spaces before inline comment.
- **W291/W292**: Trailing whitespace and missing newlines.
- **E302/E305**: Incorrect blank lines around functions/classes.
- **E402**: Module level import not at top of file (specifically in `gfa_app/check_form_fields.py`).
- **E501**: Line too long (ignored for now, but configured max 120).

**Recommendation**: Run a formatter like `black` or `autopep8` to automatically fix these issues.

## 2. Dependency Audit

Attempted to run `pip-audit` on:
- `spmo_website/requirements.txt`
- `gfa_app/requirements.txt`
- `suplay_app/requirements.txt`

**Result**: Automated audit failed due to missing system dependencies for building `pycairo` (required by `xhtml2pdf` in `suplay_app`).

**Manual Inspection**:
- **Django==5.2.5**: Appears to be an up-to-date version (as of 2026).
- **pillow==12.0.0**: Up-to-date.
- **psycopg2-binary**: Standard for PostgreSQL.
- **gunicorn**, **whitenoise**: Standard production servers.

**Action Item**: Ensure `libcairo2-dev` or equivalent is installed in the CI/CD environment or Docker image to allow building `xhtml2pdf` dependencies.

## 3. Missing Component: GAMIT

**Critical Finding**: The `gamit_app` directory is present but empty (contains only `.` and `..`).
- **Impact**: Cannot build the GAMIT service. Cannot run analysis or tests.
- **Action**: Locate the source code for GAMIT. It might be in a backup (e.g., `db_gamit_backup.sql` exists, but that is data, not code).

## 4. Docker Optimization

Analysis of `Dockerfile`s in `spmo_website`, `gfa_app`, `suplay_app` shows room for improvement:
- Currently using `python:3.10-slim`.
- Running as `root` (security risk).
- Dependencies installed in the same layer as build tools (larger image).
- `apt-get install` without cleanup (larger image).

**Plan**: Optimize Dockerfiles to use cleaner layer construction and reduced image size (removed caching files, set environment variables). Note: Non-root user implementation deferred to avoid conflict with development volume mounts.
