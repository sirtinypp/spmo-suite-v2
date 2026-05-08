from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from workflow.models import Role, Persona, WorkflowStep, SignatorySlot
from inventory.models import Department

class Command(BaseCommand):
    help = 'Seeds institutional data (Roles, Ghost Army Personas, and Signatory Slots)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Institutional Seeding...'))

        # 1. Update/Create Roles with Categories
        roles_data = [
            ('SPMO_CHIEF', 'Director / SPMO Chief', 'OPERATOR'),
            ('SPMO_ADMIN_SUPERVISOR', 'SPMO Admin Supervisor', 'OPERATOR'),
            ('SPMO_SUPERVISOR', 'SPMO Inventory Supervisor', 'OPERATOR'),
            ('INSPECTION_OFFICER', 'Inspection Officer', 'OPERATOR'),
            ('SPMO_AO', 'SPMO Inventory Officer', 'OPERATOR'),
            ('SPMO_CLERK', 'SPMO Inventory Clerk', 'OPERATOR'),
            ('UNIT_HEAD', 'Unit / Department Head', 'CLIENT'),
            ('UNIT_AO', 'Unit Accountable Officer', 'CLIENT'),
        ]

        for code, name, category in roles_data:
            role, created = Role.objects.get_or_create(code=code, defaults={'name': name, 'category': category})
            if not created:
                role.category = category
                role.save()
            self.stdout.write(f"  [Role] {code} - {category}")

        # 2. Ensure Departments & Ghost Army (Example Subset of Departments)
        dept_names = [
            "Office of the President", "Office of the Vice President", "SPMO", "HRDO", "Accounting Office",
            "Cashier's Office", "Budget Office", "Supply Office", "Building Services", "Security Division",
            "University Health Service", "University Library", "College of Arts & Sciences", "College of Engineering",
            "College of Education", "College of Law", "College of Medicine", "College of Nursing",
            "College of Pharmacy", "College of Public Health", "College of Social Work", "School of Statistics",
            "Institute of Biology", "Institute of Chemistry", "Institute of Physics", "Institute of Mathematics",
            "National Institute of Geological Sciences", "Marine Science Institute", "Computer Science",
            "Electrical Engineering", "Mechanical Engineering", "Civil Engineering"
        ]

        # Use an existing user as a "Ghost" holder or system-wide admin
        ghost_user = User.objects.filter(is_superuser=True).first()
        if not ghost_user:
            self.stdout.write(self.style.ERROR("No superuser found. Create one first."))
            return

        for d_name in dept_names:
            dept, _ = Department.objects.get_or_create(name=d_name)
            
            # Create Unit Head Persona
            Persona.objects.get_or_create(
                user=ghost_user,
                department=dept,
                role=Role.objects.get(code='UNIT_HEAD'),
                defaults={'position_title': f'Head, {d_name}'}
            )
            # Create Unit AO Persona
            Persona.objects.get_or_create(
                user=ghost_user,
                department=dept,
                role=Role.objects.get(code='UNIT_AO'),
                defaults={'position_title': f'Accountable Officer, {d_name}'}
            )
        self.stdout.write(self.style.SUCCESS(f"  [Ghost Army] 64 Personas deployed across {len(dept_names)} departments."))

        # 3. Wire Signatory Slots for Batch Acquisition
        slots_to_add = [
            ('Verify Completeness (SPMO)', 'SPMO_AO', 'Prepared By', 1),
            ('Release / Save IAR', 'INSPECTION_OFFICER', 'Inspected By', 2),
            ('Verify Completeness (Supv)', 'SPMO_SUPERVISOR', 'Reviewed By', 3),
            ('For Chief Final Approval', 'SPMO_CHIEF', 'Issued By', 4),
            ('Awaiting Unit Acceptance', 'UNIT_HEAD', 'Received By', 5),
        ]

        for step_label, role_code, slot_label, rank in slots_to_add:
            step = WorkflowStep.objects.filter(label=step_label, phase__workflow__process__code='BATCH_ACQUISITION').first()
            if step:
                role = Role.objects.get(code=role_code)
                SignatorySlot.objects.get_or_create(step=step, role=role, label=slot_label, rank=rank)
                self.stdout.write(f"  [Slot] Wired: {slot_label} to {step_label}")
            else:
                self.stdout.write(self.style.WARNING(f"  [Slot] Step [{step_label}] not found. Skipping."))

        self.stdout.write(self.style.SUCCESS('Institutional Seeding Complete.'))
