import csv
import os
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'office_supplies_project.settings')
django.setup()

from supplies.models import Product, StockBatch, Supplier

def reconcile():
    incoming_file = 'suplay_app/media/suplay_incoming_template.csv'
    outgoing_file = 'suplay_app/media/suplay_outgoing_template.csv'
    
    # 1. Aggregate Incoming
    incoming_data = {} # item_code -> total_qty
    with open(incoming_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row['item_code'].strip()
            if not code: continue
            try:
                qty = int(row['quantity'])
                # Only include up to April 2026
                dt = datetime.strptime(row['date_received'], '%m/%d/%Y')
                if dt.year == 2026 and dt.month <= 4:
                    incoming_data[code] = incoming_data.get(code, 0) + qty
            except:
                continue

    # 2. Aggregate Outgoing
    outgoing_data = {} # item_code -> total_qty
    with open(outgoing_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row['item_code'].strip()
            if not code: continue
            try:
                qty = int(row['quantity'])
                # Only include up to April 2026
                dt = datetime.strptime(row['date_requested'], '%m/%d/%Y')
                if dt.year == 2026 and dt.month <= 4:
                    outgoing_data[code] = outgoing_data.get(code, 0) + qty
            except:
                continue

    # 3. Analyze against DB
    print(f"{'Item Code':<20} | {'Incoming':<10} | {'Outgoing':<10} | {'Net Log':<10} | {'DB Stock':<10} | {'Status'}")
    print("-" * 85)
    
    all_codes = set(incoming_data.keys()) | set(outgoing_data.keys())
    discrepancies = []

    for code in sorted(all_codes):
        inc = incoming_data.get(code, 0)
        out = outgoing_data.get(code, 0)
        net = inc - out
        
        product = Product.objects.filter(item_code=code).first()
        if product:
            db_stock = product.stock
            diff = db_stock - net
            status = "MATCH" if diff == 0 else f"DIFF: {diff}"
            if diff != 0:
                discrepancies.append((code, product.name, net, db_stock))
            print(f"{code:<20} | {inc:<10} | {out:<10} | {net:<10} | {db_stock:<10} | {status}")
        else:
            print(f"{code:<20} | {inc:<10} | {out:<10} | {net:<10} | {'MISSING':<10} | ERROR")

    return discrepancies

if __name__ == "__main__":
    reconcile()
