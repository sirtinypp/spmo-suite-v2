import os
import django
from django.conf import settings
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'office_supplies_project.settings')
django.setup()

from supplies.models import UserProfile, Department, AnnualProcurementPlan, Product, StockBatch

print("=== ID MATCH REPORT ===")
# 1. Get Product IDs from StockBatch (SSPMO relevant?)
# Actually looking for "Airline Tickets"
products = Product.objects.filter(name__icontains="Airline")
for p in products:
    print(f"\nProduct: {p.name} (ID: {p.id})")
    print(f"  > Global Stock: {p.stock}")
    
    # Check Batches
    batches = StockBatch.objects.filter(product=p)
    print(f"  > Batches: {batches.count()} (Total Initial: {sum(b.quantity_initial for b in batches)})")

    # Check APP for SSPMO
    sspmo = Department.objects.get(name__icontains="Supply")
    app = AnnualProcurementPlan.objects.filter(department=sspmo, product=p, year=2026).first()
    
    if app:
        print(f"  > APP (SSPMO 2026): FOUND (ID: {app.id})")
        print(f"    - Approved: {app.quantity_approved}")
        print(f"    - Consumed: {app.quantity_consumed}")
        print(f"    - Remaining: {app.remaining_balance()}")
    else:
        print(f"  > APP (SSPMO 2026): NOT FOUND")

print("=== END ===")
