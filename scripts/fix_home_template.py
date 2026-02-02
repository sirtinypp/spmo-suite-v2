
import os

file_path = r"c:\Users\Aaron\spmo-suite - Copy\suplay_app\supplies\templates\supplies\home.html"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The erroneous split string
    target = "{% if not request.GET.category and not request.GET.supplier and not request.GET.stock and not search_query\n            %}"
    replacement = "{% if not request.GET.category and not request.GET.supplier and not request.GET.stock and not search_query %}"
    
    if target in content:
        new_content = content.replace(target, replacement)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully replaced content.")
    else:
        # Try a more flexible replacement (ignoring exact whitespace if needed, but let's stick to exact first)
        import re
        pattern = r"{% if not request\.GET\.category .*? search_query\s+%}"
        if re.search(pattern, content, re.DOTALL):
             print("Found pattern via Regex. Replacing...")
             new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
             with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
             print("Successfully replaced content via Regex.")
        else:
            print("Target string not found. Dumping a snippet around line 89:")
            lines = content.splitlines()
            if len(lines) > 90:
                print(lines[88])
                print(lines[89])
            else:
                print("File too short.")

except Exception as e:
    print(f"Error: {e}")
