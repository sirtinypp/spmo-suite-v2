import sys

sys.path.append("/app")
import os
import django
from django.db.models import Count

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "office_supplies_project.settings")
django.setup()

from supplies.models import Product


def check():
    print("--- Checking Status ---")

    # Check specific problem item
    target = "44122037-RB-P10"
    count = Product.objects.filter(item_code__icontains=target).count()
    print(f"Count for '{target}' (icontains): {count}")
    matches = list(
        Product.objects.filter(item_code__icontains=target).values_list(
            "item_code", flat=True
        )
    )
    print(f"  Matches Found: {matches}")

    exact = Product.objects.filter(item_code__iexact=target).count()
    print(f"Count for '{target}' (iexact): {exact}")

    # Check for ANY duplicates
    dupes = (
        Product.objects.values("item_code")
        .annotate(count=Count("id"))
        .filter(count__gt=1)
    )
    print(f"Total Duplicate Groups Remaining: {len(dupes)}")


if __name__ == "__main__":
    check()
