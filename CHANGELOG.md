## [Unreleased] - 2026-04-29

### Added
- **GAMIT**: Suppressed the "Return to Pool" module from the sidebar and navigation logic as it is not yet an approved process.
- **GAMIT**: Polished the "Request Inspection", "Report Loss/Damage", and "Property Clearance" headers with institutional subtitles and the "System Guide" button.
- **GAMIT**: Polished the "Transfer / Reassign" page header with a descriptive subtitle and the "System Guide" button for UI consistency.
- **GAMIT**: Polished the "Batch Acquisition" page header with a descriptive subtitle and the "System Guide" button for UI consistency.
- **GAMIT**: Polished the "Add Asset" page header with a descriptive subtitle and the "System Guide" button for UI consistency.
- **GAMIT**: Added descriptive subtitles to all 8 Dashboard KPI cards to improve user context and audit readiness.
- **GAMIT**: Optimized `sspmo-loader` to suppress itself during filters, searches, and pagination to improve UI responsiveness.
- **GAMIT**: Implemented "Search Memory" using `sessionStorage` to retain the latest search term when returning to the Asset Registry.
- **GAMIT**: Added a formal subtitle to the Asset Registry: "PAR PPE Registry — Properties valued at ₱50,000.00 and above" for institutional clarity.
- **GAMIT**: Set default sorting in the Asset Registry to **Property Number** in **Descending** order to show the latest entries first.
- **GAMIT**: Expanded the System Knowledge Base with financial terms and implemented **Category Filtering** (All, General, Property, Finance) using interactive pill buttons.
- **GAMIT**: Created a "Side-Peek" Knowledge Base Guide (Offcanvas) in the main layout for contextual terminology assistance.
- **GAMIT**: Fixed a critical bug where the `sspmo-loader` would block user clicks (e.g., Print buttons) when suppression was active.

## [Unreleased] - 2026-03-10

### Added
- **Infrastructure**: Successfully migrated **32.8 GB** of Docker WSL2 data from `C:` to `D:` drive, reclaiming **~37 GB** of space on the system drive.
- **GAMIT**: Implemented **Scenario D: CSV-Label Alignment** for asset filtering. Dropdowns now use "Pretty Labels" (e.g., "ICT Equipment") to match database records imported from CSV.
- **Verification**: Syntax check passed.

### Side-Peek Knowledge Base Relocation
- **Files**: `layout.html`, `dashboard.html`, `asset_list.html`, `asset_detail.html`
- **Logic**: Removed the floating trigger and replaced it with a subtle "System Guide" pill button beside the main page titles/breadcrumbs.
- **Rationale**: User feedback indicated the floating icon was blocking UI elements. The new placement is more integrated and official.
- **GAMIT**: Fixed alignment of the "System Guide" button in the Asset Inventory header to keep it pinned next to the title.
- **Verification**: `get_template()` check passed for all 3 templates.

### Asset Service Card Renaming
- **File**: `gamit_app/inventory/templates/inventory/asset_detail.html`
- **Logic**: Updated the button label from "Print Service Record" to "Asset Service Card".
- **Rationale**: User requested terminology alignment with "Property Card".
- **Verification**: Syntax check passed.

### Side-Peek Knowledge Base Guide
- **File**: `gamit_app/inventory/templates/layout.html`
- **Logic**: Added a fixed floating button (glossary-trigger) that toggles a Bootstrap Offcanvas drawer. The drawer contains a pre-populated glossary of 8+ institutional terms (RPCPPE, PPE, Book Value, etc.).
- **Rationale**: Provides immediate contextual help for users during the presentation and daily use, explaining complex Gov/UP terminology.
- **Verification**: `get_template()` check passed.
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
