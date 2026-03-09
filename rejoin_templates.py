import os
import re

TEMPLATES = [
    "gamit_app/inventory/templates/inventory/asset_list.html",
    "gamit_app/inventory/templates/inventory/asset_detail.html",
    "gamit_app/inventory/templates/inventory/dashboard.html",
    "gamit_app/inventory/templates/inventory/asset_add.html",
]

def rejoin_tags(content):
    # 1. Rejoin {{ ... }} tags
    content = re.sub(r'\{\{(.*?)\}\}', lambda m: '{{ ' + ' '.join(m.group(1).split()) + ' }}', content, flags=re.DOTALL)
    
    # 2. Rejoin {% ... %} tags
    content = re.sub(r'\{%(.*?)%\}', lambda m: '{% ' + ' '.join(m.group(1).split()) + ' %}', content, flags=re.DOTALL)
    
    # 3. Fix common missing spaces around == in if/elif/ifequal
    # Explicitly targeting Django comparison tags
    content = re.sub(r'(\{%\s*(?:if|elif|ifequal)\s+[^%]+?)(==|!=|>=|<=)([^%]+?%\} )', r'\1 \2 \3', content)
    
    return content

for t_path in TEMPLATES:
    if not os.path.exists(t_path):
        print(f"Skipping: {t_path} (Not found)")
        continue
    
    print(f"Processing: {t_path}")
    with open(t_path, 'r', encoding='utf-8') as f:
        original = f.read()
    
    fixed = rejoin_tags(original)
    
    with open(t_path, 'w', encoding='utf-8') as f:
        f.write(fixed)
    print(f"Successfully Purified: {t_path}")
