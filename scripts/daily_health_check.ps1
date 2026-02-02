# SPMO Suite Daily Health Check (PowerShell)
# Version: 1.0.0
# Run this daily to monitor system health

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SPMO Suite Health Check - $(Get-Date)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Container Status
Write-Host "Container Status:" -ForegroundColor Yellow
docker ps --format "table {{.Names}}`t{{.Status}}`t{{.Ports}}"
Write-Host ""

# 2. Application Health
Write-Host "Application Health:" -ForegroundColor Yellow
$ports = @{
    8000 = "SPMO Hub"
    8001 = "GAMIT   "
    8002 = "LIPAD   "
    8003 = "SUPLAY  "
}

foreach ($port in $ports.Keys | Sort-Object) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$port" -Method Head -TimeoutSec 5 -ErrorAction Stop
        Write-Host "  OK: $($ports[$port]) (port $port)" -ForegroundColor Green
    }
    catch {
        Write-Host "  FAILED: $($ports[$port]) (port $port)" -ForegroundColor Red
    }
}
Write-Host ""

# 3. Recent Errors
Write-Host "Recent Errors:" -ForegroundColor Yellow
$containers = @("app_hub", "app_gamit", "app_gfa", "app_store")
foreach ($container in $containers) {
    $errors = docker logs $container --since 24h 2>&1 | Select-String -Pattern "error"
    if ($errors.Count -gt 0) {
        Write-Host "  $container`: $($errors.Count) errors" -ForegroundColor Red
        $errors | Select-Object -First 2 | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
    }
}
Write-Host ""

# 4. Docker Resources
Write-Host "Docker Resources:" -ForegroundColor Yellow
docker system df
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "HEALTH CHECK COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host "- Review any errors above"
Write-Host "- Check detailed logs: docker logs [container_name]"
Write-Host "- Verify applications in browser if needed"
Write-Host ""
