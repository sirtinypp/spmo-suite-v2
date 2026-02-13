import os
import django
import sys
from django.contrib.auth.models import User

# Setup Django Environment
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from inventory.models import UserProfile

def test_user_creation():
    username = "test_user_signals"
    if User.objects.filter(username=username).exists():
        User.objects.filter(username=username).delete()
        print(f"Deleted existing user: {username}")

    print(f"Creating user: {username}")
    user = User.objects.create_user(username=username, password="password123")
    
    try:
        profile = UserProfile.objects.get(user=user)
        print(f"[SUCCESS] UserProfile created: {profile}")
        print(f"  Role: {profile.role}")
        print(f"  Department: {profile.department}")
    except UserProfile.DoesNotExist:
        print("[FAILURE] UserProfile was NOT created automatically.")

if __name__ == '__main__':
    test_user_creation()
