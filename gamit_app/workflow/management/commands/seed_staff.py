from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from workflow.models import Role, Persona

class Command(BaseCommand):
    help = 'Seeds standard Operations-Global staff users and their personas'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Seeding Standard Operations-Global Users...'))

        # Ensure SYSTEM_DEVELOPER role exists
        Role.objects.get_or_create(
            code='SYSTEM_DEVELOPER',
            defaults={'name': 'System Developer', 'category': 'OPERATOR'}
        )

        staff_data = [
            {
                'username': 'ajbasa',
                'first_name': 'Aaron Christian',
                'last_name': 'Basa',
                'email': 'ajbasa@up.edu.ph',
                'is_staff': True,
                'is_superuser': True,
                'roles': ['SPMO_ADMIN_SUPERVISOR', 'SYSTEM_DEVELOPER'],
            },
            {
                'username': 'grootadmin',
                'first_name': 'Aaron',
                'last_name': 'Basa',
                'email': 'grootadmin@up.edu.ph',
                'is_staff': True,
                'is_superuser': True,
                'roles': ['SYSTEM_DEVELOPER'],
            },
            {
                'username': 'ilbagus',
                'first_name': 'Isagani L.',
                'last_name': 'Bagus',
                'email': 'ilbagus@up.edu.ph',
                'is_staff': True,
                'is_superuser': False,
                'roles': ['SPMO_CHIEF'],
            },
            {
                'username': 'jldelacruz',
                'first_name': 'Julius Mar',
                'last_name': 'Dela Cruz',
                'email': 'jldelacruz4@up.edu.ph',
                'is_staff': True,
                'is_superuser': False,
                'roles': ['SPMO_SUPERVISOR'],
            },
            {
                'username': 'mmpedrosa',
                'first_name': 'Mark Joshua',
                'last_name': 'Pedrosa',
                'email': 'mmpedrosa@up.edu.ph',
                'is_staff': True,
                'is_superuser': False,
                'roles': ['INSPECTION_OFFICER'],
            },
            {
                'username': 'srcura',
                'first_name': 'Sherwin',
                'last_name': 'Cura',
                'email': 'srcura@up.edu.ph',
                'is_staff': True,
                'is_superuser': False,
                'roles': ['SPMO_CLERK'],
            },
            {
                'username': 'etsardual',
                'first_name': 'Eldefonso',
                'last_name': 'Sardual',
                'email': 'etsardual@up.edu.ph',
                'is_staff': True,
                'is_superuser': False,
                'roles': ['SPMO_AO'],
            },
            {
                'username': 'jvdelmundo',
                'first_name': 'Joeven',
                'last_name': 'Del Mundo',
                'email': 'jvdelmundo1@up.edu.ph',
                'is_staff': True,
                'is_superuser': True,
                'roles': ['SPMO_AO'],
            },
            {
                'username': 'vpresurreccion',
                'first_name': 'Augustus',
                'last_name': 'Resurreccion',
                'email': 'vpa@up.edu.ph', # Placeholder if not provided
                'is_staff': True,
                'is_superuser': True,
                'roles': ['SPMO_CHIEF'], # Mapping to Chief for oversight for now
            },
        ]

        for data in staff_data:
            # Get or create user
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'is_staff': data['is_staff'],
                    'is_superuser': data['is_superuser'],
                }
            )
            
            if not created:
                user.email = data['email']
                user.first_name = data['first_name']
                user.last_name = data['last_name']
                user.is_staff = data['is_staff']
                user.is_superuser = data['is_superuser']
                user.save()
            
            status = 'CREATED' if created else 'UPDATED'
            self.stdout.write(f"  [{status}] User: {user.username}")

            # Assign Personas
            for role_code in data['roles']:
                role = Role.objects.filter(code=role_code).first()
                if role:
                    persona, p_created = Persona.objects.get_or_create(
                        user=user,
                        role=role,
                        defaults={'position_title': f"{role.name}"}
                    )
                    p_status = 'NEW' if p_created else 'EXISTS'
                    self.stdout.write(f"    - Persona: {role_code} ({p_status})")
                else:
                    self.stdout.write(self.style.WARNING(f"    - Role {role_code} not found!"))

        self.stdout.write(self.style.SUCCESS('Standard Staff Seeding Complete.'))
