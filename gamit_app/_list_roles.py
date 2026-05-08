import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()
from workflow.models import Role

print("Available Roles in Database:")
for role in Role.objects.all():
    print(f"Code: {role.code}, Name: {role.name}")
