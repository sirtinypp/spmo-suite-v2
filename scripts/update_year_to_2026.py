import sys

sys.path.append("/app")
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "office_supplies_project.settings")
django.setup()

from supplies.models import AnnualProcurementPlan


def update_year():
    print("--- Updating APP Data Year to 2026 ---")

    # Check current distribution
    from django.db.models import Count

    dist = AnnualProcurementPlan.objects.values("year").annotate(count=Count("id"))
    print(f"Current Year Distribution: {list(dist)}")

    # Update ALL to 2026
    count = AnnualProcurementPlan.objects.all().update(year=2026)

    print(f"Updated {count} records to Year 2026.")

    # Verify
    dist_new = AnnualProcurementPlan.objects.values("year").annotate(count=Count("id"))
    print(f"New Year Distribution: {list(dist_new)}")


if __name__ == "__main__":
    update_year()
