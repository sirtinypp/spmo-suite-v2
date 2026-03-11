import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from inventory.models import Asset, InventoryBatch, AssetMedia
from django.db import transaction

def purge_data():
    print("Starting GAMIT data purge...")
    
    with transaction.atomic():
        # Count records before deletion
        asset_count = Asset.objects.count()
        batch_count = InventoryBatch.objects.count()
        media_count = AssetMedia.objects.count()
        
        print(f"Detecting: {asset_count} Assets, {batch_count} Batches, {media_count} Media entries.")
        
        # Delete records
        Asset.objects.all().delete()
        InventoryBatch.objects.all().delete()
        AssetMedia.objects.all().delete()
        
        print("Successfully purged all asset-related data.")
        print(f"Final Count - Assets: {Asset.objects.count()}, Batches: {InventoryBatch.objects.count()}")

if __name__ == "__main__":
    purge_data()
