import sys
sys.path.append('/app')
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'office_supplies_project.settings')
django.setup()

from supplies.models import Supplier, Department, Product, AnnualProcurementPlan, UserProfile

def analyze_model(model_class, name_field='name'):
    print(f"\n--- Analyzing {model_class.__name__} ---")
    
    normalized_map = {}
    all_objs = model_class.objects.all()
    
    for obj in all_objs:
        val = getattr(obj, name_field)
        if not val: continue
        norm_name = str(val).strip().lower()
        if norm_name not in normalized_map:
            normalized_map[norm_name] = []
        normalized_map[norm_name].append(obj)
        
    duplicates_found = 0
    for norm_name, objs in normalized_map.items():
        if len(objs) > 1:
            duplicates_found += 1
            print(f"Duplicate Group: '{norm_name}'")
            for obj in objs:
                # Count relationships (generic check)
                related_count = 0
                if model_class == Supplier:
                    related_count = Product.objects.filter(supplier=obj).count()
                elif model_class == Department:
                    # Check APP, UserProfile, Orders
                    app_count = AnnualProcurementPlan.objects.filter(department=obj).count()
                    profile_count = UserProfile.objects.filter(department=obj).count()
                    related_count = f"APP:{app_count}, Users:{profile_count}"
                
                print(f"  - ID: {obj.id} | Name: '{getattr(obj, name_field)}' | Usage: {related_count}")

    if duplicates_found == 0:
        print(f"No duplicate {model_class.__name__}s found.")
    else:
        print(f"Found {duplicates_found} duplicate groups for {model_class.__name__}.")
    return duplicates_found

if __name__ == '__main__':
    s_count = analyze_model(Supplier)
    d_count = analyze_model(Department)
    
    if s_count == 0 and d_count == 0:
        print("\nSUCCESS: Database appears fully normalized for these tables.")
    else:
        print("\nACTION REQUIRED: Duplicates found.")
