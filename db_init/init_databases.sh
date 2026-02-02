#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE db_spmo;
    CREATE DATABASE db_gamit;
    CREATE DATABASE db_gfa;
    CREATE DATABASE db_store;
EOSQL