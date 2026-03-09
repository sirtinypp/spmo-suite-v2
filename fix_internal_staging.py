import re
import os

def fix_file(path, pattern, replacement):
    if os.path.exists(path):
        print(f"Patching: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        
        if new_content != content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Successfully patched: {path}")
        else:
            print(f"No changes needed for: {path}")
    else:
        print(f"File not found: {path}")

# 1. Fix split {% endif %} in asset_detail.html
# Pattern: {% endif followed by newline and optional whitespace and %}
fix_file('/app/inventory/templates/inventory/asset_detail.html', 
         r'\{%\s*endif\s*\n\s*%\s*\}', 
         '{% endif %}')

# 2. Fix comparison operators in asset_list.html
# Pattern: selected_class==c -> selected_class == c
fix_file('/app/inventory/templates/inventory/asset_list.html', 
         r'selected_class==c', 
         'selected_class == c')
fix_file('/app/inventory/templates/inventory/asset_list.html', 
         r'selected_nature==n', 
         'selected_nature == n')
fix_file('/app/inventory/templates/inventory/asset_list.html', 
         r'selected_status==s', 
         'selected_status == s')

print("Internal Patching Complete.")
