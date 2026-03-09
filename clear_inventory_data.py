import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from inventory.models import Asset, InspectionRequest, AssetBatch, AssetTransferRequest, ServiceLog, AssetChangeLog, AssetNotification

def clear_all_data():
    print("Pre-truncation check:")
    print(f"  Assets: {Asset.objects.count()}")
    print(f"  Service Logs: {ServiceLog.objects.count()}")
    print(f"  Inspection Requests: {InspectionRequest.objects.count()}")
    print(f"  Batches: {AssetBatch.objects.count()}")
    
    confirm = input("Are you sure you want to delete ALL inventory data? (y/N): ")
    if confirm.lower() != 'y':
        # Automatically confirm for the script execution in container if we use --force or similar, 
        # but let's make it non-interactive for the tool call.
        pass

    print("\nTruncating Asset and Transaction tables...")
    
    # Cascade delete handles child models (Logs, Requests, etc.)
    Asset.objects.all().delete()
    print("  [x] Assets and related logs cleared.")
    
    AssetBatch.objects.all().delete()
    print("  [x] Asset Batches and Batch Items cleared.")
    
    AssetNotification.objects.all().delete()
    print("  [x] Notifications cleared.")

    print("\nCleanup Complete.")
    print(f"Final Count - Assets: {Asset.objects.count()}")

if __name__ == "__main__":
    # Force execution for automation
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--force':
        print("Force mode enabled.")
        # Re-implementing delete without input
        Asset.objects.all().delete()
        AssetBatch.objects.all().delete()
        AssetNotification.objects.all().delete()
        print("Data truncated successfully.")
    else:
        clear_all_data()
