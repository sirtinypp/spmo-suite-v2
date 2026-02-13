import os
import django
import sys

# Setup Django Environment
sys.path.append('/app') # Docker path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from inventory.models import Asset, UserProfile

def analyze_data():
    print("--- UserProfile Offices ---")
    user_offices = UserProfile.objects.values_list('office', flat=True).distinct()
    for office in user_offices:
        print(f"  - {office}")

    print("\n--- Asset Assigned Offices ---")
    asset_offices = Asset.objects.values_list('assigned_office', flat=True).distinct()
    for office in asset_offices:
        print(f"  - {office}")

if __name__ == '__main__':
    try:
        analyze_data()
    except Exception as e:
        print(f"Error: {e}")
