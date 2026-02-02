# Log: Hub Master Admin

## Task 2: Internal Link Inconsistencies (Jan 28, 2026)

- **Date & Time**: 2026-01-28 07:28 PHT
- **Agent Name**: Hub Master Admin
- **Task Assigned**: Task 2 - Internal Link Inconsistencies
- **Files Touched**: `spmo_website/config/views.py`
- **Exact Change Description**: Updated the `apps` dictionary in `admin_portal` view to use hyphenated canonical domains (`gamit-sspmo`, `suplay-sspmo`, `lipad-sspmo`) instead of the old dotted format. This ensures consistency with the production Nginx routing.
- **Result**: Links in the staff portal now point to the correct production subdomains.
- **Status**: COMPLETED
