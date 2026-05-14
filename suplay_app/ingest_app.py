import os
import sys
import csv
import django

# 1. SETUP DJANGO ENVIRONMENT
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'office_supplies_project.settings')
django.setup()

from supplies.models import AnnualProcurementPlan, Department, Product, Category
from django.db import transaction

CSV_PATH = r'c:\Users\Aaron\spmo-suite - Copy\suplay_app\media\APP-CSE 2026 Total.csv'

def ingest_app():
    print(f"Starting Direct Injection: {CSV_PATH}")
    
    if not os.path.exists(CSV_PATH):
        print(f"Error: File not found at {CSV_PATH}")
        return

    aggregated = {}
    
    # 2. IN-MEMORY AGGREGATION
    print("Reading 15,125 rows and aggregating by Department/Item...")
    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            dept_name = (row.get('Office') or row.get('Department', '')).strip()
            item_name = (row.get('Item Name') or '').strip()
            month_raw = (row.get('Month') or '').strip().lower()[:3]
            
            try:
                qty = int(float(str(row.get('QTY', 0) or 0).replace(',', '')))
            except:
                qty = 0
            
            if not dept_name or not item_name: continue
            
            key = (dept_name, item_name)
            if key not in aggregated:
                aggregated[key] = {
                    'jan':0, 'feb':0, 'mar':0, 'apr':0, 'may':0, 'jun':0,
                    'jul':0, 'aug':0, 'sep':0, 'oct':0, 'nov':0, 'dec':0
                }
            
            if month_raw in aggregated[key]:
                aggregated[key][month_raw] += qty
            
            if i % 2000 == 0 and i > 0:
                print(f"   Processed {i} rows...")

    print(f"Aggregation complete. Found {len(aggregated)} unique Department/Item combinations.")

    # 3. DATABASE INJECTION
    print("Committing to Database (Atomic Transaction)...")
    
    DEPARTMENT_MAPPING = {
        "Accounting Office": "System Accounting Office (SAO)",
        "Cash Office": "System Cash Office (SCO)",
        "Supply and Property Management Office (SPMO)": "System Supply and Property Management Office (SSPMO)",
        "Human Resource Development Office (HRDO)": "System Human Resource Development Office (SHRDO)",
        "Information Technology Development Center (ITDC)": "UP Information Technology Development Center (UP ITDC)",
        "CIFAL": "UP CIFAL Philippines",
        "COA-SYSTEM": "Commission on Audit (COA-System)",
        "Center for Integrative Development Studies (CIDS)": "UP Center for Integrative and Development Studies (UP CIDS)",
        "Center for Women and Gender Studies (CWGS)": "UP Center for Women’ and Gender Studies (UP CWGS)",
        "Digital transformation": "Office of the Vice President for Digital Transformation (OVPDX)",
        "Executive House": "Office of the President (OP)",
        "Media and Public Relation (MPRO)": "UP Media and Public Relations Office (UP MPRO)",
        "Office of Admissions": "Office of Admissions (OADMS)",
        "Office of Alumni Relation (OAR)": "Office of Alumni Relations (OAR)",
        "Office of Design and Planning Initiatives (ODPI)": "Office of Design and Planning Initiative (ODPI)",
        "Office of the Vice President for Planning and Finance (OVPPF)": "Office of the Vice President for Planning & Finance (OVPPF)",
        "TVUP": "Television network operated by the University of the Philippines (TVUP)",
        "UP Resilience Institute (UPRI)": "Up Resilience Institute (UPRI)",
        "UP Bonifacio Global City (UPBGC)": "UP Bonifacio Global City Campus (UP-BGC)",
        "UP Intelligent System Center": "UP Intelligent Systems Center (ISC)",
        "UP Korea Research Center (UPKRC)": "UP Korea Research Center (UP KRC)",
        "UP Procurement Unit": "System Procurement Office (SPO)",
        "Ugnayan ng Pahinungod": "UP Ugnayan ng Pahinungod Office"
    }

    success_count = 0
    created_prods = 0
    missing_depts = set()

    # Pre-fetch categories for auto-creation
    default_category, _ = Category.objects.get_or_create(name="Uncategorized")

    with transaction.atomic():
        for (d_name, i_name), months in aggregated.items():
            # Apply Mapping first
            lookup_name = DEPARTMENT_MAPPING.get(d_name, d_name)
            
            # Case-Insensitive Department Match
            dept = Department.objects.filter(name__iexact=lookup_name).first()
            
            if not dept:
                missing_depts.add(d_name)
                continue

            # Case-Insensitive Product Match
            product = Product.objects.filter(name__iexact=i_name).first() or \
                      Product.objects.filter(item_code__iexact=i_name).first()
            
            if not product:
                # Auto-Create if missing to ensure data has a home
                product = Product.objects.create(
                    item_code=f"AUTO-{hash(i_name) % 100000}",
                    name=i_name[:195],
                    description="Auto-created during APP Ingestion.",
                    price=1.00,
                    category=default_category,
                    stock=0
                )
                created_prods += 1
            
            app, _ = AnnualProcurementPlan.objects.get_or_create(
                department=dept, 
                product=product, 
                year=2026
            )
            for m_field, val in months.items():
                setattr(app, m_field, val)
            
            app.save()
            success_count += 1

    print(f"\nSUCCESS: {success_count} APP records restored/updated.")
    print(f"INFO: {created_prods} new products auto-created.")
    
    if missing_depts:
        print(f"WARNING: {len(missing_depts)} Departments were not found and were skipped.")
        print(f"Sample missing: {list(missing_depts)[:3]}")

if __name__ == '__main__':
    ingest_app()
