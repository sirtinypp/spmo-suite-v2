# Technical Documentation: SPMO Hub

## 1. System Overview
The **SPMO Hub** is the central gateway for the SPMO Suite. Built with Django, it serves as an institutional portal that consolidates disparate administrative and inventory-related functions into a single user-facing interface.

## 2. Architecture
- **Framework:** Django 4.x
- **Infrastructure:** Containerized via Docker, orchestrated with Docker Compose.
- **Reverse Proxy:** Nginx (handles static assets and routes requests to Gunicorn).
- **Database:** PostgreSQL (shared across the suite for centralized data management).

## 3. Core Data Models
### News Post (`website.NewsPost`)
- **Fields:** `title`, `content`, `image`, `category` (Advisory, Event, Memo), `published_at`.
- **Logic:** The `category` field dynamically updates the frontend CSS theme for each post.

### Inspection Schedule (`website.InspectionSchedule`)
- **Fields:** `unit_name`, `activity`, `date`, `status`.
- **Logic:** Provides a public-facing audit trail of planned and completed property inspections.

## 4. Key Workflows
### Centralized Routing
The Hub acts as a router. Although each app (GAMIT, SUPLAY, LIPAD) runs on its own port/container, the Hub provides a unified frontend that masks the underlying complexity.

## 5. Security & Governance
- **Authentication:** Integrated with individual app authentication or future single-sign-on (SSO) systems.
- **Static Assets:** Isolated static file serving via Nginx ensures high performance and prevents cross-site asset leaks.
