import os
import django
from django.db.models import Count

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'office_supplies_project.settings')
django.setup()

from supplies.models import Department, Category, UserProfile, AnnualProcurementPlan
from django.contrib.auth.models import User

print("=== DUPLICATE CHECK REPORT ===")

# 1. Check Departments
print("\n--- Departments ---")
dupe_headers = Department.objects.values('name').annotate(c=Count('id')).filter(c__gt=1)
if dupe_headers:
    print(f"!! FOUND {len(dupe_headers)} Duplicate Department Names !!")
    for d in dupe_headers:
        print(f"  Duplicate Name: '{d['name']}' (Count: {d['c']})")
        objs = Department.objects.filter(name=d['name'])
        for o in objs:
            print(f"    - ID: {o.id}")
else:
    print("No Duplicate Department Names found.")

# 2. Check Categories
print("\n--- Categories ---")
dupe_cats = Category.objects.values('name').annotate(c=Count('id')).filter(c__gt=1)
if dupe_cats:
    print(f"!! FOUND {len(dupe_cats)} Duplicate Category Names !!")
    for d in dupe_cats:
         print(f"  Duplicate Name: '{d['name']}' (Count: {d['c']})")
         objs = Category.objects.filter(name=d['name'])
         for o in objs:
             print(f"    - ID: {o.id}")
else:
     print("No Duplicate Category Names found.")

# 3. Check User Linkage
print("\n--- User Linkage (spmo_user) ---")
try:
    user = User.objects.get(username='spmo_user')
    profile = user.profile
    if profile.department:
        print(f"User '{user.username}' is linked to Dept ID: {profile.department.id} ('{profile.department.name}')")
        
        # Check APP Allocations for this SPECIFIC ID
        app_count = AnnualProcurementPlan.objects.filter(department_id=profile.department.id, year=2026).count()
        print(f"Allocations linked to Dept ID {profile.department.id}: {app_count}")
        
    else:
        print(f"User '{user.username}' has NO Department linked.")
except User.DoesNotExist:
    print("User 'spmo_user' not found.")
except Exception as e:
    print(f"Error checking user: {e}")

print("=== END ===")
