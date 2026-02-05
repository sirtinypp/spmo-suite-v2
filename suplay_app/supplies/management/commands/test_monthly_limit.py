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
from supplies.views.client import add_to_cart, home
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils import timezone
import json


class Command(BaseCommand):
    help = "Test monthly allocation limit"

    def handle(self, *args, **kwargs):
        from django.test.utils import setup_test_environment

        setup_test_environment()
        self.stdout.write("--- STARTING MONTHLY LIMIT TEST ---")

        # 1. Setup Data
        username = "test_usr_month"
        dept_name = "Test Dept Month"
        now = timezone.now()
        month_str = now.strftime("%b").lower()  # e.g. 'jan'

        user, _ = User.objects.get_or_create(username=username)
        dept, _ = Department.objects.get_or_create(name=dept_name)

        if not hasattr(user, "profile"):
            UserProfile.objects.create(user=user, department=dept)
        else:
            user.profile.department = dept
            user.profile.save()

        category, _ = Category.objects.get_or_create(name="Test Category Month")
        product, _ = Product.objects.get_or_create(
            name="Test Month Item",
            defaults={"price": 100, "category": category, "stock": 100},
        )
        # Force stock update if it existed
        product.stock = 100
        product.save()

        # CLEANUP OLD ORDERS
        Order.objects.filter(user=user).delete()

        # 2. Setup ALLOCATION
        # Set limit for THIS month to 10
        plan, created = AnnualProcurementPlan.objects.get_or_create(
            department=dept, product=product, year=now.year, defaults={}
        )
        # Reset all months to 0,set current to 10
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

        self.stdout.write(f"Allocation for {month_str.upper()}: 10")

        # 3. Simulate Previous Consumption (Create an Order)
        # Order 5 items
        order = Order.objects.create(
            user=user,
            department=dept,
            total_amount=500,
            status="pending",  # Pending counts towards consumption in our logic? No, let's check.
            # Logic implementation: exclude(status='cancelled'). So pending IS counted.
        )
        OrderItem.objects.create(order=order, product=product, quantity=5, price=100)

        # Manually set created_at to now (auto_now_add handles it, but just ensuring)
        order.created_at = now
        order.save()

        self.stdout.write(f"Created pending order for 5 items.")
        self.stdout.write("Remaining Allowance should be: 10 - 5 = 5")

        # 4. Test Over-limit Addition
        self.stdout.write("\nAttempting to Add 6 items (Should FAIL)...")

        factory = RequestFactory()
        request = factory.post(f"/add-to-cart/{product.id}/", {"quantity": 6})
        request.user = user
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"

        response = add_to_cart(request, product.id)

        if response.status_code == 400:
            content = json.loads(response.content.decode("utf-8"))
            self.stdout.write(
                self.style.SUCCESS(f"SUCCESS: Blocked. Message: {content['message']}")
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"FAILURE: Status {response.status_code}, Content: {response.content.decode()}"
                )
            )

        # 5. Test Valid Addition
        self.stdout.write("\nAttempting to Add 5 items (Should SUCCEED)...")
        request = factory.post(f"/add-to-cart/{product.id}/", {"quantity": 5})
        request.user = user
        middleware = SessionMiddleware(lambda x: None)  # New session/request
        middleware.process_request(request)
        request.session.save()
        request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"

        response = add_to_cart(request, product.id)

        if response.status_code == 200:
            content = json.loads(response.content.decode("utf-8"))
            self.stdout.write(
                self.style.SUCCESS(
                    f"SUCCESS: Added. Cart Count: {content['cart_count']}"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"FAILURE: Status {response.status_code}, Content: {response.content.decode()}"
                )
            )

        # 6. Test Catalog Visibility (Home View)
        self.stdout.write("\nChecking Catalog Display (Home View)...")
        request = factory.get("/")
        request.user = user
        middleware.process_request(request)
        request.session.save()

        response = home(request)

        # We need to extract context from response.
        # Since it's a direct view call (not client.get), response is HttpResponse with content,
        # context isn't directly attached unless we inspect logic or use test client.
        # However, we can't easily access context from HttpResponse object returned by render()
        # without using the Django Test Client.
        # BUT, since we are inside a management command, we can just check the logic calculation by
        # creating specific conditions.

        # Actually, let's verify if the 'personal_stock' logic is working by inspecting the product
        # modifying logic in the view? No, we can't inspect inside the view function.

        # Alternative: Re-implement the view logic here? No, that proves nothing.
        # We really should use the test client to get context.
        from django.test import Client

        c = Client()
        c.force_login(user)
        response = c.get("/", HTTP_HOST="localhost")

        if response.status_code == 200:
            products = response.context["products"]
            found = False
            for p in products:
                if p.id == product.id:
                    found = True
                    # Consumed=5 (Order) + 5 (Cart from Step 5) = 10.
                    # Limit = 10.
                    # Remaining = 0.
                    self.stdout.write(
                        f"Product Found: {p.name}. Personal Stock: {getattr(p, 'personal_stock', 'MISSING')}"
                    )
                    # Cart is empty in this new Client session, so remaining is 10 - 5 = 5.
                    if getattr(p, "personal_stock", -1) == 5:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"SUCCESS: Personal Stock is 5 (Correct: 10 Alloc - 5 Consumed - 0 Cart)"
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f"FAILURE: Personal Stock is {getattr(p, 'personal_stock', 'MISSING')}, expected 5"
                            )
                        )
                    break
            if not found:
                self.stdout.write(
                    self.style.ERROR(
                        "FAILURE: Test Product not found in home view context."
                    )
                )
        else:
            self.stdout.write(
                self.style.ERROR(f"FAILURE: Home view returned {response.status_code}")
            )

        # Cleanup (Optional)
        # order.delete()
        # plan.delete()
