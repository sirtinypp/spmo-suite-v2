import os
import django
import sys

# Setup Django environment
sys.path.append("/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "office_supplies_project.settings")
django.setup()

from django.contrib.auth.models import User
from supplies.models import UserProfile, Product, AnnualProcurementPlan


def setup_demo():
    print("Setting up Demo User and APP Data...")

    # 1. Create User: spmo_user
    username = "spmo_user"
    department = "Supply and Property Management Office (SPMO)"

    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password("password123")
        user.first_name = "SPMO"
        user.last_name = "User"
        user.save()
        print(f"User '{username}' created with password 'password123'.")
    else:
        print(f"User '{username}' already exists.")

    # 2. Assign Department (UserProfile)
    profile, created = UserProfile.objects.get_or_create(user=user)
    profile.department = department
    profile.save()
    print(f"Assigned department: {department}")

    # 3. Create Allocations for this Dept
    print("Creating Allocations...")

    # allocations map: product_name -> [q1, q2, q3, q4] (simplified)
    # We will spread these across months
    allocations = {
        "BALLPEN, BLUE, retractable": 50,
        "Test Product 1": 20,
        "Test Product 2": 100,
        "Test Product 3": 10,
    }

    # Ensure products exist and create APP entries
    for prod_name, quantity in allocations.items():
        # Find product (fuzzy)
        product = Product.objects.filter(name__icontains=prod_name).first()
        if not product:
            print(f"  [Skip] Product '{prod_name}' not found.")
            continue

        # Create/Update APP Entry
        # Distribute quantity across 12 months roughly
        per_month = quantity // 12
        remainder = quantity % 12

        app, created = AnnualProcurementPlan.objects.get_or_create(
            department=department, product=product, year=2025
        )

        # Set monthly values (simplified distribution)
        app.jan = per_month + (1 if remainder > 0 else 0)
        app.feb = per_month
        app.mar = per_month
        app.apr = per_month
        app.may = per_month
        app.jun = per_month
        app.jul = per_month
        app.aug = per_month
        app.sep = per_month
        app.oct = per_month
        app.nov = per_month
        app.dec = per_month

        app.save()
        print(f"  [OK] Allocated {quantity} of '{product.name}' to {department}")

    print("Setup Complete!")


if __name__ == "__main__":
    setup_demo()
