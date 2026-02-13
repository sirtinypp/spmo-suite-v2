from django.core.management.base import BaseCommand
from inventory.models import Asset, UserProfile, Department

class Command(BaseCommand):
    help = 'Migrates legacy text-based office fields to Department ForeignKeys'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting Department Migration...")

        # 1. Collect Unique Office Names
        office_names = set()
        
        # From Assets
        assets = Asset.objects.exclude(assigned_office__isnull=True).exclude(assigned_office__exact='')
        for asset in assets:
            office_names.add(asset.assigned_office.strip())
            
        # From UserProfiles
        profiles = UserProfile.objects.exclude(office__isnull=True).exclude(office__exact='')
        for profile in profiles:
            office_names.add(profile.office.strip())

        self.stdout.write(f"Found {len(office_names)} unique offices/departments.")

        # 2. Create Departments
        for name in office_names:
            dept, created = Department.objects.get_or_create(name=name)
            if created:
                # Code field removed as per user request
                dept.save()
                self.stdout.write(f"  [CREATED] {name}")
            else:
                self.stdout.write(f"  [EXISTS] {name}")

        # 3. Link Assets
        self.stdout.write("\nLinking Assets to Departments...")
        count_assets = 0
        for asset in assets:
            dept = Department.objects.filter(name=asset.assigned_office.strip()).first()
            if dept:
                asset.department = dept
                asset.save()
                count_assets += 1
        self.stdout.write(f"  Linked {count_assets} assets.")

        # 4. Link UserProfiles
        self.stdout.write("\nLinking Users to Departments...")
        count_users = 0
        for profile in profiles:
            dept = Department.objects.filter(name=profile.office.strip()).first()
            if dept:
                profile.department = dept
                profile.save()
                count_users += 1
        self.stdout.write(f"  Linked {count_users} users.")

        self.stdout.write(self.style.SUCCESS("Migration Complete."))
