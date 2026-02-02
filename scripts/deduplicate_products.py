import os
import django

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'suplay_project.settings')
django.setup()

from supplies.models import Product, AnnualProcurementPlan, OrderItem, StockBatch
from django.db.models import Count, Sum

def deduplicate():
    print("--- Checking for Duplicate Products by Item Code ---")
    
    # 1. Find duplicates
    duplicates = Product.objects.values('item_code').annotate(count=Count('id')).filter(count__gt=1, item_code__isnull=False)
    
    if not duplicates:
        print("No duplicates found!")
        return

    print(f"Found {len(duplicates)} Item Codes with duplicates.")

    for entry in duplicates:
        code = entry['item_code']
        products = list(Product.objects.filter(item_code=code).order_by('-stock', '-id'))
        
        # Strategy: Keep the one with the most stock, or the latest one created
        keeper = products[0]
        spares = products[1:]
        
        print(f"\nProcessing '{code}': Keeping ID {keeper.id} (Stock: {keeper.stock}). Merging {len(spares)} spares.")
        
        for spare in spares:
            print(f"  - Merging Spare ID {spare.id} (Stock: {spare.stock})...")
            
            # A. Re-point APP Allocations
            # Check if keeper already has an APP for the same Dept+Year?
            # If so, we might need to merge quantities. If not, just update FK.
            apps = AnnualProcurementPlan.objects.filter(product=spare)
            for app in apps:
                # Check collision
                existing = AnnualProcurementPlan.objects.filter(product=keeper, department=app.department, year=app.year).first()
                if existing:
                    print(f"    - Merging APP Plan for {app.department}...")
                    existing.jan += app.jan
                    existing.feb += app.feb
                    existing.mar += app.mar
                    existing.apr += app.apr
                    existing.may += app.may
                    existing.jun += app.jun
                    existing.jul += app.jul
                    existing.aug += app.aug
                    existing.sep += app.sep
                    existing.oct += app.oct
                    existing.nov += app.nov
                    existing.dec += app.dec
                    existing.quantity_consumed += app.quantity_consumed
                    existing.save()
                    app.delete()
                else:
                    print(f"    - Moving APP Plan for {app.department}...")
                    app.product = keeper
                    app.save()

            # B. Re-point Order Items
            OrderItem.objects.filter(product=spare).update(product=keeper)
            
            # C. Re-point Stock Batches
            StockBatch.objects.filter(product=spare).update(product=keeper)
            
            # D. Merge Stock (if spare had stock)
            if spare.stock > 0:
                keeper.stock += spare.stock
                keeper.save()
            
            # E. Delete Spare
            print(f"    - Deleting Spare ID {spare.id}")
            spare.delete()

    print("\n--- Deduplication Complete ---")

if __name__ == '__main__':
    deduplicate()
