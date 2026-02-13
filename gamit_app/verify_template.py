import os
import sys
import django
from django.template import Template, Context, Engine
from django.conf import settings

# Setup Django Environment
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

def check_file_content():
    print("--- Checking File Content (Lines 160-180) ---")
    file_path = '/app/inventory/templates/inventory/asset_list.html'
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if 160 <= i <= 180:
                    print(f"{i+1}: {line.rstrip()}")
    except Exception as e:
        print(f"Error reading file: {e}")

def test_template_rendering():
    print("\n--- Testing Template Rendering ---")
    try:
        # Load the template file
        with open('/app/inventory/templates/inventory/asset_list.html', 'r') as f:
            template_content = f.read()
        
        # Configure a basic engine to parse it. 
        # We need libraries and settings, but for syntax checking, basic parsing might suffice.
        # However, it extends 'layout.html' and loads 'humanize'. 
        # So we should use the configured Django engine.
        
        from django.template.loader import get_template
        
        # This parses the template and its dependencies
        template = get_template('inventory/asset_list.html')
        print("Template syntax is VALID.")
        
    except Exception as e:
        print(f"Template Syntax Error: {e}")
        # Print the traceback if needed
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_file_content()
    test_template_rendering()
