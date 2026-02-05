import os
import django
import sys

# Add the project root (gfa_app) to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from travel.forms import BookingRequestForm

try:
    form = BookingRequestForm()
    print("Form Fields:", list(form.fields.keys()))
    if "full_name" in form.fields:
        print("✅ full_name is present.")
    else:
        print("❌ full_name is MISSING.")
except Exception as e:
    print(f"Error initializing form: {e}")
