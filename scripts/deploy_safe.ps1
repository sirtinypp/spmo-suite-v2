# ==============================================================================
# SPMO SUITE - SAFE DEPLOYMENT PROTOCOL
# ==============================================================================
# PURPOSE:  Deploys Local Code to Production WITHOUT overwriting Config/Data.
# TARGET:   172.20.3.91
# EXCLUDES: settings.py, media/, sqlite3, logs, __pycache__
# ==============================================================================

$PROD_HOST = "172.20.3.91"
$PROD_USER = "ajbasa"
$SSH_PORT = "9913"
$REMOTE_DIR = "~/spmo_suite"
$STAGING_DIR = "~/deploy_staging"
$LOCAL_PKG = "deploy_package.tar.gz"

Write-Host "`n>>> SPMO SAFE DEPLOYMENT PROTOCOL <<<" -ForegroundColor Cyan
Write-Host "Target: $PROD_USER@$PROD_HOST" -ForegroundColor Gray

# --- STEP 1: Pack Local Code (Safe Mode) ---
Write-Host "`n[1/4] Packing Local Code (Excluding Sensitive Data)..." -ForegroundColor Yellow
# We use tar with strict excludes to create a "Clean" package
tar --exclude='**/settings.py' `
    --exclude='**/__pycache__' `
    --exclude='**/*.sqlite3' `
    --exclude='.git' `
    --exclude='logs' `
    --exclude='media' `
    --exclude='venv' `
    --exclude='tmp' `
    -czf $LOCAL_PKG gamit_app gfa_app suplay_app spmo_website nginx docker-compose.yml

if ($LASTEXITCODE -ne 0) { Write-Host "Error packing code!" -ForegroundColor Red; exit }
Write-Host "Package created: $LOCAL_PKG" -ForegroundColor Green

# --- STEP 2: Upload to Staging ---
Write-Host "`n[2/4] Uploading to Production Staging..." -ForegroundColor Yellow
$SCP_CMD = "scp -P $SSH_PORT $LOCAL_PKG ${PROD_USER}@${PROD_HOST}:${STAGING_DIR}/$LOCAL_PKG"

# Ensure staging dir exists first
ssh -p $SSH_PORT $PROD_USER@$PROD_HOST "mkdir -p $STAGING_DIR"
# Upload
scp -P $SSH_PORT $LOCAL_PKG ${PROD_USER}@${PROD_HOST}:~/deploy_staging/

if ($LASTEXITCODE -ne 0) { Write-Host "Upload failed!" -ForegroundColor Red; exit }
Write-Host "Upload complete." -ForegroundColor Green

# --- STEP 3: Apply Changes (Extract & Overwrite) ---
Write-Host "`n[3/4] Applying Code to Live Directory..." -ForegroundColor Yellow
$REMOTE_SCRIPT = "
    echo '>>> BACKING UP SETTINGS (Just in case) <<<'
    cp ~/spmo_suite/gamit_app/gamit_core/settings.py ~/settings_backup_gamit.py
    cp ~/spmo_suite/spmo_website/config/settings.py ~/settings_backup_hub.py
    # Add other backups if needed...

    echo '>>> EXTRACTING UPDATE <<<'
    cd ~/spmo_suite
    # Extract contents of package, overwriting matching files.
    # Since package DOES NOT contain settings.py, the live settings.py is safe.
    tar -xzf ~/deploy_staging/$LOCAL_PKG
    
    echo '>>> CLEANUP <<<'
    rm ~/deploy_staging/$LOCAL_PKG
"
ssh -p $SSH_PORT $PROD_USER@$PROD_HOST $REMOTE_SCRIPT

if ($LASTEXITCODE -ne 0) { Write-Host "Remote extraction failed!" -ForegroundColor Red; exit }
Write-Host "Code applied successfully." -ForegroundColor Green

# --- STEP 4: Restart Services (Optional) ---
# Changes to Python templates/views often require a restart. CSS/JS might not.
$RESTART = Read-Host "`n[4/4] Restart Containers to apply changes? (Y/N)"
if ($RESTART -eq "Y") {
    Write-Host "Restarting Containers..." -ForegroundColor Cyan
    ssh -p $SSH_PORT $PROD_USER@$PROD_HOST "cd ~/spmo_suite && docker restart app_gamit app_hub app_gfa app_store"
    Write-Host "Service Restart Triggered." -ForegroundColor Green
}
else {
    Write-Host "Skipping Restart." -ForegroundColor Gray
}

Write-Host "`n>>> DEPLOYMENT COMPLETE <<<" -ForegroundColor Cyan
Write-Host "Please verify changes at https://gamit-sspmo.up.edu.ph etc." -ForegroundColor Gray
Remove-Item $LOCAL_PKG
