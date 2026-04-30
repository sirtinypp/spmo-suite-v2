# ENVIRONMENT CONFIGURATION MASTER
**SPMO Suite — Authoritative Handshake & Identity Registry**
**Last Updated:** April 30, 2026

> [!IMPORTANT]
> This document is the **Single Source of Truth** for environment-sensitive data. 
> DO NOT modify these values without explicit architectural review.

---

## 1. SSO Configuration (Google OAuth)
| Property | Value |
|---|---|
| **Client ID** | `307307846379-hk1atfjhev4p84fdicmglhl57jik0cn7.apps.googleusercontent.com` |
| **Client Secret** | `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` |
| **Provider** | `google` |
| **Logic Source** | Hardcoded in `settings.py` (via `SOCIALACCOUNT_PROVIDERS`) |

---

## 2. Environment Matrix
| Environment | IP Address | Site ID | Domain Mapping | Protocol |
|---|---|---|---|---|
| **LOCAL** | `localhost` | `1` | `localhost:8001` | HTTP |
| **DEV** | `172.20.3.92` | `1` | `gamit-sspmo-dev.up.edu.ph` | HTTPS |
| **PROD** | `172.20.3.91` | `1` | `gamit-sspmo.up.edu.ph` | HTTPS |

---

## 3. Administrative Identities
| Username | Email | Role | Master Password |
|---|---|---|---|
| **`grootadmin`** | `ajbasa@up.edu.ph` | Master Superuser | `xiarabasa12` |

---

## 4. Stability Lock (Surgical Bootstrap)
To prevent "Identity Drift" or "SSO Failure" after database changes, run the following command from `gamit_app/`:

```bash
# Restore local environment to Gold State
python manage.py shell -c "from django.contrib.sites.models import Site; from django.contrib.auth.models import User; from allauth.socialaccount.models import SocialApp; SocialApp.objects.all().delete(); site = Site.objects.get_or_create(id=1)[0]; site.domain='localhost:8001'; site.name='GAMIT Local'; site.save(); user, _ = User.objects.get_or_create(username='grootadmin'); user.set_password('xiarabasa12'); user.email='ajbasa@up.edu.ph'; user.is_superuser=True; user.is_staff=True; user.save(); User.objects.filter(username='ajbasa').delete(); print('ENVIRONMENT LOCKED & RESTORED')"
```

---

## 5. Architectural Guardrails
1. **No SocialApp Records in DB:** DEV and PROD rely strictly on `settings.py`. Do NOT create database records for Google SSO as it causes `MultipleObjectsReturned` conflicts.
2. **Identity Consolidation:** `grootadmin` is the only account allowed to use `ajbasa@up.edu.ph` on Local.
