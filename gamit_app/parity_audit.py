import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from django.contrib.auth.models import User
from workflow.models import Persona, Role

print("="*40)
print("GAMIT LOCAL PARITY AUDIT")
print("="*40)
print(f"Total Users: {User.objects.count()}")
print(f"Total Personas: {Persona.objects.count()}")
print("-"*40)
print(f"{'USERNAME':<15} | {'ROLE':<20} | {'DEPARTMENT'}")
print("-"*40)

for p in Persona.objects.select_related('user', 'role', 'department').all():
    dept = p.department.name if p.department else "N/A"
    print(f"{p.user.username:<15} | {p.role.name:<20} | {dept}")

print("="*40)
