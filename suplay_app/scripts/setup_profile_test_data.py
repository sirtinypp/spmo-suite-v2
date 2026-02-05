import os
import django
import sys

# Add the project root to sys.path to ensure imports work correctly
sys.path.append("/app")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "office_supplies_project.settings")
django.setup()

from django.contrib.auth.models import User
from supplies.models import Order, Product, OrderItem
from django.utils import timezone
import random


def setup():
    print("Setting up test data...")

    # 1. Setup Data for History User
    user1, created = User.objects.get_or_create(username="history_user")
    user1.set_password("password123")
    user1.first_name = "History"
    user1.last_name = "User"
    user1.save()
    if created:
        print("Created history_user")
    else:
        print("Updated history_user")

    # Ensure products exist
    products = list(Product.objects.all())
    if not products:
        print("No products found! Creating dummy products...")
        from supplies.models import Category

        cat, _ = Category.objects.get_or_create(name="Office Supplies")
        for i in range(10):
            p = Product.objects.create(
                name=f"Test Product {i}",
                description="Test Description",
                price=100.00 + (i * 10),
                category=cat,
                stock=100,
            )
            products.append(p)

    # Create 7 orders for history_user to test limit 5 and pagination/limit logic
    current_orders = Order.objects.filter(user=user1).count()
    if current_orders < 7:
        for i in range(7 - current_orders):
            o = Order.objects.create(
                user=user1,
                employee_name="History User",
                department="IT Department",
                total_amount=0,
                status=random.choice(["pending", "approved", "delivered"]),
                created_at=timezone.now(),
            )
            # Add random items
            p = random.choice(products)
            qty = random.randint(1, 5)
            price = p.price
            OrderItem.objects.create(order=o, product=p, quantity=qty, price=price)
            o.total_amount = price * qty
            o.save()
        print(f"Created/Ensured 7 orders for history_user")

    # 2. Setup Data for New User (No History)
    user2, created = User.objects.get_or_create(username="new_user")
    user2.set_password("password123")
    user2.first_name = "New"
    user2.last_name = "User"
    user2.save()
    if created:
        print("Created new_user")
    else:
        print("Updated new_user")

    print("Test data setup complete.")


if __name__ == "__main__":
    setup()
