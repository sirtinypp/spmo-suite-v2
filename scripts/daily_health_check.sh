#!/bin/bash
# SPMO Suite Daily Health Check
# Version: 1.0.0
# Run this daily to monitor system health

echo "========================================"
echo "SPMO Suite Health Check - $(date)"
echo "========================================"
echo ""

# 1. Container Status
echo "📦 CONTAINER STATUS:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "NAMES|spmo|app_"
echo ""

# 2. Resource Usage
echo "💻 RESOURCE USAGE:"
echo "CPU Load:"
uptime | awk '{print "  Load Average: " $(NF-2) " " $(NF-1) " " $NF}'
echo "Memory:"
free -h | awk 'NR==2{printf "  Used: %s / %s (%.2f%%)\n", $3, $2, $3/$2 * 100.0}'
echo "Disk:"
df -h / | awk 'NR==2{printf "  Used: %s / %s (%s)\n", $3, $2, $5}'
echo ""

# 3. Application Health
echo "🏥 APPLICATION HEALTH:"
for PORT in 8000 8001 8002 8003; do
    APP_NAME=$(case $PORT in
        8000) echo "SPMO Hub";;
        8001) echo "GAMIT   ";;
        8002) echo "LIPAD   ";;
        8003) echo "SUPLAY  ";;
    esac)
    
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT 2>/dev/null)
    if [ "$STATUS" = "200" ] || [ "$STATUS" = "302" ]; then
        echo "  ✅ $APP_NAME (port $PORT): OK"
    else
        echo "  ❌ $APP_NAME (port $PORT): FAILED (HTTP $STATUS)"
    fi
done
echo ""

# 4. Recent Errors
echo "⚠️  RECENT ERRORS (last 10):"
for CONTAINER in app_hub app_gamit app_gfa app_store; do
    ERROR_COUNT=$(docker logs $CONTAINER --since 24h 2>&1 | grep -i error | wc -l)
    if [ $ERROR_COUNT -gt 0 ]; then
        echo "  $CONTAINER: $ERROR_COUNT errors"
        docker logs $CONTAINER --since 24h 2>&1 | grep -i error | tail -2 | sed 's/^/    /'
    fi
done
echo ""

# 5. Database Status
echo "🗄️  DATABASE:"
DB_SIZE=$(docker exec spmo_shared_db psql -U spmo_admin -d postgres -t -c "SELECT pg_size_pretty(pg_database_size('postgres'));" 2>/dev/null | xargs)
if [ -n "$DB_SIZE" ]; then
    echo "  Database Size: $DB_SIZE"
    echo "  Status: ✅ Connected"
else
    echo "  Status: ❌ Cannot connect"
fi
echo ""

# 6. Summary
echo "========================================"
echo "HEALTH CHECK COMPLETE"
echo "========================================"
echo ""
echo "Next steps:"
echo "- Review any errors above"
echo "- Check detailed logs if needed: docker logs <container>"
echo "- Verify applications in browser if issues found"
echo ""
