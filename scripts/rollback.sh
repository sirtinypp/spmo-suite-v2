#!/bin/bash
# Rollback Script for SPMO Suite
# Usage: ./rollback.sh [commit_hash]
# If commit_hash is provided, it reverts git to that hash.
# Otherwise, it attempts to rollback Docker services to the previous tag if available.

set -e

echo ">>> Starting Rollback Procedure..."

if [ -n "$1" ]; then
    echo ">>> Rolling back Source Code to commit: $1"
    git revert --no-edit $1
    echo ">>> Code reverted. Please push changes manually."
else
    echo ">>> No commit hash provided. Attempting Docker Service Rollback..."

    # Check if we are running in docker-compose environment
    if command -v docker >/dev/null 2>&1; then
        echo ">>> Stopping current containers..."
        docker compose down

        # In a real scenario, we would tag images like :v1, :v2.
        # For this setup, we assume we might want to rebuild from the previous safe state or pull 'latest'
        # Here we just restart the services to ensure a clean state
        echo ">>> Restarting services..."
        docker compose up -d --build

        echo ">>> Rollback/Restart complete. Check status with 'docker compose ps'."
    else
        echo ">>> Docker not found. Aborting."
        exit 1
    fi
fi
