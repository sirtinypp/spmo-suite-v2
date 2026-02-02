from django.core.management.base import BaseCommand
from supplies.models import Product, AnnualProcurementPlan, OrderItem, StockBatch
from django.db.models import Count

class Command(BaseCommand):
    help = 'Deduplicates Products based on item_code, keeping the one with most stock/ID.'

    def handle(self, *args, **kwargs):
        self.stdout.write("--- Aggressive Deduplication (Case-Insensitive + Stripped) ---")
        
        # 1. Normalize DB: Strip all whitespace
        all_products = Product.objects.all()
        for p in all_products:
            if p.item_code:
                clean_code = p.item_code.strip()
                if p.item_code != clean_code:
                    p.item_code = clean_code
                    p.save()

        # 2. Find duplicates via Python (simpler than complex SQL grouping for now)
        # Dictionary: normalized_code -> list of products
        code_map = {}
        
        for p in Product.objects.all():
            # Key = lowercase, stripped
            key = p.item_code.strip().lower()
            if key not in code_map:
                code_map[key] = []
            code_map[key].append(p)

        # 3. Process Duplicates
        duplicates_found = 0
        for code_key, products in code_map.items():
            if len(products) > 1:
                duplicates_found += 1
                
                # Order: Most stock first, then newest ID
                products.sort(key=lambda x: (-x.stock, -x.id))
                
                keeper = products[0]
                spares = products[1:]
                
                self.stdout.write(f"\nProcessing '{code_key}': Found {len(products)} matches. Keeping ID {keeper.id} ({keeper.item_code}).")
                
                for spare in spares:
                    self.stdout.write(f"  - Merging Spare ID {spare.id} ({spare.item_code})...")
                    
                    # A. Re-point APP Allocations
                    apps = AnnualProcurementPlan.objects.filter(product=spare)
                    for app in apps:
                        existing = AnnualProcurementPlan.objects.filter(product=keeper, department=app.department, year=app.year).first()
                        if existing:
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
                            app.product = keeper
                            app.save()

                    # B. Re-point Order Items
                    OrderItem.objects.filter(product=spare).update(product=keeper)
                    
                    # C. Re-point Stock Batches
                    StockBatch.objects.filter(product=spare).update(product=keeper)
                    
                    # D. Merge Stock
                    if spare.stock > 0:
                        keeper.stock += spare.stock
                        keeper.save()
                    
                    # E. Delete
                    spare.delete()

        if duplicates_found == 0:
             self.stdout.write(self.style.SUCCESS("No duplicates found with case-insensitive check!"))
        else:
             self.stdout.write(self.style.SUCCESS(f"\n--- Resolved {duplicates_found} Duplicate Groups ---"))
