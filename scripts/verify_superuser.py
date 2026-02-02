import os
import django
from django.contrib.auth import get_user_model

def verify_superuser():
    User = get_user_model()
    count = User.objects.filter(username='ajbasa').count()
    print(f"User 'ajbasa' exists: {count > 0} (Count: {count})")

if __name__ == '__main__':
    verify_superuser()
