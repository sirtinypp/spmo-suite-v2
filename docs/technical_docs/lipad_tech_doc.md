# Technical Documentation: LIPAD (Travel Management)

## 1. System Overview
**LIPAD** is a comprehensive travel orchestration platform. It manages the full lifecycle of university travel requests, from the initial booking request to the final financial settlement.

## 2. Core Architecture
- **Framework:** Django 4.x
- **Integration:** Utilizes a custom airline credit engine to track university allocations across carriers.
- **Reporting:** Automated flight itinerary and travel order generation.

## 3. Core Data Models
### Travel Trip (`travel.TravelTrip`)
- **Key Fields:** `trip_type` (One-Way, Round-Trip), `origin`, `destination`, `departure_date`, `status`, `credit_allocation`.
- **Workflow Fields:** `admin_verified`, `supervisor_verified`, `chief_approved`.
- **Logic:** Aggregates multiple `PassengerRecords` into a single manageable transaction.

### Passenger Record (`travel.PassengerRecord`)
- **Key Fields:** `full_name`, `employee_id`, `up_mail`, `doc_gov_id`, `doc_flight_ticket`.
- **Relationship:** A `PassengerRecord` belongs to a `TravelTrip`, allowing for complex group travel bookings.

### Credit Log (`travel.CreditLog`)
- **Transaction Types:** `DEDUCTION` (on booking), `REFUND` (on cancellation), `TOP_UP` (annual allocation).
- **Snapshot Logic:** Captures `balance_after` to ensure an immutable audit trail of airline credit usage.

## 4. Key Workflows
### The Approval Hierarchy
1. **Creation:** A travel request is filed with supporting documents (ITR, RIS).
2. **Admin Review:** Verification of documents and airline credit availability.
3. **Supervisor Verification:** Strategic approval from the unit head.
4. **Chief Approval:** Final fiscal authorization from the SPMO Chief.
5. **Issuance:** Automated ticket issuance and PNR reference generation.

### Settlement & Audit
Once a trip is completed, the system facilitates a "Settlement" workflow where final costs are audited against original estimates, and airline credits are reconciled.

## 5. Security & Governance
- **Budgetary Hard-Lock:** The system prevents the creation of new trips if the airline credit balance is insufficient.
- **Sensitive Data Handling:** Passenger government IDs and travel documents are stored with restricted access to authorized travel officers only.
