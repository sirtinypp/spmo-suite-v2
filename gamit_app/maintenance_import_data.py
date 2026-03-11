import os
import django
import sys
import tablib

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from inventory.resources import AssetResource
from inventory.models import Asset

# Path inside the container where we will mount/copy the CSV
file_path = '/app/fresh_data_march_2026.csv'

def run_import():
    if not os.path.exists(file_path):
        print(f"ERROR: Cannot find {file_path}")
        return

    print(f"Reading fresh data from {file_path}...")
    with open(file_path, 'rb') as f:
        data = f.read()
    
    dataset = None
    # Try multiple encodings for robustness
    for encoding in ('utf-8', 'utf-8-sig', 'cp1252', 'latin-1'):
        try:
            dataset = tablib.Dataset().load(data.decode(encoding), format='csv')
            print(f"✅ Decoded with {encoding}. Found {len(dataset)} rows.")
            break
        except Exception:
            continue
            
    if not dataset:
        print("❌ CRITICAL: Failed to load CSV with any standard encoding.")
        return
        
    print("🚀 Starting import via AssetResource...")
    resource = AssetResource()
    # dry_run=False to actually commit the changes
    result = resource.import_data(dataset, dry_run=False)
    
    if result.has_errors():
        print("⚠️ Import completed with some row errors:")
        for count, (idx, errors) in enumerate(result.row_errors()):
            print(f"Row {idx} error: {errors}")
            if count > 10:
                print("... and more errors")
                break
        for error in result.base_errors:
            print(f"Base error: {error.error}")
    else:
        print(f"⭐ Success! Imported {len(dataset)} rows without errors.")
        
    print(f"Total Assets now in DB: {Asset.objects.count()}")

if __name__ == "__main__":
    run_import()
