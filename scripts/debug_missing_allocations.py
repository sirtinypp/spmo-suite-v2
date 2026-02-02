import sys
sys.path.append('/app')
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'office_supplies_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone
from supplies.models import AnnualProcurementPlan, UserProfile

def debug():
    print("--- Debugging Missing Allocations ---")
    
    # 1. Check User
    username = 'spmo_user' # Based on screenshot
    try:
        user = User.objects.get(username=username)
        print(f"User Found: {user.username} (ID {user.id})")
        if hasattr(user, 'profile'):
            dept = user.profile.department
            print(f"  Profile Dept: '{dept.name}' (ID {dept.id if dept else 'None'})")
        else:
            print("  NO PROFILE FOUND.")
            return
    except User.DoesNotExist:
        print(f"User '{username}' not found. checking all users...")
        for u in User.objects.all():
            d = u.profile.department.name if hasattr(u, 'profile') and u.profile.department else "None"
            print(f"  - {u.username}: {d}")
        return

    # 2. Check APP Years
    years = AnnualProcurementPlan.objects.values_list('year', flat=True).distinct()
    print(f"\nAvailable APP Years in DB: {list(years)}")
    
    current_year = timezone.now().year
    print(f"Current System Year: {current_year}")

    # 3. Check Allocations for User's Dept
    if hasattr(user, 'profile') and user.profile.department:
        target_dept = user.profile.department
        count_all = AnnualProcurementPlan.objects.filter(department=target_dept).count()
        count_current = AnnualProcurementPlan.objects.filter(department=target_dept, year=current_year).count()
        
        print(f"\nAllocations for '{target_dept.name}':")
        print(f"  - Total (All Years): {count_all}")
        print(f"  - Current Year ({current_year}): {count_current}")
        
        if count_all > 0 and count_current == 0:
            print("  -> PROBLEM: Data exists but not for the current year.")
            # Show which years have data
            data_years = AnnualProcurementPlan.objects.filter(department=target_dept).values_list('year', flat=True).distinct()
            print(f"  -> Data exists for years: {list(data_years)}")

if __name__ == '__main__':
    debug()
