import os
import sys
import csv
import django

# 1. SETUP DJANGO ENVIRONMENT
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'office_supplies_project.settings')
django.setup()

from supplies.models import AnnualProcurementPlan

def export_golden():
    print("Exporting Processed Institutional Data (2026)...")
    
    plans = AnnualProcurementPlan.objects.filter(year=2026).select_related('department', 'product')
    
    OUTPUT_PATH = r'c:\Users\Aaron\spmo-suite - Copy\suplay_app\media\GOLDEN_RECORD_APP_2026.csv'
    
    with open(OUTPUT_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Standard Matrix Headers
        writer.writerow(['Office', 'Item Code', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Annual Cap'])
        
        for p in plans:
            writer.writerow([
                p.department.name,
                p.product.item_code,
                p.jan, p.feb, p.mar, p.apr, p.may, p.jun,
                p.jul, p.aug, p.sep, p.oct, p.nov, p.dec,
                p.quantity_approved
            ])
            
    print(f"SUCCESS: Golden Record created at {OUTPUT_PATH}")
    print(f"Total Rows: {plans.count()}")

if __name__ == '__main__':
    export_golden()
