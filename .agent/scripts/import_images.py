import os
import shutil
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gamit_core.settings")
django.setup()

from inventory.models import Asset
from django.conf import settings

media_root = settings.MEDIA_ROOT
tmp_import_dir = os.path.join(media_root, 'tmp_import')

# Target dirs
condition_dir = os.path.join(media_root, 'assets', 'condition')
serial_dir = os.path.join(media_root, 'assets', 'serials')
os.makedirs(condition_dir, exist_ok=True)
os.makedirs(serial_dir, exist_ok=True)

actual_asset_dir = os.path.join(tmp_import_dir, 'Actual Asset')
serial_asset_dir = os.path.join(tmp_import_dir, 'Serial')

def import_folder(source_folder, target_folder, field_name, db_prefix):
    if not os.path.exists(source_folder):
        print(f"Skipping {source_folder} - not found.")
        return 0, 0
    matched = 0
    missing = 0
    for filename in os.listdir(source_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            # e.g. "316103.png" -> "316103"
            number = os.path.splitext(filename)[0].strip()
            
            # Build the expected PAR format. E.g., PAR-316103
            par_number = f"PAR-{number}"
            
            # Find the Asset
            asset = Asset.objects.filter(property_number=par_number).first()
            if asset:
                # Move the file physically
                source_path = os.path.join(source_folder, filename)
                target_filename = f"{par_number}{os.path.splitext(filename)[1]}"
                target_path = os.path.join(target_folder, target_filename)
                
                shutil.copy2(source_path, target_path)
                
                # Update DB (relative to MEDIA_ROOT)
                db_path = f"{db_prefix}/{target_filename}"
                setattr(asset, field_name, db_path)
                asset.save()
                matched += 1
                # print(f"✅ Linked {par_number} -> {field_name}")
            else:
                missing += 1
                print(f"❌ Missing Asset for PAR: {par_number} (File: {filename})")
    return matched, missing

print("🚀 Starting Bulk Image Import...")
m1, f1 = import_folder(actual_asset_dir, condition_dir, 'image_condition', 'assets/condition')
m2, f2 = import_folder(serial_asset_dir, serial_dir, 'image_serial', 'assets/serials')

print("-" * 40)
print(f"Actual Condition: Matched {m1} | Missing/Skipped {f1}")
print(f"Serial Numbers  : Matched {m2} | Missing/Skipped {f2}")
print("🎉 Import Script Complete.")
