import os
import django
import sys
import re

print("--- DEBUG SCRIPT STARTED ---")

# Auto-detect settings module from manage.py
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    try:
        if os.path.exists('manage.py'):
            with open('manage.py', 'r') as f:
                content = f.read()
                match = re.search(r"['\"]DJANGO_SETTINGS_MODULE['\"]\s*,\s*['\"]([^'\"]+)['\"]", content)
                if match:
                    settings_mod = match.group(1)
                    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_mod)
                    print(f"Auto-detected settings: {settings_mod}")
                else:
                    print("Could not find DJANGO_SETTINGS_MODULE in manage.py")
        else:
            print("manage.py not found in current directory.")
            
    except Exception as e:
        print(f"Error reading manage.py: {e}")

try:
    django.setup()
    print("Django setup complete.")
except Exception as e:
    print(f"CRITICAL ERROR during setup: {e}")
    # Print environment for debugging
    # print(os.environ)
    sys.exit(1)

from django.contrib.auth import get_user_model

def debug_auth():
    User = get_user_model()
    username = 'grootadmin'
    password = 'xiarabasa12'
    
    print(f"--- DEBUGGING USER: {username} ---")
    
    try:
        user = User.objects.get(username=username)
        print(f"1. User exists: YES (ID: {user.id})")
        print(f"2. is_active: {user.is_active}")
        print(f"3. is_staff: {user.is_staff}")
        print(f"4. is_superuser: {user.is_superuser}")
        
        check = user.check_password(password)
        print(f"5. check_password match? : {check}")
        
        if not check:
            print("   -> Password mismatch! Resetting password manually now...")
            user.set_password(password)
            user.save()
            print("   -> Password reset complete. New check:", user.check_password(password))
        else:
            print("   -> Password is CORRECT.")
            
    except User.DoesNotExist:
        print("1. User exists: NO")
        print("   -> Creating user now...")
        try:
            User.objects.create_superuser(username, 'grootadmin@up.edu.ph', password)
            print("   -> User created successfully.")
        except Exception as e:
            print(f"   -> Creation failed: {e}")

if __name__ == '__main__':
    debug_auth()
