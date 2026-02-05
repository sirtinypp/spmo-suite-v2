# SPMO Suite: Production Mirroring Script
# Mirrors Code, Media, and Databases from Production (172.20.3.91) to Local.
# WARNING: This overwrites local files!

$PROD_USER = "ajbasa"
$PROD_HOST = "172.20.3.91"
$SSH_PORT = "9913"
$LOCAL_ROOT = "c:\Users\Aaron\spmo-suite - Copy"

Write-Host ">>> STARTING PRODUCTION MIRRORING PROTOCOL <<<" -ForegroundColor Yellow

# --- STEP 1: Archive Code & Media on Production ---
Write-Host "`n[1/6] Archiving Code & Media on Production..." -ForegroundColor Cyan
# We exclude venv, git, and cache to save space. We include media.
$REMOTE_CMD = "cd spmo_suite && tar -czf ~/mirror_bundle.tar.gz gamit_app gfa_app suplay_app spmo_website nginx docker-compose.yml"
ssh -p $SSH_PORT $PROD_USER@$PROD_HOST $REMOTE_CMD

if ($LASTEXITCODE -ne 0) { Write-Host "Error creating remote archive!" -ForegroundColor Red; exit }

# --- STEP 2: Dump Production Databases ---
Write-Host "`n[2/6] Dumping Production Databases..." -ForegroundColor Cyan
$DUMP_CMD = "docker exec spmo_shared_db pg_dump -U spmo_admin db_store > ~/db_store_mirror.sql && " +
"docker exec spmo_shared_db pg_dump -U spmo_admin db_gamit > ~/db_gamit_mirror.sql && " +
"docker exec spmo_shared_db pg_dump -U spmo_admin db_gfa > ~/db_gfa_mirror.sql && " +
"docker exec spmo_shared_db pg_dump -U spmo_admin db_spmo > ~/db_spmo_mirror.sql"
ssh -p $SSH_PORT $PROD_USER@$PROD_HOST $DUMP_CMD

if ($LASTEXITCODE -ne 0) { Write-Host "Error dumping databases!" -ForegroundColor Red; exit }

# --- STEP 3: Download Everything ---
Write-Host "`n[3/6] Downloading Archives & Dumps..." -ForegroundColor Cyan
scp -P $SSH_PORT "$PROD_USER@${PROD_HOST}:~/mirror_bundle.tar.gz" "$LOCAL_ROOT\mirror_bundle.tar.gz"
scp -P $SSH_PORT "$PROD_USER@${PROD_HOST}:~/db_*_mirror.sql" "$LOCAL_ROOT\"

if (!(Test-Path "$LOCAL_ROOT\mirror_bundle.tar.gz")) { Write-Host "Download failed!" -ForegroundColor Red; exit }

# --- STEP 4: Extract Code (Overwriting Local) ---
Write-Host "`n[4/6] Extracting Code (Overwriting Local)..." -ForegroundColor Cyan
# Using tar on Windows (built-in 10+)
cd $LOCAL_ROOT
tar -xzf mirror_bundle.tar.gz

# --- STEP 5: Restore Databases ---
Write-Host "`n[5/6] Restoring Databases..." -ForegroundColor Cyan
# Stop Apps first to release DB locks
docker compose down

# Start only DB
docker compose up -d db
Start-Sleep -Seconds 10 # Wait for DB to be ready

# Function to restore a single DB
function Restore-DB ($dbName, $sqlFile) {
    Write-Host "  Restoring $dbName..."
    docker exec spmo_shared_db psql -U spmo_admin -d postgres -c "DROP DATABASE IF EXISTS $dbName;"
    docker exec spmo_shared_db psql -U spmo_admin -d postgres -c "CREATE DATABASE $dbName OWNER spmo_admin;"
    # Restore using psql < file style (piping in Powershell)
    Get-Content $sqlFile | docker exec -i spmo_shared_db psql -U spmo_admin -d $dbName
}

Restore-DB "db_store" "db_store_mirror.sql"
Restore-DB "db_gamit" "db_gamit_mirror.sql"
Restore-DB "db_gfa" "db_gfa_mirror.sql"
Restore-DB "db_spmo" "db_spmo_mirror.sql"

# --- STEP 6: Finalize ---
Write-Host "`n[6/6] Restarting All Services..." -ForegroundColor Cyan
docker compose up -d

Write-Host "`n>>> MIRRORING COMPLETE! Local environment is now 1:1 with Production. <<<" -ForegroundColor Green
