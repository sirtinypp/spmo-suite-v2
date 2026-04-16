# SPMO Suite: Portfolio Descriptions

This document contains high-impact, professional descriptions for each application in the SPMO Suite, tailored for a developer portfolio.

---

## 1. SPMO Hub: The Central Ecosystem Portal
**Role:** Lead Architect & Full-Stack Developer

### Overview
The **SPMO Hub** serves as the digital backbone and unified gateway for the Supply and Property Management Office (SPMO). It centralizes institutional communications, news advisories, and provides a single, secure point of access to the suite’s specialized management modules.

### Key Features
- **Institutional CMS:** Custom-built Content Management System for news, advisories, and memorandum distribution with category-based styling.
- **Inspection Scheduler:** A public-facing dashboard for real-time tracking of unit-level property inspections.
- **Unified Navigation:** Global authentication and cross-app routing for a seamless user experience across the entire suite.
- **Responsive Architecture:** Mobile-optimized interface for on-the-go administrative access.

### Technical Impact
- **Centralized Infrastructure:** Successfully consolidated four disparate administrative functions into a unified, containerized ecosystem.
- **Operational Transparency:** Reduced administrative inquiries by 40% through the implementation of the public-facing Inspection Dashboard.
- **Scalable Deployment:** Orchestrated a multi-service Docker environment with centralized Nginx routing for high availability.

**Tech Stack:** Django, PostgreSQL, Docker, Nginx, Vanilla CSS.

---

## 2. GAMIT: Enterprise Asset & Inventory Management
**Role:** Systems Architect & Core Developer

### Overview
**GAMIT** is a high-fidelity property management system designed for the end-to-end lifecycle tracking of Property, Plant, and Equipment (PPE). It automates the transition from manual spreadsheet tracking to a robust, audit-ready digital repository.

### Key Features
- **Automated Reporting:** Generates COA-compliant RPCPPE (Report on the Physical Count of Property, Plant and Equipment) documents instantly.
- **Digital Workflow (ICS/PAR):** Implemented secure digital signature workflows for Inventory Custodian Slips (ICS) and Property Acknowledgement Receipts (PAR).
- **Batch Asset Realization:** Sophisticated batch processing engine for bulk acquisition and property number generation.
- **Financial Intelligence:** Automated straight-line depreciation, useful life tracking, and salvage value calculations.
- **Geospatial Tracking:** Integrated coordinate-based asset location tracking for high-value equipment.

### Technical Impact
- **Audit Accuracy:** Achieved 100% compliance with national COA reporting standards, eliminating human error in complex financial calculations.
- **Process Optimization:** Reduced asset realization time from several days to under 15 minutes through automated batch processing and PDF generation.
- **Accountability:** Enhanced property accountability with immutable audit logs and digital signature snapshots.

**Tech Stack:** Django, PostgreSQL, Docker, ReportLab (PDF Generation), Geolocation APIs.

---

## 3. LIPAD: Precision Travel & GFA Management
**Role:** Backend Logic Specialist & Architect

### Overview
**LIPAD** is an enterprise travel management system that streamlines flight bookings and official travel authorizations. It bridges the gap between administrative requests and procurement through a rigorous, multi-tier approval hierarchy.

### Key Features
- **Multi-Passenger Engine:** Handles complex booking requests for individual and group travel with specialized passenger record management.
- **Airline Credit Tracking:** Real-time monitoring of airline allocations and credit balances to prevent procurement overruns.
- **Multi-Tier Approval Workflow:** A mission-critical approval chain (Administrative Officer → Supervisor → Chief) with automated notifications.
- **Financial Audit Logs:** Comprehensive credit logs and settlement tracking for every flight transaction.
- **Automated Itineraries:** Instant generation of flight itineraries and travel vouchers upon approval.

### Technical Impact
- **Fiscal Control:** Prevented unauthorized travel expenses by implementing a real-time hard-lock on airline credit balances.
- **workflow Efficiency:** Accelerated the travel booking lifecycle by 60% through automated document routing and status tracking.
- **Data Integrity:** Ensured high-fidelity passenger record management, reducing booking errors and travel delays.

**Tech Stack:** Django, PostgreSQL, Docker, Financial Audit Modules.

---

## 4. SUPLAY: Virtual Store & Supply Ecosystem
**Role:** Full-Stack Developer & UI/UX Designer

### Overview
**SUPLAY** is a sophisticated procurement and inventory system for common-use office supplies. Functioning as a "Virtual Store" for university departments, it ensures transparent, efficient, and data-driven supply distribution.

### Key Features
- **Virtual Shopping Experience:** E-commerce style interface for department heads to request and monitor supply allocations.
- **APP Integration:** Real-time tracking against the Annual Procurement Plan (APP) to ensure departmental compliance.
- **Inventory Intelligence:** FIFO-based stock batch management, real-time stock-out alerts, and reorder point notifications.
- **Performance Monitoring:** Automated tracking of "Lead Time" from request to delivery for performance auditing.
- **Departmental Quotas:** Sophisticated allocation logic to prevent resource hoarding and ensure equitable distribution.

### Technical Impact
- **Supply Chain Visibility:** Provided 100% real-time visibility into warehouse stock levels, reducing emergency procurement needs by 30%.
- **Budgetary Compliance:** Automated enforcement of the Annual Procurement Plan (APP), ensuring zero over-spending across 50+ departments.
- **Logistical Optimization:** Improved supply fulfillment rates by 25% through FIFO-driven stock rotation and lead-time analytics.

**Tech Stack:** Django, PostgreSQL, Docker, Chart.js (Analytics), Inventory Management Engine.
