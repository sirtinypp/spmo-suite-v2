# Force Sync Code: Wipe Local & Replace from Mirror
# Ensures 1:1 match with Production Code.

$LOCAL_ROOT = "c:\Users\Aaron\spmo-suite - Copy"
$BUNDLE = "$LOCAL_ROOT\mirror_bundle.tar.gz"

Write-Host ">>> STARTING FORCE CODE SYNC (NUKE & PAVE) <<<" -ForegroundColor Yellow

if (!(Test-Path $BUNDLE)) {
    Write-Host "Error: Mirror bundle not found! Run mirror_production.ps1 first." -ForegroundColor Red
    exit 1
}

# --- STEP 1: Wipe Local Directories ---
Write-Host "[1/4] Wiping local application directories..." -ForegroundColor Cyan
Remove-Item -Recurse -Force "$LOCAL_ROOT\gamit_app" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$LOCAL_ROOT\gfa_app" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$LOCAL_ROOT\suplay_app" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$LOCAL_ROOT\spmo_website" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$LOCAL_ROOT\nginx" -ErrorAction SilentlyContinue

# --- STEP 2: Extract Archive ---
Write-Host "[2/4] Extracting Production Code..." -ForegroundColor Cyan
cd $LOCAL_ROOT
tar -xzf mirror_bundle.tar.gz

# --- STEP 3: Restart Containers ---
Write-Host "[3/4] Restarting Containers to load new code..." -ForegroundColor Cyan
docker restart app_gamit app_gfa app_store app_hub spmo_gateway

# --- STEP 4: Collect Static Files ---
Write-Host "[4/4] Collecting Static Files (Fixing Design)..." -ForegroundColor Cyan
# We run this to ensure static assets (CSS/JS) are copied to the volume served by Nginx/WhiteNoise
docker exec app_gamit python manage.py collectstatic --noinput
docker exec app_gfa python manage.py collectstatic --noinput
docker exec app_store python manage.py collectstatic --noinput
docker exec app_hub python manage.py collectstatic --noinput

Write-Host "`n>>> FORCE SYNC COMPLETE! Code and Design are now 1:1. <<<" -ForegroundColor Green
