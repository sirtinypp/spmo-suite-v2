
from supplies.models import AnnualProcurementPlan, Order, UserProfile, Department
from django.db import transaction

def run():
    print("Starting Data Migration for Departments...")
    
    with transaction.atomic():
        # --- 1. AnnualProcurementPlan ---
        print("Migrating APP Allocations...")
        # Get all unique department names that are not empty
        app_depts = AnnualProcurementPlan.objects.exclude(department__isnull=True).exclude(department='').values_list('department', flat=True).distinct()
        
        for dept_name in app_depts:
            dept_obj, created = Department.objects.get_or_create(name=dept_name.strip())
            if created:
                print(f"  Created Department: {dept_obj.name}")
            
            # Update all APPs with this name
            count = AnnualProcurementPlan.objects.filter(department=dept_name).update(department_new=dept_obj)
            print(f"  Linked {count} APP items to '{dept_obj.name}'")

        # --- 2. Order ---
        print("\nMigrating Orders...")
        order_depts = Order.objects.exclude(department__isnull=True).exclude(department='').values_list('department', flat=True).distinct()
        
        for dept_name in order_depts:
            dept_obj, created = Department.objects.get_or_create(name=dept_name.strip())
            # Update Orders
            count = Order.objects.filter(department=dept_name).update(department_new=dept_obj)
            print(f"  Linked {count} Orders to '{dept_obj.name}'")

        # --- 3. UserProfile ---
        print("\nMigrating UserProfiles...")
        profile_depts = UserProfile.objects.exclude(department__isnull=True).exclude(department='').values_list('department', flat=True).distinct()
        
        for dept_name in profile_depts:
            dept_obj, created = Department.objects.get_or_create(name=dept_name.strip())
            # Update Profiles
            count = UserProfile.objects.filter(department=dept_name).update(department_new=dept_obj)
            print(f"  Linked {count} Profiles to '{dept_obj.name}'")

    print("\nData Migration Completed Successfully!")

if __name__ == "__main__" or True: # Force run in shell
    run()
