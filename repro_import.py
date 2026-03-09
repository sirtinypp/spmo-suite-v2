import os
import django
import sys

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from inventory.resources import SaneCSV, AssetResource
import tablib

file_path = '/tmp/repro.csv'

def test_repro():
    if not os.path.exists(file_path):
        print(f"ERROR: {file_path} not found")
        return

    with open(file_path, 'rb') as f:
        data = f.read()

    print(f"REPRO: Testing file of size {len(data)} bytes")
    fmt = SaneCSV()
    
    # Manually try the encodings like SaneCSV does but with more verbosity
    print("REPRO: Starting encoding tests...")
    dataset = None
    for encoding in ('utf-8', 'utf-8-sig', 'cp1252', 'latin-1'):
        try:
            decoded = data.decode(encoding)
            print(f"REPRO: Successfully decoded with {encoding}")
            dataset = tablib.Dataset()
            dataset.csv = decoded
            print(f"REPRO: Dataset created with {len(dataset)} rows")
            break
        except Exception as e:
            print(f"REPRO: Failed with {encoding}: {type(e).__name__}: {e}")
    
    if dataset is None:
        print("REPRO: ALL ENCODINGS FAILED")
        return

    # Check headers
    print(f"REPRO: Headers found: {dataset.headers}")
    
    # Test Resource
    resource = AssetResource()
    print("REPRO: Running dry-run import...")
    result = resource.import_data(dataset, dry_run=True)
    
    print(f"REPRO: Import finished. Has errors? {result.has_errors()}")
    if result.has_errors():
        for row_number, errors in result.row_errors():
            print(f"Row {row_number} error: {errors}")
        for error in result.base_errors:
            print(f"Base error: {error.error}")
    else:
        print("REPRO: No errors during dry-run import!")

if __name__ == "__main__":
    test_repro()
