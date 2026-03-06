# ==============================================================================
# SPMO SUITE - DAILY STARTUP HEALTH CHECK v2.0
# ==============================================================================
# Run: powershell -File scripts/daily_startup.ps1
# Part of the JARVIS Startup Protocol
# Last Updated: 2026-03-04
# ==============================================================================

param(
    [switch]$SkipRemote
)

$ErrorActionPreference = "SilentlyContinue"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   SPMO SUITE - DAILY STARTUP HEALTH CHECK" -ForegroundColor Cyan
Write-Host "   $timestamp" -ForegroundColor Gray
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ==============================================================================
# PHASE 1: Docker Engine Check
# ==============================================================================

Write-Host "[Phase 1] Docker Engine" -ForegroundColor Yellow
docker info > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [CRITICAL] Docker is NOT running!" -ForegroundColor Red
    Write-Host "  Please start Docker Desktop and run this script again." -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] Docker Engine is active." -ForegroundColor Green
Write-Host ""

# ==============================================================================
# PHASE 2: Local Container Check (All 6)
# ==============================================================================

Write-Host "[Phase 2] Local Containers" -ForegroundColor Yellow

$ContainerNames = @("spmo_gateway", "spmo_shared_db", "app_hub", "app_gamit", "app_gfa", "app_store")
$ServiceLabels = @("Nginx Gateway", "PostgreSQL 15", "SPMO Hub", "GAMIT", "LIPAD", "SUPLAY")
$Ports = @("80", "5432", "8000", "8001", "8002", "8003")

$RunningRaw = docker ps --format "{{.Names}}" 2>&1
$RunningContainers = $RunningRaw -split "`n"
$upCount = 0
$downCount = 0

for ($i = 0; $i -lt $ContainerNames.Count; $i++) {
    $name = $ContainerNames[$i]
    $service = $ServiceLabels[$i]
    $port = $Ports[$i]

    if ($RunningContainers -contains $name) {
        Write-Host "  [UP]   $name ($service) :$port" -ForegroundColor Green
        $upCount++
    }
    else {
        Write-Host "  [DOWN] $name ($service) :$port" -ForegroundColor Red
        $downCount++
    }
}

Write-Host ""
if ($downCount -gt 0) {
    Write-Host "  Result: $upCount/6 containers running, $downCount DOWN" -ForegroundColor Red
    Write-Host "  Recommendation: docker compose up -d" -ForegroundColor Yellow
}
else {
    Write-Host "  Result: 6/6 containers running" -ForegroundColor Green
}
Write-Host ""

# ==============================================================================
# PHASE 3: Git Status
# ==============================================================================

Write-Host "[Phase 3] Git Status" -ForegroundColor Yellow

$branch = git branch --show-current 2>&1
$headCommit = git log --oneline -1 2>&1
$statusOutput = git status --short 2>&1

Write-Host "  Branch: $branch" -ForegroundColor White
Write-Host "  HEAD:   $headCommit" -ForegroundColor White

if ([string]::IsNullOrWhiteSpace($statusOutput)) {
    Write-Host "  Tree:   Clean" -ForegroundColor Green
}
else {
    $lines = @($statusOutput -split "`n")
    $fileCount = $lines.Count
    Write-Host "  Tree:   $fileCount modified/untracked files" -ForegroundColor Yellow
}
Write-Host ""

# ==============================================================================
# PHASE 4: Remote Server Checks (Dev + Prod)
# ==============================================================================

if (-not $SkipRemote) {
    Write-Host "[Phase 4] Remote Servers" -ForegroundColor Yellow

    # Dev Server
    Write-Host "  Checking Dev (172.20.3.92:9913)..." -ForegroundColor Gray
    $devResult = ssh -o ConnectTimeout=5 -o BatchMode=yes -p 9913 ajbasa@172.20.3.92 "docker ps --format '{{.Names}}' | wc -l" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Dev: $devResult containers running" -ForegroundColor Green
    }
    else {
        Write-Host "  [WARN] Dev: UNREACHABLE" -ForegroundColor Yellow
    }

    # Prod Server
    Write-Host "  Checking Prod (172.20.3.91:9913)..." -ForegroundColor Gray
    $prodResult = ssh -o ConnectTimeout=5 -o BatchMode=yes -p 9913 ajbasa@172.20.3.91 "docker ps --format '{{.Names}}' | wc -l" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Prod: $prodResult containers running" -ForegroundColor Green
    }
    else {
        Write-Host "  [WARN] Prod: UNREACHABLE" -ForegroundColor Yellow
    }
    Write-Host ""
}
else {
    Write-Host "[Phase 4] Remote Servers (SKIPPED)" -ForegroundColor Gray
    Write-Host ""
}

# ==============================================================================
# PHASE 5: Disk Space
# ==============================================================================

Write-Host "[Phase 5] Disk Space" -ForegroundColor Yellow

$drives = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Used -gt 0 }
foreach ($drive in $drives) {
    $total = [math]::Round($drive.Used / 1GB + $drive.Free / 1GB, 1)
    $free = [math]::Round($drive.Free / 1GB, 1)
    $usedPct = [math]::Round(($drive.Used / ($drive.Used + $drive.Free)) * 100, 0)
    $driveName = $drive.Name

    if ($usedPct -ge 90) {
        Write-Host "  [$driveName`:] $free GB free of $total GB ($usedPct% used)" -ForegroundColor Red
    }
    elseif ($usedPct -ge 75) {
        Write-Host "  [$driveName`:] $free GB free of $total GB ($usedPct% used)" -ForegroundColor Yellow
    }
    else {
        Write-Host "  [$driveName`:] $free GB free of $total GB ($usedPct% used)" -ForegroundColor Green
    }
}
Write-Host ""

# ==============================================================================
# SUMMARY
# ==============================================================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   HEALTH CHECK COMPLETE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if ($downCount -gt 0) {
    Write-Host "  ACTION NEEDED: $downCount container(s) are down." -ForegroundColor Red
    Write-Host ""
    $choice = Read-Host "  Start all containers now? (y/N)"
    if ($choice -eq "y" -or $choice -eq "Y") {
        Write-Host "  Starting containers..." -ForegroundColor Cyan
        docker compose up -d
        Write-Host "  Done." -ForegroundColor Green
    }
}
else {
    Write-Host "  All systems nominal. Ready for JARVIS." -ForegroundColor Green
}
Write-Host ""
