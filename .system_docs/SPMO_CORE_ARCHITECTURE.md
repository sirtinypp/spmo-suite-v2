# SPMO Core Architecture: Unified Identity & Workflow Logic

## 1. The Identity Layer (User-Persona-Role)
The SPMO Suite uses a "Hat-Switching" model to handle institutional authority across GAMIT, SUPLAY, and LIPAD.

*   **User**: The login account (email/password).
*   **Role**: An abstract set of permissions (e.g., `UNIT_AO`, `SPMO_CHIEF`).
*   **Persona**: The active identity. It links a User to a Role and a Department.
    *   *Gist*: A user doesn't "have" permissions; their **active persona** does. This allows one user to act as a Unit Head for one office and an AO for another.

## 2. The Workflow Engine (Dynamic Blueprints)
The system is designed to be "Blueprint-Driven." The logic of how a transaction moves is stored in the database, not hardcoded in the files.

*   **ActionProcess**: The high-level business process (e.g., Asset Acquisition, Supply Request).
*   **Workflow**: A specific path of steps for that process.
*   **WorkflowStep**: A status milestone that requires a specific **Role** to approve.
    *   *Gist*: Different apps (LIPAD, SUPLAY) can have totally different steps, but they all use the same engine to check "Does the current user have a Persona with the Role required for this Step?"

## 3. The Audit Trail (Snapshot Integrity)
Historical accuracy is maintained through the **WorkflowMovementLog**.

*   **Signatory Slots**: Maps Roles to specific signature blocks on institutional reports (PAR, IAR, PTR).
*   **Signature Snapshots**: At the moment of approval, the system captures the Persona's digital signature and title.
    *   *Gist*: This creates a "frozen" record. Even if a staff member's title changes later, the documents they signed in the past remain historically accurate.

## 4. Cross-App Portability
Because the `workflow` logic is centralized:
*   The same **Role Registry** can be used across all apps.
*   The same **Persona Registry** (Staff List) can be imported into any app in the suite.
*   The **Persona Switcher** provides a unified "Cockpit" experience for administrators.
