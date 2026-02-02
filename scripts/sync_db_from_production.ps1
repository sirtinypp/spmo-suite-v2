# Database Sync: Production → Local
# SPMO Suite v1.0.1
# Syncs remote database to local for development with real data

# Step 1: Backup production database
Write-Host "Step 1: Creating production database backup..." -ForegroundColor Cyan
ssh -p 9913 ajbasa@172.20.3.91 "docker exec spmo_shared_db pg_dump -U spmo_admin db_store > ~/backups/db_store_$(date +%Y%m%d_%H%M%S).sql"

# Step 2: Download latest backup
Write-Host "Step 2: Downloading database backup..." -ForegroundColor Cyan
scp -P 9913 "ajbasa@172.20.3.91:~/backups/db_store_*.sql" "c:\Users\Aaron\spmo-suite - Copy\db_backup.sql"

# Step 3: Stop local containers
Write-Host "Step 3: Stopping local containers..." -ForegroundColor Cyan
docker compose -f "c:\Users\Aaron\spmo-suite - Copy\docker-compose.yml" down

# Step 4: Start only database
Write-Host "Step 4: Starting database container..." -ForegroundColor Cyan
docker compose -f "c:\Users\Aaron\spmo-suite - Copy\docker-compose.yml" up -d db

Start-Sleep -Seconds 5

# Step 5: Drop and recreate database
Write-Host "Step 5: Recreating local database..." -ForegroundColor Cyan
docker exec spmo_shared_db psql -U spmo_admin -d postgres -c "DROP DATABASE IF EXISTS db_store;"
docker exec spmo_shared_db psql -U spmo_admin -d postgres -c "CREATE DATABASE db_store OWNER spmo_admin;"

# Step 6: Restore backup
Write-Host "Step 6: Restoring production data to local..." -ForegroundColor Cyan
Get-Content "c:\Users\Aaron\spmo-suite - Copy\db_backup.sql" | docker exec -i spmo_shared_db psql -U spmo_admin -d db_store

# Step 7: Start all containers
Write-Host "Step 7: Starting all containers..." -ForegroundColor Cyan
docker compose -f "c:\Users\Aaron\spmo-suite - Copy\docker-compose.yml" up -d

Start-Sleep -Seconds 5

# Step 8: Verify
Write-Host "Step 8: Verifying data sync..." -ForegroundColor Cyan
docker exec app_store python manage.py shell -c "from supplies.models import AnnualProcurementPlan, Product, Department; print(f'APP Allocations: {AnnualProcurementPlan.objects.count()}'); print(f'Products: {Product.objects.count()}'); print(f'Departments: {Department.objects.count()}')"

Write-Host "`nDatabase sync complete!" -ForegroundColor Green
Write-Host "You can now develop locally with production data." -ForegroundColor Green
