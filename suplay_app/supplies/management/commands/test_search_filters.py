from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from supplies.models import (
    Product,
    Department,
    AnnualProcurementPlan,
    UserProfile,
    Category,
    Supplier,
)
from supplies.views.client import home, search
from django.test import RequestFactory, Client
from django.utils import timezone


class Command(BaseCommand):
    help = "Verify Search and Filter Logic"

    def handle(self, *args, **kwargs):
        from django.test.utils import setup_test_environment

        setup_test_environment()
        self.stdout.write("--- STARTING SEARCH & FILTER TEST ---")

        # 1. Setup Data
        user, _ = User.objects.get_or_create(username="test_search_usr")
        dept, _ = Department.objects.get_or_create(name="Test Search Dept")

        if not hasattr(user, "profile"):
            UserProfile.objects.create(user=user, department=dept)
        else:
            user.profile.department = dept
            user.profile.save()

        cat_a, _ = Category.objects.get_or_create(name="Category A")
        cat_b, _ = Category.objects.get_or_create(name="Category B")

        sup_x, _ = Supplier.objects.get_or_create(name="Supplier X")

        # Product 1: Allocated, Cat A, Supplier X, In Stock
        p1, _ = Product.objects.get_or_create(
            name="Allocated Pen",
            defaults={
                "price": 10,
                "category": cat_a,
                "supplier": sup_x,
                "stock": 50,
                "item_code": "CODE123",
            },
        )
        p1.category = cat_a  # Ensure correct cat if existed
        p1.stock = 50
        p1.save()

        # Product 2: Allocated, Cat B, Out of Stock
        p2, _ = Product.objects.get_or_create(
            name="Allocated Paper",
            defaults={"price": 20, "category": cat_b, "stock": 0},
        )
        p2.category = cat_b
        p2.stock = 0
        p2.save()

        # Product 3: Unallocated (Should never show)
        p3, _ = Product.objects.get_or_create(
            name="Hidden Marker", defaults={"price": 5, "category": cat_a, "stock": 100}
        )

        # Setup Allocations (Only for P1 and P2)
        now = timezone.now()
        defaults = {
            m: 10
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
            ]
        }

        AnnualProcurementPlan.objects.get_or_create(
            department=dept, product=p1, year=now.year, defaults=defaults
        )
        AnnualProcurementPlan.objects.get_or_create(
            department=dept, product=p2, year=now.year, defaults=defaults
        )

        # Ensure NO allocation for P3
        AnnualProcurementPlan.objects.filter(department=dept, product=p3).delete()

        # 2. Test HOME Filtering (Default: In Stock Only? No, normally shows all if not filtered, seeing client.py logic...)
        # Logic check:
        # if search_query: ...
        # else: if stock_status == 'out_of_stock': ... else: products.filter(stock__gt=0)
        # So DEFAULT is Stock > 0.

        c = Client()
        c.force_login(user)

        self.stdout.write("\nTest 1: Default Home View (Expects Allocated + In Stock)")
        resp = c.get("/", HTTP_HOST="localhost")
        prods = list(resp.context["products"])
        if p1 in prods and p2 not in prods and p3 not in prods:
            self.stdout.write(
                self.style.SUCCESS(
                    "✅ Pass: Shows P1 (Alloc+Stock), Hides P2 (No Stock), Hides P3 (Unalloc)"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"❌ Fail: Got {[p.name for p in prods]}")
            )

        self.stdout.write("\nTest 2: Filter 'Out of Stock' (Expects P2)")
        resp = c.get("/?status=out_of_stock", HTTP_HOST="localhost")
        prods = list(resp.context["products"])
        if p2 in prods and p1 not in prods:
            self.stdout.write(self.style.SUCCESS("✅ Pass: Shows P2, Hides P1"))
        else:
            self.stdout.write(
                self.style.ERROR(f"❌ Fail: Got {[p.name for p in prods]}")
            )

        self.stdout.write("\nTest 3: Filter Category A (Expects P1)")
        resp = c.get(f"/?category={cat_a.id}", HTTP_HOST="localhost")
        prods = list(resp.context["products"])
        if p1 in prods and p2 not in prods:
            self.stdout.write(
                self.style.SUCCESS("✅ Pass: Shows P1 (Cat A), Hides P2 (Cat B)")
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"❌ Fail: Got {[p.name for p in prods]}")
            )

        # 3. Test SEARCH View
        self.stdout.write(
            "\nTest 4: Search 'Allocated' (Expects P1 and P2? Search usually shows OOS too?)"
        )
        # Checking client.py search logic...
        # products = products.filter(Q(name__icontains...))
        # Then APP filtered.
        # It does NOT seem to filter by stock > 0 in search view based on previous read.
        resp = c.get("/search/?q=Allocated", HTTP_HOST="localhost")
        prods = list(resp.context["products"])

        # P1 matches "Allocated", P2 matches "Allocated"
        # P3 does NOT match.
        if p1 in prods and p2 in prods:
            self.stdout.write(
                self.style.SUCCESS(
                    "✅ Pass: Search finds both Allocated items (In/Out Stock)"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"❌ Fail: Got {[p.name for p in prods]}")
            )

        self.stdout.write("\nTest 5: Search 'Hidden' (Expects Empty - Restricted)")
        resp = c.get("/search/?q=Hidden", HTTP_HOST="localhost")
        prods = list(resp.context["products"])
        if not prods:
            self.stdout.write(
                self.style.SUCCESS("✅ Pass: Search blocked Unallocated item")
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"❌ Fail: Found restricted item {[p.name for p in prods]}"
                )
            )

        self.stdout.write("\nTest 6: Search by Code 'CODE123' (Expects P1)")
        resp = c.get("/search/?q=CODE123", HTTP_HOST="localhost")
        prods = list(resp.context["products"])
        if p1 in prods and len(prods) == 1:
            self.stdout.write(self.style.SUCCESS("✅ Pass: Search by Item Code works"))
        else:
            self.stdout.write(
                self.style.ERROR(f"❌ Fail: Got {[p.name for p in prods]}")
            )

        # Cleanup
        # user.delete()
        # dept.delete()
