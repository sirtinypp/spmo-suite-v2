## [Unreleased] - 2026-03-10

### Added
- **Infrastructure**: Successfully migrated **32.8 GB** of Docker WSL2 data from `C:` to `D:` drive, reclaiming **~37 GB** of space on the system drive.
- **GAMIT**: Implemented **Scenario D: CSV-Label Alignment** for asset filtering. Dropdowns now use "Pretty Labels" (e.g., "ICT Equipment") to match database records imported from CSV.
- **Protocol**: Formalized the **Pre-Deployment Simulation Protocol (PDSP)** to verify template syntax and logic before staging deployment.

### Fixed
- **GAMIT**: Hidden "Middle Name" from UI, forms, and templates to clean up display (e.g., matching "None" removal). Model field remains for DB stability.
- **GAMIT**: Resolved `AttributeError: 'Asset' object has no attribute 'assigned_office'` by removing legacy field references in `views.py` and `asset_add.html`.
- **GAMIT**: Updated PPE Category and Asset Type labels to use "&" instead of "and" (e.g., "Furniture & Fixtures"), including a typo fix.
- **GAMIT**: Resolved literal template rendering of `{{ total_count_all }}` and other variables by rejoining split tags in `asset_list.html` and `dashboard.html`.

## [Unreleased] - 2026-03-09

### Fixed
- **GAMIT**: Resolved persistent `TemplateSyntaxError` by refactoring `query_transform` tag and moving sorting URL logic to `views.py`.
- **GAMIT**: Rejoined split template tags in `asset_list.html` to ensure single-line compliance for Django parser.
- **GAMIT**: Aligned Dashboard KPI logic to use `SERVICEABLE` instead of `ACTIVE` to match model status choices.

### Maintenance & Optimization
- **Static Code Analysis**: Ran `flake8` on all services. Identified consistent style violations (PEP 8). Use of a formatter is recommended.
- **Dependency Audit**: Ran `pip-audit`. Identified missing system dependencies (`libcairo2-dev`) required for `suplay_app` PDF generation.
- **Baseline Tests**: Created baseline unit tests (`test_basics.py`) for `spmo_website`, `gfa_app`, and `suplay_app`.
- **Docker Optimization**: Optimized Dockerfiles (added `PYTHONDONTWRITEBYTECODE`, cleaned up apt lists, added `--no-install-recommends`).
- **Configuration**: Updated `suplay_app` settings to allow local testing with SQLite fallback.

### Critical Findings
- **Missing GAMIT Code**: The `gamit_app` directory is empty. Source code recovery is required.

### Added
- **GAMIT**: Implemented dynamic column sorting (ASC/DESC) for Property No., Name, Category, Type, Status, and Department.
- **GAMIT**: Added "Results per Page" selector (10, 20, 50, 100) to the Asset Inventory.
- **GAMIT**: Implemented automated `item_id` generation in `Asset.save()` (format: `AST-YYYY-XXXXXX`).

## [Unreleased] - 2026-03-07

### Fixed
- **GAMIT**: Resolved `UnicodeDecodeError` during bulk CSV import by implementing an encoding fallback chain (`utf-8`, `utf-8-sig`, `cp1252`, `latin-1`).
- **GAMIT**: Fixed requestor display in `batch_detail.html` to use username when full name is missing.

### Added
- **GAMIT**: Enhanced "Add Asset" form with refined labels, help texts, and field logic for `image_condition`.
- **Scripts**: Polished `daily_startup.ps1` with improved terminal feedback and color-coded status reporting.

## [v1.1.0] - 2026-01-16

### Major Changes
- [Added] **News Archive**: Dedicated searchable archive page with filters for Category, Year, and Keywords.
- [Added] **Database Schema**: Added `InspectionSchedule` model and `AuditableModel` abstract base class.
- [Added] **UI Overhaul**: Implementation of Government Standard Masthead and Landing Page layout.
- [Added] **CMS Features**: Dynamic "News" and "Inspection Calendar" widgets powered by Django models.
- [Refactor] **Layout**: Restructured Landing Page (Apps > News > Services > Charter) with sticky nav anchors.

### Minor Changes
- [Fixed] **Routing**: Updated internal app links to use `*.sspmo.up.edu.ph` domains.
- [Updated] **Content**: Refined "About Us" and Footer text to reflect new SSPMO mandate.
