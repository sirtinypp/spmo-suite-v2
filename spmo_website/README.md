# SPMO Website CMS Guide

## News Management
1. Go to Admin Panel > **News Posts**
2. Click "Add News Post"
3. Select Category (Advisory, Event, Memo) - *This determines the color theme*
4. Upload Image (Optional but recommended)
5. Fill Content (Popup details) and Summary (Card view)

## Inspection Schedule
1. Go to Admin Panel > **Inspection Schedules**
2. Add "Unit Name", "Activity", and "Date"
3. Set Status to "Confirmed" to display on the dashboard.

## Deployment Notes
- This update `design_sspmohub_1` requires database migrations.
- **Commands**:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```
