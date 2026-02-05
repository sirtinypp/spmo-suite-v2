# Changelog

All notable changes to the SPMO Suite project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-21

### 🎉 Initial Stable Release

This is the first stable production release of the SPMO Suite, a unified containerized application suite for the University of the Philippines Supply & Property Management Office.

### Applications Included

- **SPMO Hub** (Port 8000) - Central portal and landing page
- **GAMIT** (Port 8001) - Government Asset Management and Inventory Tracking
- **LIPAD** (Port 8002) - Logistics and travel Itinerary Portal for Authorized Departures
- **SUPLAY** (Port 8003) - Sustainable Supply Utilization, Purchasing, Logistics, Assets and Yield Assessment

### Added

#### Infrastructure
- Docker Compose orchestration for all services
- Shared PostgreSQL 15 database across all applications
- Nginx reverse proxy with domain routing
- Persistent Docker volumes for database storage
- Environment variable configuration via `.env` file

#### Applications
- SPMO Hub with news management and service directory
- GAMIT asset management with QR code support
- LIPAD travel booking and GFA integration
- SUPLAY supply management with real-time inventory

#### Configuration
- Nginx virtual host routing for subdomains:
  - `sspmo.up.edu.ph` → SPMO Hub
  - `gamit.sspmo.up.edu.ph` → GAMIT
  - `lipad.sspmo.up.edu.ph` → LIPAD
  - `suplay.sspmo.up.edu.ph` → SUPLAY
- Default server block for IP address access
- SSL/HTTPS ready configuration (certificates not included)

#### Security
- CSRF protection enabled across all apps
- Secure cookie settings
- HSTS headers configured
- X-Frame-Options and security headers
- Superuser credential management

### Fixed

#### Critical Fixes
- **SPMO Hub**: Applied database migration for `config_newspost.created_at` column
- **LIPAD**: Updated CSRF_TRUSTED_ORIGINS to include localhost addresses
- **Nginx**: Added default server block to prevent binary downloads on IP access
- **Superuser**: Synchronized `grootadmin` credentials across all applications

#### Application Fixes
- HTTP/HTTPS access clarification for development server
- Database connection configuration for Docker networking
- Static file serving configuration
- Template syntax errors corrected

### Changed

- Consolidated all logs into `logs/` directory
- Organized legacy archives into `archive/` folder
- Updated README with correct port mappings
- Enhanced .gitignore for better version control

### Infrastructure

#### Deployment
- **Development**: localhost ports 8000-8003
- **Production**: Deployed to 172.20.3.91
- **Uptime**: 8+ days stable operation
- **Resources**: 15GB RAM (7% used), 75GB disk (19% used)

#### Database
- PostgreSQL 15 (Alpine)
- Separate databases per application:
  - `db_spmo` - SPMO Hub
  - `db_gamit` - GAMIT
  - `db_gfa` - LIPAD
  - `db_store` - SUPLAY
- Persistent storage via Docker volumes

### Documentation

- Comprehensive README with setup instructions
- Docker Compose configuration documented
- Nginx routing configuration explained
- Troubleshooting guide included

### Security Notes

- Default superuser: `grootadmin` / `xiarabasa12`
- SSH server access: Port 9913
- All containers running in isolated Docker network
- Database credentials managed via environment variables

### Known Issues

- Domain name `sspmo.up.edu.ph` may require browser cache clear on first access
- SSL certificates not configured (HTTP only in current release)
- Some debug files present on remote server (cleanup pending)

### Deployment Status

- ✅ Local Development: Fully operational
- ✅ Remote Server (172.20.3.91): Deployed and stable
- ⚠️ HTTPS/SSL: Not configured (planned for future release)
- ⚠️ Automated Backups: Not configured (planned for future release)

### Credits

**Developed for**: University of the Philippines - Supply & Property Management Office  
**Server Admin**: ajbasa  
**Release Date**: January 21, 2026  
**Status**: Stable Production Release

---

## [1.2.0-production] - 2026-02-05

### 🎉 Stable Release v2

Major stability release consolidating UI fixes, security hardening, and code reorganization.

### Added
- **Vault Guardian Protocols**: Automated pre-push safety checks, backup verification, and hardcoded credential scanning.
- **LIPAD UI Polish**: Fixed template rendering issues in forms and dashboard credits display.
- **Prevention Guides**: Added `.agent/TEMPLATE_TAG_PREVENTION.md` for safer Django template handling.
- **Utility Scripts**: Added `fix_templates.py` for automated tag repair.
- **Code Organization**: Restructured 51+ files into `archives/`, `backups/`, `logs/`, and `scripts/utils/`.

### Fixed
- **Template Rendering**: Resolved split Django template tags (`{{ form.field }}`) appearing as text in `form.html` and `dashboard.html`.
- **Git Push Blocker**: Resolved Git LFS issue by removing 153MB `mirror_bundle.tar.gz` from history.
- **Security**: Removed 7 debug scripts containing hardcoded credentials (`xiarabasa12`).
- **Configuration**: Standardized `DEBUG=True` handling and environment variable usage across all apps.

### Security
- **Hardening**: Verified `check --deploy` status for all 4 applications.
- **Credentials**: Scrubbed all hardcoded passwords from version control.
- **Backups**: Verified database backup integrity (7 recent backups).

### Changed
- **Documentation**: Updated `DAILY_LOG`, `walkthrough.md`, and added `pre_push_verification.md`.
- **Gitignore**: Enhanced rules to strictly exclude debug scripts and archives.

---

## [1.1.0-pre] - 2026-01-23

### Added
- **JARVIS Agent System**: Initialized a specialized multi-agent command system for focused project development.
- **Persistent Memory Logs**: Department-specific documentation and history tracking.
- **Simple Portal View**: Added `views_simple.py` and `portal.html` (pending) for staff/public separation on the Hub.
- **Vaulting Protocols**: Formalized session-end git and backup procedures.

### Fixed
- **Git Repository Health**: Cleaned large legacy tarballs from the active repository to restore remote push functionality.
- **Team Synchronization**: All agents updated with the January 22nd production status.

### Planned for 1.3.0
- SSL/HTTPS certificate configuration
- Automated database backup system
- Enhanced error logging and monitoring
- Performance optimization
- User authentication improvements

### Planned for 2.0.0
- API endpoints for external integrations
- Mobile-responsive improvements
- Advanced reporting features
- Email notification system

---

**Note**: For detailed deployment and troubleshooting information, see the project README.md and documentation in the `docs/` folder.
