import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()
from inventory.models import Asset
from django.db.models import Count

print("=== CATEGORY AUDIT ===")
classes = Asset.objects.values('asset_class').annotate(count=Count('id'))
for c in classes:
    print(f"Class Key: '{c['asset_class']}', Count: {c['count']}")

natures = Asset.objects.values('asset_nature').annotate(count=Count('id'))
for n in natures:
    print(f"Nature Key: '{n['asset_nature']}', Count: {n['count']}")

if Asset.objects.exists():
    a = Asset.objects.first()
    print("\n--- SAMPLE ASSET ---")
    print(f"ID: {a.id}, Prop: {a.property_number}")
    print(f"Class raw: {a.asset_class}, Display: {a.get_asset_class_display()}")
    print(f"Nature raw: {a.asset_nature}, Display: {a.get_asset_nature_display()}")
else:
    print("No assets found.")
