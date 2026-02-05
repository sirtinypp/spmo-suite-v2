from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from supplies.models import (
    Product,
    Department,
    AnnualProcurementPlan,
    UserProfile,
    Category,
    Order,
    OrderItem,
)
from supplies.views.client import update_cart, checkout_init
from django.test import RequestFactory, Client
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils import timezone


class Command(BaseCommand):
    help = "Verify Cart Security Logic"

    def handle(self, *args, **kwargs):
        from django.test.utils import setup_test_environment

        setup_test_environment()
        self.stdout.write("--- STARTING CART SECURITY TEST ---")

        # 1. Setup Data
        username = "test_sec_usr"
        dept_name = "Test Sec Dept"
        now = timezone.now()
        month_str = now.strftime("%b").lower()

        user, _ = User.objects.get_or_create(username=username)
        dept, _ = Department.objects.get_or_create(name=dept_name)

        if not hasattr(user, "profile"):
            UserProfile.objects.create(user=user, department=dept)
        else:
            user.profile.department = dept
            user.profile.save()

        cat, _ = Category.objects.get_or_create(name="Sec Cat")
        product, _ = Product.objects.get_or_create(
            name="Sec Item", defaults={"price": 100, "category": cat, "stock": 100}
        )

        # 2. Setup ALLOCATION (Limit 10)
        plan, _ = AnnualProcurementPlan.objects.get_or_create(
            department=dept, product=product, year=now.year, defaults={}
        )
        for m in [
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
        ]:
            setattr(plan, m, 0)
        setattr(plan, month_str, 10)
        plan.save()

        # 3. Test Vulnerability 1: UPDATE CART
        # Scenario: User adds 1 item (legal), then updates cart to 100 (illegal) via POST

        c = Client()
        c.force_login(user)

        # Init cart with 1 item
        session = c.session
        session["cart"] = {str(product.id): 1}
        session.save()

        self.stdout.write(f"\n[Test 1] Attempting to UPDATE cart to 100 (Limit 10)...")
        resp = c.post(f"/update-cart/{product.id}/", {"quantity": 100})

        # Check session
        session = c.session
        qty = session["cart"].get(str(product.id), 0)

        if qty == 100:
            self.stdout.write(
                self.style.ERROR(
                    f"❌ VULNERABILITY CONFIRMED: Cart updated to 100 despite limit 10."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"✅ SECURE: Cart quantity is {qty} (Expected < 10)")
            )

        # 4. Test Vulnerability 2: CHECKOUT (Draft Order Creation)
        # Scenario: Session has 100 items (forced). Does checkout_init block it?

        session["cart"] = {str(product.id): 100}  # Force blocked state
        session.save()

        self.stdout.write(f"\n[Test 2] Attempting to CHECKOUT with 100 items...")
        resp = c.post("/checkout/", {"department": dept_name, "name": "Tester"})

        # Check if Order was created
        latest_order = Order.objects.filter(user=user).last()
        if latest_order and latest_order.total_amount == 100 * 100:
            self.stdout.write(
                self.style.ERROR(
                    f"❌ VULNERABILITY CONFIRMED: Order #{latest_order.id} created for 100 items."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"✅ SECURE: Checkout blocked or order not created.")
            )

        # Cleanup
        Order.objects.filter(user=user).delete()
