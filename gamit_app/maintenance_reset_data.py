import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from inventory.models import (
    Asset, AssetBatch, BatchItem, AssetChangeLog, 
    AssetNotification, ServiceLog, InspectionRequest, 
    AssetTransferRequest, ApprovalLog
)
from django.db import transaction

def purge_data():
    print("Starting GAMIT data purge...")
    
    with transaction.atomic():
        # Delete dependent items first
        print("Purging related logs, items, and requests...")
        AssetChangeLog.objects.all().delete()
        AssetNotification.objects.all().delete()
        ServiceLog.objects.all().delete()
        InspectionRequest.objects.all().delete()
        AssetTransferRequest.objects.all().delete()
        ApprovalLog.objects.all().delete()
        BatchItem.objects.all().delete()
        AssetBatch.objects.all().delete()
        
        # Finally delete main assets
        asset_count_start = Asset.objects.count()
        print(f"Purging {asset_count_start} Assets...")
        Asset.objects.all().delete()
        
        print("✅ Successfully purged all asset-related data.")
        print(f"Final Count - Assets: {Asset.objects.count()}")

if __name__ == "__main__":
    purge_data()
