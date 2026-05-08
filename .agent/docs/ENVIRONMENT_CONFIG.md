# ENVIRONMENT CONFIGURATION MASTER
**SPMO Suite — Authoritative Handshake & Identity Registry**
**Last Updated:** May 5, 2026

> [!IMPORTANT]
> This document is the **Single Source of Truth** for environment-sensitive data. 
> DO NOT modify these values without explicit architectural review.

---

## 1. SSO Configuration (Google OAuth)
| Property | Value |
|---|---|
| **Client ID** | `[REDACTED]` |
| **Client Secret** | `[REDACTED]` |
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

## 2.1 Git & Version Control
| Property | Value |
|---|---|
| **Local Repo Root** | `c:\Users\Aaron\spmo-suite - Copy` |
| **Git Executable** | `C:\Users\Aaron\AppData\Local\GitHubDesktop\app-3.5.8\resources\app\git\cmd\git.exe` |
| **Remote (SSH)** | `git@github.com:sirtinypp/spmo-suite-v2.git` |
| **GitHub Desktop** | `C:\Users\Aaron\AppData\Local\GitHubDesktop\app-3.5.8\GitHubDesktop.exe` |

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

## 6. GAMIT Technical Inventory (Asset Manager)
| Component | Value / Path |
|---|---|
| **App Root** | `c:\Users\Aaron\spmo-suite - Copy\gamit_app` |
| **Database Name** | `db_gamit` |
| **Local URL** | `http://localhost:8001` |
| **Secret Key** | `+g1($&r^jwkprb)2o9fl8m=ba_(tq5v+^bj43)2z*$&l1c@7edx5` |
| **Container Name**| `app_gamit` |
| **Workflow App** | `workflow` (internal) |
| **Primary Models** | `Asset`, `AssetBatch`, `AssetTransferRequest` |

---

## 7. SUPLAY Technical Inventory (Virtual Store)
| Component | Value / Path |
|---|---|
| **App Root** | `c:\Users\Aaron\spmo-suite - Copy\suplay_app` |
| **Database Name** | `db_store` |
| **Local URL** | `http://localhost:8003` |
| **Secret Key** | `store-prod-secret-2026-v2-virtual-store-key` |
| **Container Name**| `app_store` |

---

## 8. GFA/LIPAD Technical Inventory (Travel)
| Component | Value / Path |
|---|---|
| **App Root** | `c:\Users\Aaron\spmo-suite - Copy\gfa_app` |
| **Database Name** | `db_gfa` |
| **Local URL** | `http://localhost:8002` |
| **Secret Key** | `gfa-prod-secret-key-2026-secure-lipad-travel-system-v1` |
| **Container Name**| `app_gfa` |
+
+---
+
+## 9. Architectural Guardrails
+1. **No SocialApp Records in DB:** DEV and PROD rely strictly on `settings.py`. Do NOT create database records for Google SSO as it causes `MultipleObjectsReturned` conflicts.
+2. **Identity Consolidation:** `grootadmin` is the only account allowed to use `ajbasa@up.edu.ph` on Local.
+3. **GAMIT Branding:** Ensure GAMIT remains branded as GAMIT in this workspace to avoid confusion with other "Asset Manager" initiatives.
+
