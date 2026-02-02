import sys
sys.path.append('/app')
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'office_supplies_project.settings')
django.setup()

from supplies.models import Category

def list_cats():
    print("--- Current Categories ---")
    cats = Category.objects.all().order_by('name')
    for c in cats:
        print(f"{c.id}: {c.name}")

if __name__ == '__main__':
    list_cats()
