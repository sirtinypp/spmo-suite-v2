import os

file_path = '/app/inventory/templates/inventory/asset_list.html'

try:
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix 1: Add spaces around ==
    # We use simple string replacement which is robust against regex nuances
    content = content.replace('selected_class==c', 'selected_class == c')
    content = content.replace('selected_nature==n', 'selected_nature == n')
    content = content.replace('selected_status==s', 'selected_status == s')
    content = content.replace('selected_department==d.id', 'selected_department == d.id')
    
    # Fix 2: Join split 'if' tag
    # The split looks like:
    # {% if search_term or selected_class or selected_nature or selected_status or selected_office or
    # selected_department %}
    # We can normalize whitespace to find it, or just target the strings.
    # Let's try to replace the newline sequence.
    
    # Detect the specific split. 
    # It might vary by line ending \n or \r\n. 
    # Python's read() usually handles universal newlines but we should be careful.
    
    split_str = "{% if search_term or selected_class or selected_nature or selected_status or selected_office or\n                        selected_department %}"
    joined_str = "{% if search_term or selected_class or selected_nature or selected_status or selected_office or selected_department %}"
    
    # Try multiple indentation variants just in case
    variations = [
        "{% if search_term or selected_class or selected_nature or selected_status or selected_office or\n                        selected_department %}",
        "{% if search_term or selected_class or selected_nature or selected_status or selected_office or\n        selected_department %}",
        "{% if search_term or selected_class or selected_nature or selected_status or selected_office or\n    selected_department %}",
        "{% if search_term or selected_class or selected_nature or selected_status or selected_office or\nselected_department %}",
        # Also try with just "selected_department" (no indent)
    ]

    replaced_split = False
    for v in variations:
        if v in content:
            content = content.replace(v, joined_str)
            replaced_split = True
            print(f"Fixed split 'if' tag using variation: {repr(v)}")
            break
            
    if not replaced_split:
        # Fallback: regex search if simple replace fails
        import re
        pattern = r"\{%\s*if\s+search_term.+?selected_department\s*%\}"
        # This is risky if we don't construct it right.
        # Let's try basic multiline replace with regex
        content = re.sub(
            r'\{% if search_term or selected_class or selected_nature or selected_status or selected_office or\s+selected_department %\}',
            '{% if search_term or selected_class or selected_nature or selected_status or selected_office or selected_department %}',
            content
        )
        print("Attempted regex fix for split 'if' tag.")

    # Fix 3: Fix split {{ asset.get_status_display }}
    # It seems to be causing issues or text error. Consolidate to one line.
    content = re.sub(
        r'\{\{\s*asset\.get_status_display\s*\}\}', 
        '{{ asset.get_status_display }}', 
        content, 
        flags=re.DOTALL
    )
    print("Fixed split 'asset.get_status_display' tag.")
    
    # Also fix the weird one in line 169 which might be:
    # <i ...></i>{{ asset.get_status_display
    # }}
    # Regex to capture it with the preceding tag to be sure, or just the tag itself.
    # The previous regex \s* includes newlines, so it should catch it.
    
    # Let's double check if there are any other split tags causing issues.
    # {{ asset.department.name|default:asset.assigned_office }}
    content = re.sub(
        r'\{\{\s*asset\.department\.name\|default:asset\.assigned_office\s*\}\}',
        '{{ asset.department.name|default:asset.assigned_office }}',
        content,
        flags=re.DOTALL
    )

    with open(file_path, 'w') as f:
        f.write(content)
        
    print(f"Successfully processed {file_path}")

except Exception as e:
    print(f"Error processing file: {e}")
