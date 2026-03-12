import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from inventory.resources import AssetResource
from inventory.models import Asset
import tablib

file_path = '/app/import.csv'

def run_import():
    if not os.path.exists(file_path):
        print(f"Cannot find {file_path}")
        return

    with open(file_path, 'rb') as f:
        data = f.read()
    
    dataset = None
    for encoding in ('utf-8', 'utf-8-sig', 'cp1252', 'latin-1'):
        try:
            dataset = tablib.Dataset().load(data.decode(encoding), format='csv')
            print(f"Decoded with {encoding}, found {len(dataset)} rows.")
            break
        except Exception as e:
            continue
            
    if not dataset:
        print("Failed to load CSV")
        return
        
    resource = AssetResource()
    result = resource.import_data(dataset, dry_run=False)
    
    if result.has_errors():
        print("Import completed with some row errors:")
        for count, (idx, errors) in enumerate(result.row_errors()):
            print(f"Row {idx} error: {errors}")
            if count > 5:
                print("... and more errors")
                break
        for error in result.base_errors:
            print(f"Base error: {error.error}")
    else:
        print(f"Success! Imported {len(dataset)} rows without errors.")
        
    print(f"Total Assets in DB: {Asset.objects.count()}")
    
run_import()
