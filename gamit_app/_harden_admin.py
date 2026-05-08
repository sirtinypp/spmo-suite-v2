import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()
from django.contrib.auth.models import User

# Rule: Only grootadmin is_staff=True. Everyone else is_staff=False.
users = User.objects.all()

print('Hardening Django Admin Access...')
for u in users:
    if u.username == 'grootadmin':
        if not u.is_staff:
            u.is_staff = True
            u.save()
            print(f'  [KEEP] {u.username} (Staff enabled)')
    else:
        if u.is_staff:
            u.is_staff = False
            u.save()
            print(f'  [REVOKE] {u.username} (Staff disabled)')

print('\nAccess Hardening Complete. Only grootadmin has Django Admin access.')
