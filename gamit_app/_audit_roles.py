import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()
from django.contrib.auth.models import User
from workflow.models import Persona

print("User Role Assignment Audit\n" + "="*40)
usernames = [
    'ajbasa', 'ilbagus', 'jldelacruz', 'mmpedrosa', 
    'srcura', 'etsardual', 'jvdelmundo', 'vpresurreccion', 'grootadmin'
]

users = User.objects.filter(username__in=usernames).order_by('username')

for user in users:
    personas = Persona.objects.filter(user=user)
    role_names = [p.role.name for p in personas if p.role]
    role_codes = [p.role.code for p in personas if p.role]
    
    roles_str = ", ".join(f"{name} ({code})" for name, code in zip(role_names, role_codes))
    if not roles_str:
        roles_str = "NO ROLES ASSIGNED"
        
    print(f"User: {user.first_name} {user.last_name} ({user.username})")
    print(f"Roles: {roles_str}")
    print(f"Superuser: {user.is_superuser} | Staff: {user.is_staff}")
    print("-" * 40)
