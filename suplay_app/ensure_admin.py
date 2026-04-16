import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'office_supplies_project.settings')
django.setup()

from django.contrib.auth.models import User

for username in ['grootadmin', 'xiarabasa12']:
    u = User.objects.filter(username=username).first()
    if u:
        u.is_staff = True
        u.is_superuser = True
        u.save()
        print(f"User '{username}' updated: is_staff=True, is_superuser=True")
    else:
        print(f"User '{username}' NOT found.")
