# Architecture Overview

This document outlines the architecture of the SPMO-SUITE monorepo, detailing the applications, their ports, and database configurations as defined in `docker-compose.yml` and their respective `settings.py` files.

## Application Details

| Application | Docker Service Name | Host Port | Database Name | Source Folder |
| :--- | :--- | :--- | :--- | :--- |
| **GAMIT** | `gamit_app` | 8001 | `db_gamit` | `gamit_app` |
| **LIPAD** | `gfa_app` | 8002 | `db_gfa` | `gfa_app` |
| **SUPLAY** | `virtual_store` | 8003 | `db_store` | `virtual_store` |

## Verification Notes

- **GAMIT Dependencies**: The `gamit_app` (`gamit_app/requirements.txt`) **includes** `django-import-export`.
