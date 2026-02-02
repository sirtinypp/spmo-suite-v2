import os
import sys
import django
from django.utils import timezone

# Setup Django
sys.path.append(os.getcwd())
# Inject Env Vars for Local DB Access
os.environ['DB_NAME'] = 'db_store'
os.environ['DB_USER'] = 'spmo_admin'
os.environ['DB_PASSWORD'] = 'secret_password'
os.environ['DB_HOST'] = 'localhost'
os.environ['DJANGO_ALLOWED_HOSTS'] = 'localhost'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'office_supplies_project.settings')
django.setup()

from django.contrib.auth.models import User
from supplies.models import Product, AnnualProcurementPlan

def trace_visibility(username):
    print(f"=== VISIBILITY TRACE FOR: {username} ===")
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"User {username} not found!")
        return

    # 1. Setup Context
    user_department = None
    if hasattr(user, 'profile'):
        user_department = user.profile.department
        print(f"Department: {user_department.name} (ID: {user_department.id})")
    else:
        print("No profile/department found.")
        return

    # 2. Replicate 'home' view Logic
    print("\n--- 'home' View Logic Trace ---")
    current_year = timezone.now().year
    target_years = [2025, 2026, current_year]
    print(f"Target Years: {target_years}")

    allocations = AnnualProcurementPlan.objects.filter(
        department=user_department, 
        year__in=target_years
    ).select_related('product')
    
    print(f"Allocations Query Count: {allocations.count()}")
    
    if allocations.count() > 0:
        print("Sample Allocation Years:", list(allocations.values_list('year', flat=True).distinct()))

    allocated_product_ids = [a.product_id for a in allocations]
    print(f"Allocated Product IDs Count: {len(allocated_product_ids)}")
    if len(allocated_product_ids) > 0:
        print(f"Sample Product IDs: {allocated_product_ids[:5]}")

    # Base Product Query
    products = Product.objects.select_related('category', 'supplier').all().order_by('category__name', 'name')
    print(f"Base Product Count: {products.count()}")

    # Filter
    products_filtered = products.filter(id__in=allocated_product_ids)
    print(f"Filtered Product Count: {products_filtered.count()}")

    # 3. Compare with 'my_app_status' View Logic
    print("\n--- 'my_app_status' View Logic Trace ---")
    my_app_allocs = AnnualProcurementPlan.objects.filter(
        department=user_department, 
        year=timezone.now().year
    )
    print(f"My App Allocs (Year {timezone.now().year}): {my_app_allocs.count()}")

    # 4. Check for Mismatch?
    if my_app_allocs.count() > 0 and products_filtered.count() == 0:
        print("\n[DIAGNOSTIC] Mismatch Detected!")
        # Check if product IDs from my_app_allocs exist in Product table
        my_app_pids = list(my_app_allocs.values_list('product_id', flat=True))
        print(f"My App Product IDs: {my_app_pids[:5]}")
        
        exist_check = Product.objects.filter(id__in=my_app_pids).count()
        print(f"Do these Product IDs exist in Product table? Count: {exist_check}")
        
        if exist_check < len(my_app_pids):
             print("WARNING: Some APP entries point to non-existent products??")

if __name__ == "__main__":
    trace_visibility('sao_user2')
