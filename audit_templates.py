import re
import os

def audit_template(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for split tags
    split_tags = re.findall(r'(\{%[^%]*?\n[^%]*?%\}|\{\{[^\}]*?\n[^\}]*?\}\})', content)
    
    # Check for unspaced ==
    unspaced_ops = re.findall(r'\{%\s*if\s+.*?[^\s]==[^\s].*?%\}', content)
    
    # Check for unspaced == in other tags too
    unspaced_ops_gen = re.findall(r'\{%.*?[^\s]==[^\s].*?%\}', content)

    # Count if/endif
    if_count = len(re.findall(r'\{%\s*if\s+.*?%\}', content))
    endif_count = len(re.findall(r'\{%\s*endif\s*%\}', content))
    
    print(f"Audit Results for {path}:")
    print(f"  Split Tags: {len(split_tags)}")
    for t in split_tags:
        print(f"    - {t.strip()}")
    print(f"  Unspaced Operators: {len(unspaced_ops)}")
    for op in unspaced_ops:
        print(f"    - {op}")
    print(f"  If Count: {if_count}, Endif Count: {endif_count}")
    if if_count != endif_count:
        print("  WARNING: Unbalanced IF/ENDIF blocks!")

audit_template('gamit_app/inventory/templates/inventory/asset_list.html')
audit_template('gamit_app/inventory/templates/inventory/asset_detail.html')
