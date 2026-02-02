import os
import django
from django.conf import settings
from django.utils import timezone

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'office_supplies_project.settings')
django.setup()

from supplies.models import UserProfile, Department, AnnualProcurementPlan, Product
from django.contrib.auth.models import User

print("=== DEBUG VISIBILITY REPORT ===")
print(f"Server Time: {timezone.now()}")
print(f"Server Year: {timezone.now().year}")

# 1. Check User Profiles
print("\n--- User Profiles ---")
for p in UserProfile.objects.select_related('user', 'department').all():
    print(f"User: {p.user.username} | Dept: {p.department.name if p.department else 'NONE'}")

# 2. Check APP Allocation for SSPMO
print("\n--- Checking APP Allocations (SSPMO 2026) ---")
try:
    sspmo = Department.objects.get(name__icontains="Supply")
    print(f"Found Dept: {sspmo.name}")
    
    allocs = AnnualProcurementPlan.objects.filter(department=sspmo, year=2026)
    print(f"Total Allocations for 2026: {allocs.count()}")
    
    if allocs.count() > 0:
        print("First 5 Items:")
        for a in allocs[:5]:
            print(f" - {a.product.name} (Approved: {a.quantity_approved}, Consumed: {a.quantity_consumed})")
    else:
        print("NO ALLOCATIONS FOUND FOR 2026!")

except Department.DoesNotExist:
    print("CRITICAL: SSPMO Department NOT FOUND in DB.")

# 3. Check Airline Tickets Specifically
print("\n--- Checking Airline Tickets ---")
tickets = AnnualProcurementPlan.objects.filter(product__name__icontains="Airline", year=2026)
for t in tickets:
    print(f"Found Ticket Allocation for: {t.department.name} (Year {t.year})")

print("=== END REPORT ===")
