# Django Static Files Troubleshooting Guide

## Overview
This guide helps diagnose and resolve static file serving issues in Django applications within the SPMO Suite.

## Quick Diagnosis

### Symptom Checklist
- [ ] Static files return 404 errors
- [ ] Admin panel displays without CSS
- [ ] Images/CSS/JS not loading
- [ ] Works in one environment but not another
- [ ] collectstatic runs successfully but files not served

## Common Scenarios

### Scenario 1: Static Files 404 in Local Development

**Symptoms**:
- Accessing app via `localhost:800X`
- HTML loads but CSS/JS return 404
- Admin panel unstyled

**Diagnosis**:
```bash
# Check if static files exist
docker exec <container> ls -la /app/staticfiles/admin/css/

# Test static file access
curl -I http://localhost:800X/static/admin/css/base.css
```

**Likely Causes**:
1. WhiteNoise not installed/configured
2. Accessing app directly (bypassing nginx)
3. STATIC_ROOT not served by Django

**Solution**: Install and configure WhiteNoise
- See: [Admin Panel Static Files Fix](../fixes/2026-02-06_admin-panel-static-files-whitenoise.md)

---

### Scenario 2: Static Files 404 in Production

**Symptoms**:
- Works locally but not in production
- Nginx returns 404 for static files
- collectstatic ran successfully

**Diagnosis**:
```bash
# Check nginx static volume
docker exec spmo_gateway ls -la /var/www/<app>/static/

# Check nginx configuration
docker exec spmo_gateway cat /etc/nginx/conf.d/default.conf | grep static

# Check nginx logs
docker logs spmo_gateway --tail 50 | grep static
```

**Likely Causes**:
1. Nginx volume not mounted correctly
2. Static files not collected to correct location
3. Nginx alias path incorrect
4. File permissions issue

**Solution**:
```bash
# Recollect static files
docker exec <app_container> python manage.py collectstatic --noinput

# Restart nginx
docker restart spmo_gateway

# Verify nginx volume
docker inspect spmo_gateway | grep -A 10 Mounts
```

---

### Scenario 3: Static Files Work Sometimes

**Symptoms**:
- Intermittent 404 errors
- Works after container restart
- Different behavior on different domains

**Diagnosis**:
```bash
# Check nginx DNS resolution
docker exec spmo_gateway cat /etc/nginx/conf.d/default.conf | grep resolver

# Check container logs for DNS errors
docker logs spmo_gateway | grep -i dns
```

**Likely Causes**:
1. DNS caching issues
2. Container IP changes
3. Nginx upstream resolution

**Solution**: Implement dynamic DNS resolution
```nginx
resolver 127.0.0.11 valid=10s;
set $upstream_app http://app_name:8000;
```

---

### Scenario 4: Shared Volume Conflicts

**Symptoms**:
- One app's static files overwrite another's
- Admin panel works for some apps but not others
- Static files change unexpectedly

**Diagnosis**:
```bash
# Check volume configuration
docker-compose config | grep -A 5 volumes

# Check which containers share volumes
docker inspect <container> | grep -A 10 Mounts
```

**Likely Causes**:
1. Multiple apps using same static volume
2. collectstatic overwrites files
3. Volume mount conflicts

**Solution**: Use separate volumes per app
```yaml
volumes:
  hub_static:
  gamit_static:
  lipad_static:
  suplay_static:
```

## Diagnostic Commands

### Check Static File Configuration
```bash
# View Django settings
docker exec <container> python manage.py diffsettings | grep STATIC

# Check STATIC_ROOT
docker exec <container> python -c "from django.conf import settings; print(settings.STATIC_ROOT)"

# Check STATIC_URL
docker exec <container> python -c "from django.conf import settings; print(settings.STATIC_URL)"
```

### Verify Static Files Collected
```bash
# List collected files
docker exec <container> ls -la /app/staticfiles/

# Count static files
docker exec <container> find /app/staticfiles/ -type f | wc -l

# Check admin files specifically
docker exec <container> ls -la /app/staticfiles/admin/css/
```

### Test Static File Serving
```bash
# Test via localhost (direct)
curl -I http://localhost:800X/static/admin/css/base.css

# Test via nginx (production-like)
curl -I -H "Host: app-domain.up.edu.ph" http://localhost/static/admin/css/base.css

# Test with full response
curl http://localhost:800X/static/admin/css/base.css | head -20
```

### Check Nginx Configuration
```bash
# View nginx config
docker exec spmo_gateway cat /etc/nginx/conf.d/default.conf

# Test nginx config syntax
docker exec spmo_gateway nginx -t

# Reload nginx
docker exec spmo_gateway nginx -s reload

# Check nginx static volumes
docker exec spmo_gateway ls -la /var/www/
```

## Django Static Files Behavior Reference

### DEBUG = True
- Serves files from `STATICFILES_DIRS`
- Does NOT serve from `STATIC_ROOT`
- Automatic serving via `django.contrib.staticfiles`
- Not suitable for production

### DEBUG = False
- Does NOT serve static files at all
- Requires external web server (nginx) OR WhiteNoise
- Production-safe behavior
- Recommended for deployment

### collectstatic Command
```bash
# Collect all static files
python manage.py collectstatic --noinput

# Clear and recollect
python manage.py collectstatic --clear --noinput

# Dry run (see what would be collected)
python manage.py collectstatic --dry-run
```

**What it does**:
1. Gathers files from `STATICFILES_DIRS`
2. Gathers files from each app's `static/` folder
3. Copies everything to `STATIC_ROOT`
4. Does NOT make them servable (requires nginx or WhiteNoise)

## WhiteNoise Integration

### When to Use WhiteNoise
- ✅ Deploying to platforms without nginx
- ✅ Want simplified static file serving
- ✅ Need consistent behavior across environments
- ✅ Want production-ready caching/compression

### When NOT to Use WhiteNoise
- ❌ Already have optimized nginx setup
- ❌ Need advanced CDN integration
- ❌ Require custom static file processing

### WhiteNoise Configuration
```python
# settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Must be here
    # ... other middleware
]

# Optional: Enable compression and caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

## Prevention Checklist

### New Django App Setup
- [ ] Add WhiteNoise to requirements.txt
- [ ] Configure WhiteNoise middleware
- [ ] Set STATIC_ROOT in settings.py
- [ ] Set STATIC_URL in settings.py
- [ ] Add collectstatic to deployment script
- [ ] Test static files in dev environment
- [ ] Test static files in production environment
- [ ] Document static file architecture

### Deployment Checklist
- [ ] Run collectstatic before deployment
- [ ] Verify static volume mounts
- [ ] Check nginx configuration
- [ ] Test static file access
- [ ] Verify admin panel styling
- [ ] Check browser console for 404s
- [ ] Test on all domains

## Related Documentation

- [Admin Panel Static Files Fix](../fixes/2026-02-06_admin-panel-static-files-whitenoise.md)
- [Django Static Files Documentation](https://docs.djangoproject.com/en/stable/howto/static-files/)
- [WhiteNoise Documentation](http://whitenoise.evans.io/)
- [Nginx Static Files Guide](https://nginx.org/en/docs/http/ngx_http_core_module.html#alias)

---

**Last Updated**: 2026-02-06  
**Maintained By**: JARVIS AI Agent System
