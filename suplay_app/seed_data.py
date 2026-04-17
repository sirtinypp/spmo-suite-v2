import os
import django
import random
from decimal import Decimal
from django.utils import timezone

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'office_supplies_project.settings')
django.setup()

from supplies.models import Category, Supplier, Product, Order, OrderItem, Department, APRRequest, News, UserProfile
from django.contrib.auth.models import User

def seed_data():
    print("[START] Initiating Institutional Data Seeding Protocol...")

    # 1. Categories
    categories = [
        ("Office Supplies", "General stationery, papers, and desk essentials."),
        ("IT Equipment & Consumables", "Computer peripherals, ink toners, and hardware snacks."),
        ("Medical & First Aid", "Essential health supplies for campus safety."),
        ("Janitorial & Cleaning", "Sanitation and facility maintenance chemicals."),
        ("Furniture & Fixtures", "Institutional comfort and ergonomic assets."),
        ("Electrical & Hardware", "Maintenance and electrical engineering supplies.")
    ]
    
    cat_objs = []
    for name, desc in categories:
        cat, _ = Category.objects.get_or_create(name=name, defaults={'description': desc})
        cat_objs.append(cat)
    print(f"[OK] Categories Synchronized: {len(cat_objs)}")

    # 2. Suppliers
    suppliers = [
        ("PS-DBM Main", True),
        ("Advance Solutions Inc.", False),
        ("Silicon Valley Systems", False),
        ("Paper One Philippines", False),
        ("Sanitary Care Products", False)
    ]
    
    sup_objs = []
    for name, is_ps in suppliers:
        sup, _ = Supplier.objects.get_or_create(name=name, defaults={'is_ps_dbm': is_ps})
        sup_objs.append(sup)
    print(f"[OK] Suppliers Registered: {len(sup_objs)}")

    # 3. Products
    products_data = [
        ("Paper, Multicopy A4 80gsm", "Paper One", "PAP-A4-80", 250.00, "ream", 50, cat_objs[0]),
        ("Stapler, Manual Heavy Duty", "MAX", "STA-HD", 850.00, "pc", 10, cat_objs[0]),
        ("Toner Cartridge, HP CE285A", "HP", "INK-85A", 3200.00, "cart", 5, cat_objs[1]),
        ("Wireless Mouse, Multi-Device", "Logitech", "IT-MSE-01", 1250.00, "pc", 15, cat_objs[1]),
        ("Surgical Mask, 3-ply 50s", "Indoplas", "MED-MSK", 150.00, "box", 100, cat_objs[2]),
        ("Liquid Hand Soap, 1L", "Sanicare", "JAN-LHS-1", 185.00, "bottle", 30, cat_objs[3]),
        ("Alcohol, Isopropyl 70% 1Gal", "Casino", "MED-ALC-1G", 550.00, "gallon", 40, cat_objs[2]),
        ("LED Bulb, 9W Daylight", "Philips", "ELE-LED-9W", 180.00, "pc", 50, cat_objs[5]),
    ]
    
    prod_objs = []
    for name, brand, code, price, unit, reorder, cat in products_data:
        prod, _ = Product.objects.get_or_create(
            name=name,
            defaults={
                'brand': brand,
                'item_code': code,
                'price': Decimal(price),
                'unit': unit,
                'reorder_point': reorder,
                'category': cat,
                'stock': random.randint(20, 500),
                'description': f"Institutional grade {name} categorized under {cat.name}."
            }
        )
        prod_objs.append(prod)
    print(f"[OK] Master Inventory Populated: {len(prod_objs)} assets")

    # 4. Departments
    depts = ["CAS", "COE", "CBA", "CHK", "CS", "CFA", "SPMO-ADMIN"]
    dept_objs = []
    for d in depts:
        dept, _ = Department.objects.get_or_create(name=d)
        dept_objs.append(dept)
    print(f"[OK] Departments Established: {len(dept_objs)}")

    # 5. Orders (Dashboard telemetry)
    admin_user = User.objects.filter(is_superuser=True).first()
    if admin_user and prod_objs:
        for i in range(5):
            status = random.choice(['pending', 'approved', 'delivered'])
            order = Order.objects.create(
                user=admin_user,
                employee_name=f"Employee {random.randint(100,999)}",
                department=random.choice(dept_objs),
                total_amount=0,
                status=status,
                admin_validated=(status != 'pending'),
                chief_approved=(status == 'delivered')
            )
            
            total = Decimal(0)
            for _ in range(random.randint(1, 4)):
                p = random.choice(prod_objs)
                qty = random.randint(1, 10)
                subtotal = p.price * qty
                OrderItem.objects.create(order=order, product=p, quantity=qty, price=p.price)
                total += subtotal
            
            order.total_amount = total
            order.save()
        print("[OK] Dashboard Telemetry (Orders) Generated")

    # 6. News
    if admin_user:
        News.objects.get_or_create(
            title="Q2 Inventory Audit Scheduled",
            defaults={
                'content': "All department heads are required to submit their physical asset counts by April 30. Please ensure all DRs are filed.",
                'urgency': 'URGENT',
                'author': admin_user
            }
        )
        print("[OK] Institutional News Synchronized")

    print("\n[FINISH] Seeding Protocol Complete. SPMO Suite is now Data-Rich.")

if __name__ == "__main__":
    seed_data()
