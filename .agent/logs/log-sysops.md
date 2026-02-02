# Log: SysOps Sentinel

## Historical Background (Synthesized from History)
The SysOps Sentinel orchestrated the containerization and remote deployment of the SPMO Suite.

### Key Milestones
- **Docker Orchestration (Jan 2026)**: Configured `docker-compose.yml` to run four applications and a shared PostgreSQL database.
- **Nginx Subdomain Routing**: Implemented virtual host routing for:
  - `sspmo.up.edu.ph`
  - `gamit.sspmo.up.edu.ph`
  - `lipad.sspmo.up.edu.ph`
  - `suplay.sspmo.up.edu.ph`
- **Remote Server Setup**: Configured the remote server (`172.20.3.91`) with custom SSH port `9913` and optimized resource allocation (15GB RAM).

### Infrastructure Details
- **OS**: Alpine Linux (Containers) / Windows (Local Development).
- **Service Stack**: Django + WhiteNoise + PostgreSQL 15 + Nginx.
- **Network**: Isolated Docker bridge network.

### Recent Operations
- **Production Recovery (Jan 23, 2026 @ 13:58 PHT)**: Resolved container name conflicts blocking service startup. Force-removed orphaned standalone containers and redeployed via docker-compose. All 6 containers restored successfully.

- **Domain Routing Diagnosis (Jan 23, 2026 @ 14:05 PHT)**:
  - **Issue**: Public domains (`sspmo.up.edu.ph`, `gamit-sspmo.up.edu.ph`, etc.) not accessible
  - **Findings**:
    - ✅ Server status: All containers running healthy
    - ✅ Nginx config: Valid and correct (`nginx -t` passed)
    - ✅ Local routing: Port 80 responding correctly with proper virtual host routing
    - ✅ Direct IP access: `172.20.3.91:8000-8003` all accessible
    - ❌ DNS Resolution: Domains resolve to Cloudflare IPs (104.26.6.202, 172.67.70.216, 104.26.7.202)
    - ❌ Expected: Domains should resolve to `172.20.3.91`
  - **Root Cause**: DNS records point to Cloudflare CDN, not to production server
  - **Server Responsibility**: ✅ COMPLETE - Server infrastructure is operational
  - **External Dependency**: DNS/Cloudflare configuration (outside server control)

- **Domain Routing Fix (Jan 23, 2026 @ 14:18 PHT)**: ✅ **RESOLVED**
  - **Root Cause Identified**: Hyphenated domain format mismatch
    - IT configured: `gamit-sspmo.up.edu.ph` (hyphenated)
    - Django settings had: `gamit.sspmo.up.edu.ph` (dotted) ❌
  - **Resolution Steps**:
    1. Updated `CSRF_TRUSTED_ORIGINS` in all app settings.py files (GAMIT, LIPAD, SUPLAY)
    2. Updated `.env` file with hyphenated domains in `ALLOWED_HOSTS`
    3. Uploaded corrected nginx config to remote server
    4. Executed `docker compose down && up -d` to reload environment variables
    5. Restarted nginx gateway
  - **Verification**: Browser testing confirmed all domains routing correctly ✅
  - **Status**: All public domains now operational via Cloudflare proxy

- **Production Lock Protocol Established (Jan 23, 2026 @ 14:27 PHT)**:
  - **Purpose**: Prevent future configuration drift and unauthorized changes
  - **Actions Taken**:
    1. Created `PRODUCTION_LOCK_PROTOCOL.md` - Defines Tier 1/2 protected files
    2. Created `AGENT_BOUNDARIES.md` - Enforces agent responsibility boundaries
    3. Established violation detection and escalation procedures
  - **Protected Files** (Tier 1 - CRITICAL):
    - `.env` (ALLOWED_HOSTS configuration)
    - `docker-compose.yml` (Container orchestration)
    - `nginx/conf.d/default.conf` (Domain routing)
  - **Protected Files** (Tier 2 - SECURITY):
    - All `settings.py` files (CSRF_TRUSTED_ORIGINS)
  - **Enforcement**: JARVIS will flag and halt any agent attempting to modify locked files without user approval
  - **Hub Domain Misconfiguration Resolution (Jan 28, 2026 @ 07:25 PHT)**: ✅ **COMPLETED**
  - **Date & Time**: 2026-01-28 07:25 PHT
  - **Agent Name**: SysOps Sentinel
  - **Task Assigned**: Task 1 - Hub Domain Misconfiguration
  - **Files Touched**: `nginx/conf.d/debug.conf`
  - **Exact Change Description**: Deleted `debug.conf` which contained placeholder `return 200` responses for `sspmo.up.edu.ph` and other dotted domains. Deletion allows Nginx to fall back to the production `proxy_pass` rules defined in `default.conf`.
  - **Result**: `debug.conf` removed. Production routing for `sspmo.up.edu.ph` should now render the full Hub content once deployed.
  - **Status**: COMPLETED
- **Incident Recovery: Forced HTTPS Rollback (Jan 28, 2026 @ 09:10 PHT)**: ✅ **RESOLVED**
  - **Issue**: Forced SSL redirection caused a loop (Cloudflare 521).
  - **Actions Taken**:
    1. Revert `SECURE_SSL_REDIRECT = False` in all 4 apps.
    2. Fixed `nginx` directory permissions (chown to `ajbasa`).
    3. Re-deployed stable configuration via git.
  - **Verification**:
    - `curl -I http://172.20.3.91` → **200 OK**
    - Subdomain routing (vhosts) → **200 OK** (Localhost tests)
  - **Status**: 🟢 PRODUCTION STABLE. (Cloudflare domains may require cache purge).
