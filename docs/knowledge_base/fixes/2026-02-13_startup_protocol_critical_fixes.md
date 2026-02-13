# Critical Fixes Log: Startup Protocol 2026-02-13

## Overview
This document logs the diagnosis and resolution of three critical issues encountered during the system startup and revision preparation on 2026-02-13.

### 1. SUPLAY Production Image Serving Failure
**Severity**: High (Production UI Broken)
**Environment**: Production (`DEBUG=False`)

#### Root Cause
- **Django Behavior**: When `DEBUG=False`, Django *does not* serve static or media files. It expects a reverse proxy (Nginx) or whitespace middleware to handle them.
- **Missing Configuration**: The Nginx configuration (`nginx/conf.d/default.conf`) lacked a `location /media/` block for the SUPLAY server block.
- **Result**: Nginx passed media requests to Django, which returned 404s.

#### Resolution
Added `location /media/` blocks to **all** server blocks in `nginx/conf.d/default.conf`, mapping them to their respective Docker volumes.

```nginx
# Example for SUPLAY
location /media/ {
    alias /var/www/suplay/media/;
}
```

#### Prevention / Learning
- **Protocol**: Always ensure Nginx configuration includes explicit static/media location blocks matching Docker volume mounts for *every* new application.
- **Reference**: See `static_asset_isolation_pattern.md`.

---

### 2. Local Environment CSRF 403 Errors
**Severity**: High (Blocker for Local Development)
**Environment**: Local Development (Docker)

#### Root Cause
- **Django 4.x Security**: Strictly enforces `Origin` header verification against `CSRF_TRUSTED_ORIGINS`.
- **Environment Discrepancy**: The local `.env` file did not specify `CSRF_TRUSTED_ORIGINS`.
- **Fallback Failure**: The default fallback in `settings.py` covered some ports but potentially missed specific `localhost` vs `127.0.0.1` variations used by the user's browser/Docker setup.

#### Resolution
Updated `.env` to explicitly include all development ports and domains:

```ini
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://localhost:8001,http://localhost:8002,http://localhost:8003,http://127.0.0.1:8000,...
```

#### Prevention / Learning
- **Protocol**: When onboarding a new developer or environment, the `.env` file MUST be audited to ensure `CSRF_TRUSTED_ORIGINS` matches the access method (localhost, IP, domain).

---

### 3. SPMO Hub Dashboard "Page Error" (500)
**Severity**: Medium (Internal Dashboard Inaccessible)
**Environment**: Local Development

#### Root Cause
- **Template Syntax Error**: The file `spmo_website/templates/portal.html` used the `{% static ... %}` template tag to load the session timeout script.
- **Missing Load Tag**: The file was missing `{% load static %}` at the very top.
- **Result**: Django raised a `TemplateSyntaxError` when rendering the dashboard.

#### Resolution
Added `{% load static %}` to the first line of `spmo_website/templates/portal.html`.

```html
+ {% load static %}
  <!DOCTYPE html>
  <html lang="en">
```

#### Prevention / Learning
- **Coding Standard**: Any template using `{% static %}` or `{% url %}` MUST have `{% load static %}` or relevant library loaded at the top.
- **Linting**: Consider adding a linter or pre-commit hook to check for orphaned template tags.
