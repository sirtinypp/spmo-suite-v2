
import os
import django
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from inventory.models import (
    Asset, InspectionRequest, AssetBatch, AssetTransferRequest, 
    AssetReturnRequest, AssetLossReport, PropertyClearanceRequest,
    AssetNotification, ServiceLog, AssetChangeLog
)
from workflow.models import WorkflowMovementLog

def hard_reset():
    print("--- Hard Reset: Clearing All Injected Data ---")
    
    # 1. Clear All Transactions
    print("Clearing Transaction Tables...")
    AssetBatch.objects.all().delete()
    InspectionRequest.objects.all().delete()
    AssetTransferRequest.objects.all().delete()
    AssetReturnRequest.objects.all().delete()
    AssetLossReport.objects.all().delete()
    PropertyClearanceRequest.objects.all().delete()
    print("  [OK] All transaction requests deleted.")

    # 2. Clear All Assets and Logs
    print("Clearing Asset Registry and Logs...")
    Asset.objects.all().delete()
    ServiceLog.objects.all().delete()
    AssetChangeLog.objects.all().delete()
    AssetNotification.objects.all().delete()
    print("  [OK] Asset registry and audit logs deleted.")

    # 3. Clear Workflow Logs (just in case any orphaned)
    WorkflowMovementLog.objects.all().delete()
    print("  [OK] Workflow movement history wiped.")

    print("\n--- Cleanup Complete: The system is now empty and ready for manual testing. ---")

if __name__ == "__main__":
    hard_reset()
