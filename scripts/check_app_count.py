import sys

sys.path.append("/app")
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "office_supplies_project.settings")
django.setup()

from supplies.models import AnnualProcurementPlan, Department, Product


def check():
    print("--- APP Allocation Statistics ---")

    total_apps = AnnualProcurementPlan.objects.count()
    total_depts = AnnualProcurementPlan.objects.values("department").distinct().count()
    total_products = AnnualProcurementPlan.objects.values("product").distinct().count()

    print(f"Total Allocations (Rows): {total_apps}")
    print(f"Unique Departments: {total_depts}")
    print(f"Unique Allocated Products: {total_products}")

    if total_apps > 0:
        print("\nSuccess: Data is present.")
    else:
        print("\nWarning: No allocations found.")


if __name__ == "__main__":
    check()
