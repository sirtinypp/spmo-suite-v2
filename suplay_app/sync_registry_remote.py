import os
import sys
import json
import django

# 1. SETUP DJANGO ENVIRONMENT
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'office_supplies_project.settings')
django.setup()

from supplies.models import Department, Product, Category

JSON_PATH = 'REGISTRY_SYNC_2026_05_14.json'

def sync_registry():
    print(f"Starting Registry Sync from {JSON_PATH}")
    
    if not os.path.exists(JSON_PATH):
        print("Error: JSON file not found.")
        return

    with open(JSON_PATH, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    # Pre-fetch/Create Uncategorized
    default_cat, _ = Category.objects.get_or_create(name="Uncategorized")
    
    dept_count = 0
    prod_count = 0

    for item in data:
        model = item['model']
        fields = item['fields']
        
        if model == 'supplies.department':
            dept, created = Department.objects.get_or_create(
                name=fields['name'],
                defaults={'description': fields.get('description', '')}
            )
            if created: dept_count += 1
            
        elif model == 'supplies.product':
            # Match by Item Code first
            product = Product.objects.filter(item_code=fields['item_code']).first() or \
                      Product.objects.filter(name=fields['name']).first()
            
            if not product:
                # Create if missing
                Product.objects.create(
                    item_code=fields['item_code'],
                    name=fields['name'],
                    description=fields.get('description', ''),
                    price=fields.get('price', 0),
                    category=default_cat,
                    stock=fields.get('stock', 0)
                )
                prod_count += 1
            else:
                # Update name/code to match local "Source of Truth"
                product.name = fields['name']
                product.item_code = fields['item_code']
                product.save()

    print(f"SUCCESS: Synced {dept_count} new Departments and {prod_count} new Products.")

if __name__ == '__main__':
    sync_registry()
