# Knowledge Base: CSRF Trusted Origins Environment Sync
**Fix ID:** KB-20260212-001  
**Category:** Security / Deployment  
**Status:** RESOLVED

---

## 🔍 Issue: CSRF Verification Failed (403 Forbidden)
During the transition to a multi-container architecture with a reverse proxy (Nginx), Django's CSRF mechanism failed when accessed via subdomains (e.g., `sspmo-dev.up.edu.ph`).

### Root Cause
1. **Hardcoded Settings:** `CSRF_TRUSTED_ORIGINS` was hardcoded to production domains in `settings.py`.
2. **Missing Environment Pass-through:** The `docker-compose.yml` file did not pass the `CSRF_TRUSTED_ORIGINS` environment variable from the host `.env` file to the individual app containers.

---

## 🛠️ Solution: Dynamic Origin Synchronization

### 1. Settings Modification
Updated `settings.py` for all apps (Hub, GAMIT, SUPLAY, LIPAD) to read trusted origins from an environment variable:

```python
# CSRF Configuration - Read from environment or use production defaults
csrf_origins_env = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if csrf_origins_env:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_origins_env.split(',') if origin.strip()]
else:
    CSRF_TRUSTED_ORIGINS = [
        'https://sspmo.up.edu.ph',
        'http://sspmo.up.edu.ph',
        'http://localhost:8000'
    ]
```

### 2. Docker Compose Update
Ensured the variable is properly mapped in `docker-compose.yml`:

```yaml
services:
  app_name:
    ...
    environment:
      - CSRF_TRUSTED_ORIGINS=${CSRF_TRUSTED_ORIGINS}
```

### 3. Environment Configuration
Maintained a clean `.env` on the host:
```bash
CSRF_TRUSTED_ORIGINS=https://sspmo-dev.up.edu.ph,https://gamit-sspmo-dev.up.edu.ph...
```

---

## ✅ Prevention Checklist
- [ ] Ensure `DJANGO_ALLOWED_HOSTS` matches incoming request headers.
- [ ] Ensure `CSRF_TRUSTED_ORIGINS` contains the full URL with protocol (https/http).
- [ ] Always pass environment variables explicitly in `docker-compose.yml` if using `.env`.
