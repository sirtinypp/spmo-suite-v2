import sys
sys.path.append('/app')
import os
import django
from django.db.models import Count, Q

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'office_supplies_project.settings')
django.setup()

from supplies.models import Category, Product

def analyze():
    print("--- Analyzing Categories for Duplicates (Case-Insensitive) ---")
    
    # 1. Group by normalized name
    normalized_map = {}
    all_cats = Category.objects.all()
    
    for cat in all_cats:
        norm_name = cat.name.strip().lower()
        if norm_name not in normalized_map:
            normalized_map[norm_name] = []
        normalized_map[norm_name].append(cat)
        
    # 2. Identify Duplicates
    duplicates_found = 0
    for norm_name, cats in normalized_map.items():
        if len(cats) > 1:
            duplicates_found += 1
            print(f"\nDuplicate Group: '{norm_name}'")
            for cat in cats:
                # Count related products to see which one is "active"
                prod_count = Product.objects.filter(category=cat).count()
                print(f"  - ID: {cat.id} | Name: '{cat.name}' | Related Products: {prod_count}")

    if duplicates_found == 0:
        print("\nNo duplicate categories found.")
    else:
        print(f"\nFound {duplicates_found} groups of duplicate categories.")

if __name__ == '__main__':
    analyze()
