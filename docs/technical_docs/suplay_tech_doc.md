# Technical Documentation: SUPLAY (Virtual Store & Supply Management)

## 1. System Overview
**SUPLAY** is a digital procurement platform for common-use office supplies. It models the Supply and Property Management Office's inventory as a "Virtual Store" for university departments.

## 2. Core Architecture
- **Framework:** Django 4.x
- **Integration:** Directly linked to the Annual Procurement Plan (APP) for budgetary compliance.
- **Reporting:** Real-time inventory analytics and reorder point alerts.

## 3. Core Data Models
### Product (`supplies.Product`)
- **Key Fields:** `name`, `brand`, `item_code`, `category`, `stock`, `unit`, `reorder_point`.
- **Logic:** Integrated reorder point alerts monitor stock levels against departmental demand.

### Stock Batch (`supplies.StockBatch`)
- **Key Fields:** `product`, `batch_number`, `quantity_initial`, `quantity_remaining`, `cost_per_item`, `date_received`.
- **Relationship:** Each `Product` has multiple `StockBatches`, following a strict FIFO methodology.

### Annual Procurement Plan (`supplies.AnnualProcurementPlan`)
- **Key Fields:** `department`, `product`, `year`, `jan` through `dec` allocations.
- **Logic:** Tracks `quantity_consumed` and `remaining_balance` for every product and department.

## 4. Key Workflows
### The Procurement Lifecycle
1. **Demand Forecasting:** Departments define their annual needs in the APP.
2. **Requisition (The "Store" Flow):** Users add items to their "Virtual Cart" and checkout based on their APP allocation.
3. **Approval:** The SPMO staff verifies the request and approves the delivery/pickup.
4. **FIFO Issuance:** The system automatically deducts stock from the oldest `StockBatch` available.

### Inventory Replenishment
SUPLAY provides real-time stock-out reports, allowing the SPMO warehouse to optimize procurement based on actual departmental burn rates.

## 5. Security & Governance
- **Quota Enforcement:** The system prevents orders that exceed the approved Annual Procurement Plan (APP) allocations.
- **Performance Auditing:** `Lead Time` monitoring (Request Time → Approval Time → Delivery Time) provides operational KPIs for the SPMO staff.
