import os
import sys
import django
from django.conf import settings
from django.utils import timezone

sys.path.append("/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "office_supplies_project.settings")
django.setup()

from django.contrib.auth.models import User
from supplies.models import (
    UserProfile,
    Department,
    AnnualProcurementPlan,
    Product,
    StockBatch,
)

TARGET_USER = "sao_user2"

print(f"=== INSPECTION REPORT FOR: {TARGET_USER} ===")
try:
    user = User.objects.get(username=TARGET_USER)
    print(f"User Found: {user.username} (ID: {user.id})")

    if hasattr(user, "profile") and user.profile.department:
        dept = user.profile.department
        print(f"Department: {dept.name} (ID: {dept.id})")

        # 1. ANALYZE ALLOCATIONS
        print("\n--- APP Allocations Analysis ---")
        # Group by Year
        from django.db.models import Count

        years = (
            AnnualProcurementPlan.objects.filter(department=dept)
            .values("year")
            .annotate(count=Count("id"))
        )
        if years:
            for y in years:
                print(f"Year {y['year']}: {y['count']} entries")
        else:
            print("!! NO ALLOCATIONS FOUND FOR THIS DEPARTMENT !!")

        # 2. CHECK CURRENT YEAR LOGIC
        sys_year = timezone.now().year
        print(f"\nSystem Time: {timezone.now()}")
        print(f"System Year Checked by Code: {sys_year}")

        relevant_allocs = AnnualProcurementPlan.objects.filter(
            department=dept, year=sys_year
        )
        count_relevant = relevant_allocs.count()
        print(f"Allocations Matching System Year ({sys_year}): {count_relevant}")

        if count_relevant == 0 and years:
            # Find the year they DO have
            likely_year = list(years)[0]["year"]
            print(f"\n[DIAGNOSIS] MISMATCH DETECTED!")
            print(
                f"User has data for Year {likely_year}, but Code looks for {sys_year}."
            )

        # 3. SAMPLE PRODUCT CHECK
        if count_relevant > 0:
            print("\n--- Sample Allocation (First 1) ---")
            sample = relevant_allocs.first()
            prod = sample.product
            print(f"Allocated Product: {prod.name} (ID: {prod.id})")
            print(f"  > Global Stock: {prod.stock}")
            print(f"  > APP Approved: {sample.quantity_approved}")
            print(f"  > APP Remaining: {sample.remaining_balance()}")

            # Check StockBatch for this Product
            from supplies.models import StockBatch

            batches = StockBatch.objects.filter(product=prod)
            print(f"  > Linked Batches: {batches.count()}")

        # 4. SIMULATE VIEW LOGIC
        print("\n--- VIEW LOGIC SIMULATION ---")
        qs = Product.objects.select_related("category", "supplier").all()
        print(f"Initial Product Count: {qs.count()}")

        alloc_ids = AnnualProcurementPlan.objects.filter(
            department=dept, year=sys_year
        ).values_list("product_id", flat=True)
        print(f"Alloc IDs Count: {len(alloc_ids)} (Sample: {list(alloc_ids)[:5]})")

        qs_filtered = qs.filter(id__in=alloc_ids)
        print(f"Filtered Product Count: {qs_filtered.count()}")

        if qs_filtered.count() == 0:
            print("[CRITICAL FAILURE] Filter returned 0! Why?")
            print(f"Checking ID 20 in Initial QS: {qs.filter(id=20).exists()}")
            if len(alloc_ids) > 0 and qs.filter(id=20).exists():
                print(f"Is 20 in alloc_ids? {20 in alloc_ids}")
        else:
            print("[SUCCESS] View Logic Query returns items!")

    else:
        print("!! User has NO Profile or NO Department !!")

except User.DoesNotExist:
    print(f"User {TARGET_USER} NOT FOUND.")

print("=== END REPORT ===")
