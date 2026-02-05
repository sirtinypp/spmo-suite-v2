# SPMO Suite v2 Changelog

## [Unreleased] - 2026-02-05

### Added
- **Gamit App**: Initialized new Django app structure (`gamit_app`) with `requirements.txt` and `Dockerfile`.
- **CI/CD**: Added GitHub Actions workflow (`.github/workflows/ci.yml`) for automated linting and testing.
- **Rollback**: Added `scripts/rollback.sh` for deployment safety.
- **Tests**:
    - Added unit tests for `spmo_website` (Home/Login).
    - Added unit tests for `gamit_app` (Admin).
    - Added booking form rendering tests for `gfa_app`.
    - Added restricted product logic tests for `suplay_app`.

### Changed
- **Security**:
    - Updated `settings.py` in all apps to use `os.environ` for secrets (SECRET_KEY, DEBUG, DB credentials).
    - Removed insecure "LOCAL DEV OVERRIDES" blocks that forced `DEBUG=True` in production.
    - Updated `suplay_app` admin logic to handle exceptions safely.
- **Docker**:
    - Optimized all Dockerfiles to use `python:3.10-slim`.
    - Implemented non-root user (`appuser`).
    - Added `libcairo2-dev` to `suplay_app` container for PDF generation.
    - Added `apt-get clean` steps to reduce image size.
- **Code Quality**:
    - Formatted entire repository with `black`.
    - Fixed UTF-16 encoding issue in `suplay_app/.gitignore`.

### Fixed
- Fixed `ModuleNotFoundError` for `django-import-export` and `xhtml2pdf` in `suplay_app`.
- Fixed `gfa_app` test failures regarding template rendering expectations.
