import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()
from django.contrib.auth.models import User

user = User.objects.filter(username='grootadmin').first()
if user:
    user.set_password('xiarabasa12')
    user.save()
    print('Password updated for grootadmin')
else:
    print('grootadmin not found')
