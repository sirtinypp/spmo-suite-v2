#!/usr/bin/env pwsh
# Production Health Check Script
# Purpose: Verify SPMO Suite production server status
# Run this before and after any deployment

param(
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"
$server = "ajbasa@172.20.3.91"
$port = 9913

Write-Host "================================" -ForegroundColor Cyan
Write-Host "SPMO Production Health Check" -ForegroundColor Cyan
Write-Host "Server: 172.20.3.91" -ForegroundColor Cyan
Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Container Status
Write-Host "[1/3] Container Status Check..." -ForegroundColor Yellow
$containerCheck = ssh -p $port $server "docker ps --format 'table {{.Names}}\t{{.Status}}'"
Write-Host $containerCheck
Write-Host ""

# Expected containers
$expectedContainers = @(
    "spmo_gateway",
    "app_hub",
    "app_gamit",
    "app_gfa",
    "app_store",
    "spmo_shared_db"
)

$runningContainers = ssh -p $port $server "docker ps --format '{{.Names}}'" | Out-String
$allRunning = $true
foreach ($container in $expectedContainers) {
    if ($runningContainers -notmatch $container) {
        Write-Host "  ❌ CRITICAL: $container is NOT running!" -ForegroundColor Red
        $allRunning = $false
    }
    else {
        if ($Verbose) {
            Write-Host "  ✅ $container is running" -ForegroundColor Green
        }
    }
}

if ($allRunning) {
    Write-Host "  ✅ All 6 containers are running" -ForegroundColor Green
}
else {
    Write-Host "  🚨 ALERT: Some containers are down!" -ForegroundColor Red
}
Write-Host ""

# Test 2: Domain Accessibility
Write-Host "[2/3] Domain Accessibility Check..." -ForegroundColor Yellow
$domains = @(
    "sspmo.up.edu.ph",
    "gamit-sspmo.up.edu.ph",
    "suplay-sspmo.up.edu.ph",
    "lipad-sspmo.up.edu.ph"
)

$allDomainsUp = $true
foreach ($domain in $domains) {
    try {
        $response = Invoke-WebRequest -Uri "http://$domain" -Method Head -TimeoutSec 5 -ErrorAction Stop
        $statusCode = $response.StatusCode
        if ($statusCode -eq 200) {
            Write-Host "  ✅ $domain → HTTP $statusCode" -ForegroundColor Green
        }
        else {
            Write-Host "  ⚠️  $domain → HTTP $statusCode" -ForegroundColor Yellow
            $allDomainsUp = $false
        }
    }
    catch {
        Write-Host "  ❌ $domain → FAILED ($($_.Exception.Message))" -ForegroundColor Red
        $allDomainsUp = $false
    }
}

if ($allDomainsUp) {
    Write-Host "  ✅ All domains accessible" -ForegroundColor Green
}
else {
    Write-Host "  🚨 ALERT: Some domains are inaccessible!" -ForegroundColor Red
}
Write-Host ""

# Test 3: Configuration Integrity
Write-Host "[3/3] Configuration Integrity Check..." -ForegroundColor Yellow

# Check .env for hyphenated domains
$envCheck = ssh -p $port $server "cat spmo_suite/.env | grep 'gamit-sspmo'"
if ($envCheck -match "gamit-sspmo") {
    Write-Host "  ✅ .env has correct hyphenated domains" -ForegroundColor Green
}
else {
    Write-Host "  ❌ .env is missing hyphenated domains!" -ForegroundColor Red
}

# Check nginx config syntax
$nginxCheck = ssh -p $port $server "docker exec spmo_gateway nginx -t 2>&1"
if ($nginxCheck -match "successful") {
    Write-Host "  ✅ Nginx configuration valid" -ForegroundColor Green
}
else {
    Write-Host "  ❌ Nginx configuration has errors!" -ForegroundColor Red
    Write-Host "     $nginxCheck" -ForegroundColor Red
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
if ($allRunning -and $allDomainsUp) {
    Write-Host "✅ PRODUCTION STATUS: HEALTHY" -ForegroundColor Green
}
else {
    Write-Host "🚨 PRODUCTION STATUS: DEGRADED" -ForegroundColor Red
    Write-Host "   Action Required: Review errors above" -ForegroundColor Red
}
Write-Host "================================" -ForegroundColor Cyan
