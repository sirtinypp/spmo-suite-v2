import sys
sys.path.append('/app')
import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'office_supplies_project.settings')
django.setup()

from supplies.models import Product, AnnualProcurementPlan, UserProfile
from django.contrib.auth.models import User

def debug_catalog():
    print("--- Debugging Catalog Logic ---")
    
    username = 'spmo_user'
    try:
        user = User.objects.get(username=username)
        print(f"User: {user.username}")
        if hasattr(user, 'profile'):
            dept = user.profile.department
            print(f"Department: {dept.name} (ID {dept.id})")
        else:
            print("No Profile/Department found.")
            return
    except User.DoesNotExist:
        print("User not found.")
        return

    # Mimic client.py logic
    current_year = timezone.now().year
    print(f"Current Year: {current_year}")

    # 1. Get Allocated IDs
    allocated_ids = AnnualProcurementPlan.objects.filter(
        department=dept,
        year=current_year
    ).values_list('product_id', flat=True)
    
    print(f"Allocated Product IDs Count: {len(allocated_ids)}")
    print(f"Sample IDs: {list(allocated_ids)[:10]}")

    # 2. Filter Products
    products = Product.objects.all()
    filtered_products = products.filter(id__in=allocated_ids)
    
    print(f"Total Products in DB: {products.count()}")
    print(f"Products matching Allocation: {filtered_products.count()}")
    
    if len(allocated_ids) > 0 and filtered_products.count() == 0:
        print("CRITICAL: APP has Product IDs that do not exist in the Product table!")
        # Check a specific ID
        orphan_id = list(allocated_ids)[0]
        print(f"Checking orphan ID {orphan_id} in Product table...")
        exists = Product.objects.filter(id=orphan_id).exists()
        print(f"  Exists? {exists}")
    
    # 3. Personal Stock Logic
    allocations = AnnualProcurementPlan.objects.filter(
        department=dept, 
        year=current_year
    ).select_related('product')
    
    allocation_map = {a.product_id: a.remaining_balance() for a in allocations}
    print(f"Allocation Map Size: {len(allocation_map)}")
    
if __name__ == '__main__':
    debug_catalog()
