# Changelog - SPMO Hub
All notable changes to the UP SSPMO project will be documented in this file.

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
