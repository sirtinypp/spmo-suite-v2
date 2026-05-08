import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()
from django.contrib.auth.models import User

users_to_check = ['grootadmin', 'xiarabasa12']
for username in users_to_check:
    user = User.objects.filter(username=username).first()
    if user:
        print(f"[{username}] Found! Superuser: {user.is_superuser}, Staff: {user.is_staff}, Email: {user.email}")
    else:
        print(f"[{username}] NOT FOUND")
