import os
import sys
import django

# Setup Django Environment
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from django.contrib.auth.models import User
from inventory.models import Asset, UserProfile, Department

def test_filtering():
    print("--- Setting up Test Data ---")
    # 1. Create Departments
    dept_a, _ = Department.objects.get_or_create(name="Dept A")
    dept_b, _ = Department.objects.get_or_create(name="Dept B")
    print(f"Departments: {dept_a}, {dept_b}")

    # 2. Create User linked to Dept A
    username = "filter_user"
    if User.objects.filter(username=username).exists():
        User.objects.filter(username=username).delete()
    
    user = User.objects.create_user(username=username, password="password")
    # Signal should create profile, but let's ensure department is set
    profile = UserProfile.objects.get(user=user)
    profile.department = dept_a
    profile.save()
    print(f"User {user.username} assigned to {profile.department}")

    # 3. Create Assets
    from django.utils import timezone
    today = timezone.now().date()
    asset_a = Asset.objects.create(property_number="A-001", name="Asset A", department=dept_a, assigned_office="Dept A Legacy", date_acquired=today)
    asset_b = Asset.objects.create(property_number="B-001", name="Asset B", department=dept_b, assigned_office="Dept B Legacy", date_acquired=today)
    print(f"Created Assets: {asset_a.name} ({asset_a.department}), {asset_b.name} ({asset_b.department})")

    print("\n--- Testing Filtering Logic ---")
    user.refresh_from_db() # Refresh to get updated profile
    # Simulate View Logic
    assets = Asset.objects.all()
    user_department = None
    if not user.is_staff:
        try:
            p = user.userprofile
            user_department = p.department
            if user_department:
                assets = assets.filter(department=user_department)
            else:
                assets = Asset.objects.none()
        except:
            assets = Asset.objects.none()
    
    print(f"User is staff? {user.is_staff}")
    print(f"User Dept: {user_department}")
    print(f"Filtered Assets Count: {assets.count()}")
    for a in assets:
        print(f" - Found: {a.name} ({a.department})")

    if assets.count() == 1 and assets.first() == asset_a:
        print("[SUCCESS] Filtering works correctly.")
    else:
        print("[FAILURE] Filtering logic failed.")

    print("\n--- Testing Auto-Assignment Logic ---")
    # Simulate Add Asset Logic
    new_asset = Asset(property_number="C-001", name="Asset C", date_acquired=today)
    if not user.is_staff:
        try:
            p = user.userprofile
            new_asset.assigned_office = p.office or "Legacy Office"
            new_asset.department = p.department
        except:
            pass
    new_asset.save()
    
    print(f"Created {new_asset.name}. Department: {new_asset.department}")
    if new_asset.department == dept_a:
        print("[SUCCESS] Auto-assignment works correctly.")
    else:
        print("[FAILURE] Auto-assignment failed.")

    # Cleanup
    asset_a.delete()
    asset_b.delete()
    new_asset.delete()
    user.delete()
    # Depts might be used by others, keep them or delete if clean
    if dept_a.asset_set.count() == 0: dept_a.delete()
    if dept_b.asset_set.count() == 0: dept_b.delete()

if __name__ == '__main__':
    test_filtering()
