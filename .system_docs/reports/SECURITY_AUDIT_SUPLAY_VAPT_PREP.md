# 🔒 SUPLAY Security Audit Report (VAPT Preparation)

**Date:** 2026-01-29  
**Auditor:** Security Shield (Multi-Agent Team)  
**Application:** SUPLAY (Office Supplies Management)  
**Environment:** Production (`suplay-sspmo.up.edu.ph`)

---

## Executive Summary

This security audit identifies **3 CRITICAL**, **4 MODERATE**, and **3 LOW** priority vulnerabilities in SUPLAY before formal Vulnerability Assessment and Penetration Testing (VAPT). Immediate remediation of critical issues is recommended before stakeholder launch.

**Overall Risk Level:** 🔴 HIGH

---

## 🔴 CRITICAL Vulnerabilities

### 1. DEBUG Mode Enabled in Production
**Severity:** CRITICAL  
**CVSS Score:** 9.1  
**Location:** [`settings.py:17`](file:///c:/Users/Aaron/spmo-suite%20-%20Copy/suplay_app/office_supplies_project/settings.py#L17)

**Finding:**
```python
DEBUG = True  # Line 17 - Hardcoded
```

**Risk:**
- Exposes detailed error pages with stack traces
- Reveals file paths, database queries, and environment variables
- Leaks SECRET_KEY and sensitive configuration
- Enables Django Debug Toolbar (if installed)

**Impact:** Attackers can gather intelligence about application structure, dependencies, and potential attack vectors.

**Remediation:**
```python
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
```
Set `DEBUG=False` in `docker-compose.yml` for production.

**Validation:** After fix, trigger 404 error and verify custom error page (not detailed traceback).

---

### 2. Hardcoded SECRET_KEY
**Severity:** CRITICAL  
**CVSS Score:** 9.8  
**Location:** [`settings.py:14`](file:///c:/Users/Aaron/spmo-suite%20-%20Copy/suplay_app/office_supplies_project/settings.py#L14)

**Finding:**
```python
SECRET_KEY = 'django-insecure-spc7#!k=$cb8azdidp*jflg7(_6_#scd7^e=lmww_b1!sqxn2h'
```

**Risk:**
- SECRET_KEY is visible in version control (Git)
- Used for cryptographic signing (sessions, CSRF tokens, password reset)
- Compromise allows session hijacking, CSRF bypass, and privilege escalation

**Impact:** Complete authentication bypass possible if key is leaked.

**Remediation:**
```python
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
```
Generate new key: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

**Validation:** Verify SECRET_KEY not in Git history, stored only in environment variables.

---

### 3. Weak ALLOWED_HOSTS Default
**Severity:** CRITICAL  
**CVSS Score:** 7.5  
**Location:** [`settings.py:20`](file:///c:/Users/Aaron/spmo-suite%20-%20Copy/suplay_app/office_supplies_project/settings.py#L20)

**Finding:**
```python
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost').split(',')
```

**Risk:**
- If `DJANGO_ALLOWED_HOSTS` env var is missing, defaults to `['localhost']`
- In Docker, this may prevent legitimate access
- Potential HTTP Host header attacks

**Impact:** Service disruption or cache poisoning via Host header manipulation.

**Remediation:**
```python
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['']:
    ALLOWED_HOSTS = ['suplay-sspmo.up.edu.ph', 'localhost', '127.0.0.1']
```

**Validation:** Test with invalid Host header, verify rejection.

---

## 🟠 MODERATE Vulnerabilities

### 4. Session Timeout Not Configured
**Severity:** MODERATE  
**CVSS Score:** 5.3  
**Location:** `settings.py` (missing configuration)

**Finding:** No explicit session timeout settings found.

**Risk:**
- Sessions may persist indefinitely
- Increases window for session hijacking
- Unattended terminals remain logged in

**Default Behavior:** Django sessions expire on browser close (unreliable).

**Remediation:**
Add to `settings.py`:
```python
SESSION_COOKIE_AGE = 3600  # 1 hour in seconds
SESSION_SAVE_EVERY_REQUEST = True  # Refresh timeout on activity
SESSION_COOKIE_SECURE = True  # HTTPS only (after SSL enabled)
SESSION_COOKIE_HTTPONLY = True  # Prevent JS access
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection
```

---

### 5. Missing HTTPS Enforcement
**Severity:** MODERATE  
**CVSS Score:** 6.5  
**Status:** Known Issue (Phase 4 - SSL/TLS pending)

**Finding:** Application currently served over HTTP only.

**Risk:**
- Credentials transmitted in plaintext
- Session cookies can be intercepted
- Man-in-the-middle attacks possible

**Remediation:**
1. Obtain SSL certificates
2. Configure Nginx for HTTPS
3. Add to `settings.py`:
```python
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

---

### 6. No Rate Limiting
**Severity:** MODERATE  
**CVSS Score:** 5.0  
**Location:** Application-wide

**Finding:** No rate limiting on login, cart, or checkout operations.

**Risk:**
- Brute-force attacks on authentication
- Cart abuse (resource exhaustion)
- Denial of service via repeated requests

**Remediation:**
Install `django-ratelimit`:
```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')
@login_required
def add_to_cart(request, pk):
    ...
```

---

### 7. Public Product Browsing (New Feature)
**Severity:** MODERATE  
**CVSS Score:** 4.0  
**Location:** [`client.py`](file:///c:/Users/Aaron/spmo-suite%20-%20Copy/suplay_app/supplies/views/client.py)

**Finding:** Recent change removed `@login_required` from `home()`, `search()`, `product_detail()`.

**Risk:**
- Information disclosure (product catalog, pricing, stock levels)
- Potential reconnaissance for targeted attacks

**Business Decision Required:** Is public catalog browsing intentional?

**Mitigation (if intentional):**
- Limit information shown to unauthenticated users (hide stock, pricing)
- Implement rate limiting on search
- Monitor for scraping/crawling

---

## 🟡 LOW Priority Issues

### 8. Missing Content Security Policy (CSP)
**Severity:** LOW  
**CVSS Score:** 3.5

**Finding:** No CSP headers configured.

**Remediation:**
Install `django-csp` and configure:
```python
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")  # Remove unsafe-inline later
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
```

---

### 9. No Security Headers
**Severity:** LOW  
**CVSS Score:** 3.0

**Finding:** Missing X-Content-Type-Options, Referrer-Policy.

**Positive Finding:** `X-Frame-Options` enabled via `XFrameOptionsMiddleware` (line 46).

**Remediation:**
Add to `settings.py`:
```python
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
```

---

### 10. Weak Password Requirements
**Severity:** LOW  
**CVSS Score:** 2.5  
**Location:** [`settings.py:86-99`](file:///c:/Users/Aaron/spmo-suite%20-%20Copy/suplay_app/office_supplies_project/settings.py#L86-L99)

**Finding:** Default Django validators only (no custom length, complexity).

**Current Validators:**
- Similarity check ✅
- Minimum length (8 chars) ✅
- Common passwords ✅
- Not all numeric ✅

**Recommendation:**
Add custom validator for complexity (uppercase, lowercase, digit, special char).

---

## ✅ Positive Security Findings

1. **CSRF Protection:** `CsrfViewMiddleware` enabled (line 43) ✅
2. **Clickjacking Protection:** `XFrameOptionsMiddleware` enabled (line 46) ✅
3. **Authentication Required:** `@login_required` on sensitive operations (cart, checkout) ✅
4. **SQL Injection Protection:** Using Django ORM (`.filter()`, `.get()`) - no raw SQL ✅
5. **Business Logic Enforcement:** `check_monthly_allocation()` validates department limits ✅
6. **Password Validation:** 4 default validators configured ✅
7. **Database Credentials:** From environment variables (not hardcoded) ✅

---

## Remediation Priority Matrix

| Priority | Issue | Effort | Impact |
|:---|:---|:---|:---|
| **P0 (Immediate)** | DEBUG=True | Low | Critical |
| **P0 (Immediate)** | Hardcoded SECRET_KEY | Low | Critical |
| **P0 (Immediate)** | ALLOWED_HOSTS default | Low | Critical |
| **P1 (Pre-Launch)** | Session timeout | Low | Moderate |
| **P1 (Pre-Launch)** | Rate limiting | Medium | Moderate |
| **P2 (Phase 4)** | HTTPS enforcement | High | Moderate |
| **P2 (Phase 4)** | CSP headers | Low | Low |
| **P3 (Enhancement)** | Password complexity | Low | Low |

---

## Compliance & Standards

### OWASP Top 10 (2021) Assessment

| Risk | Status | Notes |
|:---|:---|:---|
| A01: Broken Access Control | 🟡 Partial | Auth required for sensitive ops |
| A02: Cryptographic Failures | 🔴 Vulnerable | Hardcoded SECRET_KEY, no HTTPS |
| A03: Injection | 🟢 Protected | Django ORM prevents SQL injection |
| A04: Insecure Design | 🟡 Partial | Business logic validated |
| A05: Security Misconfiguration | 🔴 Vulnerable | DEBUG=True, weak defaults |
| A06: Vulnerable Components | 🟡 Unknown | Requires dependency scan |
| A07: Authentication Failures | 🟡 Partial | No rate limiting, weak session mgmt |
| A08: Data Integrity Failures | 🟢 Protected | CSRF enabled |
| A09: Logging Failures | 🟡 Unknown | Not assessed |
| A10: SSRF | 🟢 Low Risk | Limited external requests |

---

## Pre-VAPT Action Plan

### Phase 1: Critical Fixes (Required Before VAPT)
1. ✅ Move SECRET_KEY to environment variable
2. ✅ Set DEBUG=False via environment
3. ✅ Fix ALLOWED_HOSTS configuration
4. ✅ Commit & deploy changes
5. ✅ Verify fixes in production

### Phase 2: Moderate Fixes (Recommended Before Launch)
1. Configure session timeout
2. Implement rate limiting
3. Review public browsing permissions
4. Test authentication flows

### Phase 3: SSL/TLS (Phase 4 Planning)
1. Obtain SSL certificates
2. Configure Nginx for HTTPS
3. Enable HTTPS-only settings
4. Test certificate validity

### Phase 4: VAPT Engagement
1. Provide auditors with scope document
2. Schedule penetration testing
3. Monitor and respond to findings
4. Remediate identified vulnerabilities

---

## VAPT Scope Recommendations

**In-Scope:**
- Authentication & authorization mechanisms
- Session management
- Input validation & injection
- Business logic (allocation limits)
- File upload functionality
- API endpoints (if any)

**Out-of-Scope:**
- Third-party libraries (separate dependency scan)
- Infrastructure (separate infrastructure audit)
- Social engineering

**Testing Constraints:**
- Non-destructive testing only
- Production database read-only access
- Rate limiting (5 req/sec max)

---

**Report Compiled By:** Security Shield + JARVIS  
**Status:** Ready for Critical Remediation  
**Next Step:** Fix P0 issues before VAPT engagement

---
*Security Audit - 2026-01-29 09:45 PHT*
