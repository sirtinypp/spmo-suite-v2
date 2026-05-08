import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from django.contrib.auth.models import User
from workflow.models import Persona

AUTHORIZED_USERS = [
    'ajbasa',
    'grootadmin',
    'ilbagus',
    'jldelacruz',
    'mmpedrosa',
    'srcura',
    'etsardual',
    'jvdelmundo',
    'vpresurreccion'
]

# Delete any User that is NOT in the authorized list
deleted_count, details = User.objects.exclude(username__in=AUTHORIZED_USERS).delete()

# Double check total users
total_users = User.objects.count()
active_usernames = list(User.objects.values_list('username', flat=True))

print(f"Purge Complete. Deleted {deleted_count} unauthorized users.")
print(f"Total Users Remaining: {total_users}")
print(f"Active Usernames: {', '.join(active_usernames)}")
