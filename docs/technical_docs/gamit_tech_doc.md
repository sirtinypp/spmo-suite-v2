# Technical Documentation: GAMIT (Inventory & Asset Management)

## 1. System Overview
**GAMIT** is a specialized ERP-level application for property management. It provides the necessary tools for national government-compliant property accounting and lifecycle management.

## 2. Core Architecture
- **Framework:** Django 4.x
- **Data Engine:** Multi-tenant approach with Department-based isolation.
- **Reporting:** Utilizes ReportLab for real-time PDF generation of ICS and PAR documents.

## 3. Core Data Models
### Asset (`inventory.Asset`)
- **Key Fields:** `property_number`, `item_id`, `acquisition_cost`, `date_acquired`, `useful_life_years`, `salvage_value`.
- **Financial Logic:** Implements automated straight-line depreciation via `@property` methods like `book_value` and `annual_depreciation`.
- **Classification:** Categorized by standard PPE classes (ICT, Machinery, Furniture, etc.).

### Asset Batch (`inventory.AssetBatch`)
- **Key Fields:** `transaction_id`, `status` (Anticipatory to PAR Released), `po_number`, `supplier_name`.
- **Workflow Engine:** A state machine monitors batch progress, transitioning from delivery validation to final signature.

### Approval Log (`inventory.ApprovalLog`)
- **Logic:** Each workflow step creates an immutable log entry with a snapshot of the approver's digital signature for audit integrity.

## 4. Key Workflows
### Asset Realization (The "Batch" Flow)
1. **Acquisition:** Procurement data is imported (via CSV or manual entry) into an `AssetBatch`.
2. **Inspection:** Assets are verified for condition and serial numbers.
3. **Accountability (ICS/PAR):** Assets are assigned to a custodian.
4. **Finalization:** The system generates a property number and a finalized PDF receipt (PAR/ICS).

### Depreciation Tracking
GAMIT automatically calculates the monthly depreciation for all PPE, allowing the Accounting department to maintain accurate financial records for government audits.

## 5. Security & Governance
- **Role-Based Access Control (RBAC):** Users are assigned roles (SPMO Admin, Accounting, Unit Head), which restrict access to specific management functions.
- **Audit Trails:** `AssetChangeLog` tracks every field-level change on high-value assets, capturing the user, timestamp, and IP address.
