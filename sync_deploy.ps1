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
    @{ local = "suplay_app/supplies/templates/supplies/admin_base.html"; remote = "suplay_app/supplies/templates/supplies/admin_base.html" },
    @{ local = "suplay_app/supplies/templates/supplies/order_detail.html"; remote = "suplay_app/supplies/templates/supplies/order_detail.html" },
    @{ local = "suplay_app/supplies/templates/supplies/transactions.html"; remote = "suplay_app/supplies/templates/supplies/transactions.html" },
    @{ local = "suplay_app/supplies/templates/supplies/inventory.html"; remote = "suplay_app/supplies/templates/supplies/inventory.html" },
    @{ local = "suplay_app/supplies/views/admin_views.py"; remote = "suplay_app/supplies/views/admin_views.py" },
    @{ local = "suplay_app/office_supplies_project/settings.py"; remote = "suplay_app/office_supplies_project/settings.py" },
    @{ local = "suplay_app/supplies/templates/supplies/app_registry.html"; remote = "suplay_app/supplies/templates/supplies/app_registry.html" },
    @{ local = "suplay_app/supplies/templates/supplies/apr_list.html"; remote = "suplay_app/supplies/templates/supplies/apr_list.html" },
    @{ local = "suplay_app/supplies/templates/supplies/apr_detail.html"; remote = "suplay_app/supplies/templates/supplies/apr_detail.html" },
    @{ local = "suplay_app/supplies/migrations/0027_procurementdocument.py"; remote = "suplay_app/supplies/migrations/0027_procurementdocument.py" },
    @{ local = "suplay_app/supplies/migrations/0028_aprrequest_has_unregistered_items_and_more.py"; remote = "suplay_app/supplies/migrations/0028_aprrequest_has_unregistered_items_and_more.py" },
    @{ local = "suplay_app/supplies/migrations/0029_apritem_remarks_alter_apritem_product.py"; remote = "suplay_app/supplies/migrations/0029_apritem_remarks_alter_apritem_product.py" },
    @{ local = "suplay_app/supplies/migrations/0030_order_dv_file_order_dv_no_order_dv_uploaded_at_and_more.py"; remote = "suplay_app/supplies/migrations/0030_order_dv_file_order_dv_no_order_dv_uploaded_at_and_more.py" },
    @{ local = "suplay_app/supplies/models.py"; remote = "suplay_app/supplies/models.py" },
    @{ local = "suplay_app/supplies/templatetags/supply_extras.py"; remote = "suplay_app/supplies/templatetags/supply_extras.py" },
    @{ local = "suplay_app/supplies/templatetags/__init__.py"; remote = "suplay_app/supplies/templatetags/__init__.py" },
    @{ local = "suplay_app/supplies/templates/supplies/profile.html"; remote = "suplay_app/supplies/templates/supplies/profile.html" },
    @{ local = "suplay_app/supplies/templates/supplies/delivery.html"; remote = "suplay_app/supplies/templates/supplies/delivery.html" }
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
