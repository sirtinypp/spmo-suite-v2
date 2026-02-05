# ==============================================================================
# SPMO SUITE - DAILY STARTUP ASSISTANT
# ==============================================================================

Write-Host "`n>>> SPMO SUITE: SYSTEM STATUS CHECK <<<" -ForegroundColor Cyan

# 1. Check Docker
$DockerStatus = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[CRITICAL] Docker is NOT running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and run this script again." -ForegroundColor Red
    exit
}
else {
    Write-Host "[OK] Docker Engine is Active." -ForegroundColor Green
}

# 2. Check Containers
$Running = docker ps --format "{{.Names}}"
if ($Running -match "app_gamit") { Write-Host "[OK] GAMIT is running." -ForegroundColor Green } else { Write-Host "[WARN] GAMIT is stopped." -ForegroundColor Yellow }
if ($Running -match "app_store") { Write-Host "[OK] SUPLAY is running." -ForegroundColor Green } else { Write-Host "[WARN] SUPLAY is stopped." -ForegroundColor Yellow }

# 3. Operations Menu
Write-Host "`n==========================================" -ForegroundColor White
Write-Host "       AVAILABLE OPERATIONS" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor White
Write-Host "1. [Start]   Start All Servers (Localhost)" -ForegroundColor Cyan
Write-Host "2. [Deploy]  Push Changes to Production (Safe Mode)" -ForegroundColor Yellow
Write-Host "3. [Mirror]  Reset Local env from Production (Nuke)" -ForegroundColor Red
Write-Host "4. [Docs]    Open Operations Manual" -ForegroundColor Gray
Write-Host "==========================================" -ForegroundColor White

$Choice = Read-Host "Select an option (1-4)"

switch ($Choice) {
    "1" { docker-compose up -d; Write-Host "Servers starting..." -ForegroundColor Green }
    "2" { ./scripts/deploy_safe.ps1 }
    "3" { ./scripts/mirror_production.ps1 }
    "4" { Start-Process "OPS_MANUAL.md" }
    Default { Write-Host "Exiting." }
}
