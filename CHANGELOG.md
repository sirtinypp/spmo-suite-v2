## [Unreleased] - 2026-04-29

### Added
- **GAMIT**: Implemented **Surgical Execution Protocol (SEP)** for persona-aware data isolation across all core views (`dashboard`, `asset_list`, `transaction_ledger`, `transaction_history`, `rpcppe_report`).
- **GAMIT**: Hardened **RPCPPE Reports** with department-level filtering, persistent "DRAFT - NOT OFFICIAL" watermarking, and formal institutional disclosure footers.
- **GAMIT**: Implemented **Administrative UI Gating**, suppressing "Add Asset" and specific "Print" actions for Unit-level personas (`UNIT_AO`, `UNIT_HEAD`).
- **GAMIT**: Gated sidebar navigation to hide "Activity Pulse" and "Admin Panel" from all Unit personas, ensuring a focused departmental experience.
- **GAMIT**: Injected persona-aware queryset filtering into all movement request forms (`Inspection`, `Transfer`, `Return`, `Loss`) to restrict asset selection to the user's unit.
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

### Fixed
- **GAMIT**: Fixed a critical bug where the `sspmo-loader` would block user clicks (e.g., Print buttons) when suppression was active.
- **GAMIT**: Resolved `TypeError` in `AssetLossReportForm` by correctly injecting `request.user` into the form constructor.
- **Infrastructure**: Executed a comprehensive `hard_reset_data.py` protocol to clear all injected demo data for fresh manual validation.

## [Unreleased] - 2026-03-10
...
