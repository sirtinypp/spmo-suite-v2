import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "config.settings"
)  # Changed loop logic below
django.setup()

User = get_user_model()
USERNAME = "grootadmin"
PASSWORD = "xiarabasa12"
EMAIL = "admin@example.com"

try:
    if User.objects.filter(username=USERNAME).exists():
        print(f"User {USERNAME} found. Update password.")
        u = User.objects.get(username=USERNAME)
        u.set_password(PASSWORD)
        u.is_superuser = True
        u.is_staff = True
        u.save()
        print(f"Password updated for {USERNAME}")
    else:
        print(f"User {USERNAME} not found. Creating...")
        User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
        print(f"Superuser {USERNAME} created.")
except Exception as e:
    print(f"Error: {e}")
