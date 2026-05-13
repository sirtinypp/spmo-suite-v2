# SPMO Suite Institutional Resource Map
**Authoritative Environment Mapping**

## 🌐 Server Infrastructure
| Environment | IP Address | SSH Port | User | Primary Usage |
|:---|:---|:---|:---|:---|
| **PRODUCTION** | `172.20.3.91` | `9913` | `ajbasa` | Live institutional operations |
| **DEVELOPMENT** | `172.20.3.92` | `9913` | `ajbasa` | Feature staging and VAPT |

## 📦 SUPLAY Container Ports
| Port | Service | Environment Link |
|:---|:---|:---|
| `8003` | SUPLAY Web App | [Live Site](http://172.20.3.91:8003) |
| `8000` | SPMO Hub | [Live Site](http://172.20.3.91:8000) |
| `8001` | GAMIT | [Live Site](http://172.20.3.91:8001) |
| `8002` | LIPAD | [Live Site](http://172.20.3.91:8002) |

## 🔑 Database Registry
- **Shared DB Container:** `spmo_shared_db`
- **SUPLAY Database:** `db_store`
- **GAMIT Database:** `db_gamit`
- **GFA Database:** `db_gfa`
- **Hub Database:** `db_spmo`

---
*Last Updated: 2026-05-13*
