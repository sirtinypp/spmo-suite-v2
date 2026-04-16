import csv
import os
import django
from datetime import datetime

# Setup Django
import sys
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from inventory.models import Asset, Department

def import_final_data(csv_path):
    print("Clearing existing Assets and Departments...")
    Asset.objects.all().delete()
    Department.objects.all().delete()
    print("Database cleared.")

    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    with open(csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        count = 0
        
        # Pre-cache brands for detection if missing
        BRANDS = [
            'APPLE', 'ACER', 'ASUS', 'BROTHER', 'CANON', 'CARRIER', 'CISCO', 'DELL', 
            'EPSON', 'FUJITSU', 'HP', 'LENOVO', 'LOGITECH', 'MICROSOFT', 'MITSUBISHI', 
            'PANASONIC', 'SAMSUNG', 'SONY', 'TOSHIBA', 'XEROX', 'VIEWSONIC', 'POLY', 'JABRA',
            'LG', 'ARUBA', 'EDGECORE', 'MSI', 'XITRIX', 'NIKON', 'BLEREX', 'IMPULSE', 'DJI', 'UNIFI', 'TRENDSONIC'
        ]

        for row in reader:
            # 1. Get or Create Department
            dept_name = row.get('assigned_office', 'UNASSIGNED').strip()
            if not dept_name:
                dept_name = 'UNASSIGNED'
            dept, _ = Department.objects.get_or_create(name=dept_name)

            # 2. Parse Date
            date_acquired = None
            date_str = row.get('date_acquired', '').strip()
            if date_str:
                for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%d/%m/%Y'):
                    try:
                        date_acquired = datetime.strptime(date_str, fmt).date()
                        break
                    except ValueError:
                        continue

            # 3. Handle Brand fallback
            brand = row.get('brand', '').strip()
            if not brand:
                name_upper = row.get('name', '').upper()
                for b in BRANDS:
                    if b in name_upper:
                        brand = b.title()
                        break

            # 4. Create Asset
            try:
                asset = Asset.objects.create(
                    item_id=row.get('item_id', ''),
                    property_number=row.get('property_number', ''),
                    name=row.get('name', ''),
                    brand=brand,
                    description=row.get('description', ''),
                    date_acquired=date_acquired,
                    acquisition_cost=float(row.get('acquisition_cost', 0) or 0),
                    unit_of_measure=row.get('unit_of_measure', 'unit'),
                    quantity_physical_count=int(row.get('quantity_physical_count', 1) or 1),
                    asset_class=row.get('ppe_category', 'OTHER').upper(),
                    asset_nature=row.get('asset_type', 'PPE').upper(),
                    status=row.get('status', 'SERVICEABLE').upper(),
                    department=dept,
                    assigned_custodian=row.get('assigned_custodian', ''),
                    accountable_firstname=row.get('accountable_firstname', ''),
                    accountable_surname=row.get('accountable_surname', ''),
                )
                count += 1
                if count % 100 == 0:
                    print(f"Imported {count} assets...")
            except Exception as e:
                print(f"Error importing row {row.get('id', 'unknown')}: {e}")

    print(f"SUCCESS: Imported {count} assets into {Department.objects.count()} departments.")

if __name__ == "__main__":
    import_final_data('/app/rpcppe_final.csv')
