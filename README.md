
# SPMO Suite (GAMIT, SUPLAY, LIPAD)

This is the unified containerized suite for the SPMO applications.

## Applications
*   **SPMO Hub**: `http://localhost:8000` (Central Portal)
*   **GAMIT (Inventory)**: `http://localhost:8001` (Asset Management)
*   **LIPAD (Travel)**: `http://localhost:8002` (GFA/Travel)
*   **SUPLAY (Virtual Store)**: `http://localhost:8003` (Supply Management)

## How to Run

1.  **Install Docker Desktop**: Ensure Docker Engine is running on your machine.
2.  **Configuration**: 
    *   Ensure the `.env` file exists in this directory (defaults typically provided in `docker-compose.yml`).
3.  **Start Services**:
    ```bash
    docker compose up --build
    ```
4.  **Access**: Open your browser to the URLs listed above.

## Infrastructure
*   **Database**: Shared PostgreSQL 15 container (Service name: `db`).
*   **Networking**: Internal Docker network `spmo_network` (auto-created).
*   **Storage**: Persistent volume `postgres_data` for database storage.

## Troubleshooting
*   If a service fails to connect to the DB, ensure the `db` container is "Healthy" (it may take 10-20 seconds to start up initially).
*   To stop all services: `docker compose down`.
