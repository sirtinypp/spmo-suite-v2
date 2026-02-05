import os
import django
from django.contrib.auth import get_user_model


def create_superuser():
    User = get_user_model()
    username = "grootadmin"
    email = "grootadmin@up.edu.ph"
    password = "xiarabasa12"

    if not User.objects.filter(username=username).exists():
        print(f"Creating superuser: {username}")
        User.objects.create_superuser(username, email, password)
    else:
        print(f"Superuser {username} already exists. Updating password.")
        u = User.objects.get(username=username)
        u.set_password(password)
        u.save()


if __name__ == "__main__":
    create_superuser()
