import os
import sys
import csv
import django

# 1. SETUP DJANGO ENVIRONMENT
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'office_supplies_project.settings')
django.setup()

from supplies.models import AnnualProcurementPlan, Department, Product
from django.db import transaction

CSV_PATH = 'media/GOLDEN_RECORD_APP_2026.csv'

def ingest_golden():
    print(f"Starting Final Institutional Ingestion: {CSV_PATH}")
    
    if not os.path.exists(CSV_PATH):
        print(f"Error: File not found at {CSV_PATH}")
        return

    success_count = 0
    error_count = 0

    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        with transaction.atomic():
            for row in reader:
                dept = Department.objects.filter(name__iexact=row['Office']).first()
                product = Product.objects.filter(item_code__iexact=row['Item Code']).first() or \
                          Product.objects.filter(name__iexact=row['Item Code']).first()
                
                if dept and product:
                    app, _ = AnnualProcurementPlan.objects.get_or_create(
                        department=dept, 
                        product=product, 
                        year=2026
                    )
                    # Mapping columns
                    app.jan = int(row['Jan'])
                    app.feb = int(row['Feb'])
                    app.mar = int(row['Mar'])
                    app.apr = int(row['Apr'])
                    app.may = int(row['May'])
                    app.jun = int(row['Jun'])
                    app.jul = int(row['Jul'])
                    app.aug = int(row['Aug'])
                    app.sep = int(row['Sep'])
                    app.oct = int(row['Oct'])
                    app.nov = int(row['Nov'])
                    app.dec = int(row['Dec'])
                    
                    app.save()
                    success_count += 1
                else:
                    error_count += 1

    print(f"SUCCESS: {success_count} APP records restored to Production.")
    if error_count > 0:
        print(f"WARNING: {error_count} records could not be matched and were skipped.")

if __name__ == '__main__':
    ingest_golden()
