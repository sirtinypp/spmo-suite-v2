$SERVERS = @("172.20.3.92", "172.20.3.91")
$PORT = "9913"
$USER = "ajbasa"
$REMOTE_BASE = "/home/ajbasa/spmo_suite"

$FILES = @(
    @{ local = "suplay_app/supplies/templates/supplies/emergency_form.html"; remote = "suplay_app/supplies/templates/supplies/emergency_form.html" },
    @{ local = "suplay_app/supplies/templates/supplies/requisition_slip.html"; remote = "suplay_app/supplies/templates/supplies/requisition_slip.html" },
    @{ local = "suplay_app/supplies/views/client.py"; remote = "suplay_app/supplies/views/client.py" },
    @{ local = "suplay_app/supplies/urls.py"; remote = "suplay_app/supplies/urls.py" },
    @{ local = "suplay_app/supplies/migrations/0025_emergencyrequest.py"; remote = "suplay_app/supplies/migrations/0025_emergencyrequest.py" },
    @{ local = "suplay_app/supplies/migrations/0026_order_is_emergency_alter_userprofile_role.py"; remote = "suplay_app/supplies/migrations/0026_order_is_emergency_alter_userprofile_role.py" },
    @{ local = "suplay_app/supplies/templates/supplies/admin_dashboard.html"; remote = "suplay_app/supplies/templates/supplies/admin_dashboard.html" },
    @{ local = "suplay_app/supplies/templates/supplies/inventory.html"; remote = "suplay_app/supplies/templates/supplies/inventory.html" },
    @{ local = "suplay_app/supplies/views/admin_views.py"; remote = "suplay_app/supplies/views/admin_views.py" },
    @{ local = "suplay_app/office_supplies_project/settings.py"; remote = "suplay_app/office_supplies_project/settings.py" },
    @{ local = "suplay_app/scratch/populate_safety_levels.py"; remote = "suplay_app/scratch/populate_safety_levels.py" }
)

foreach ($SERVER in $SERVERS) {
    Write-Host "--- DEPLOYING TO $SERVER ---" -ForegroundColor Cyan
    foreach ($item in $FILES) {
        $localPath = $item.local
        $remotePath = "$REMOTE_BASE/$($item.remote)"
        Write-Host "Syncing: $localPath -> $remotePath"
        scp -P $PORT $localPath "$($USER)@$($SERVER):$remotePath"
    }
}
