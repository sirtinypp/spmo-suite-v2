import os
import django
import sys

# Setup Django Environment
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from inventory.models import Asset, UserProfile, Department

def verify_data():
    print("--- Verifying Department FKs ---")
    
    # 1. Assets
    total_assets = Asset.objects.count()
    linked_assets = Asset.objects.filter(department__isnull=False).count()
    print(f"Total Assets: {total_assets}")
    print(f"Assets with Linked Department: {linked_assets}")
    
    if total_assets != linked_assets:
        print(f"WARNING: {total_assets - linked_assets} assets do not have a department!")
        # Debug missing ones
        missing = Asset.objects.filter(department__isnull=True).exclude(assigned_office='').exclude(assigned_office__isnull=True)
        if missing.exists():
            print("  Samples Missing:")
            for a in missing[:5]:
                print(f"    - {a.property_number} (Office: '{a.assigned_office}')")

    # 2. Users
    total_users = UserProfile.objects.count()
    linked_users = UserProfile.objects.filter(department__isnull=False).count()
    print(f"\nTotal Users: {total_users}")
    print(f"Users with Linked Department: {linked_users}")

if __name__ == '__main__':
    verify_data()
