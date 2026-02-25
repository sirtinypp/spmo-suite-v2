import re
import os

def fix_template(file_path):
    print(f"Repairing {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Join split {{ ... }} tags
    # Handles: {{ \n field }} , {{ field \n }}, etc.
    content = re.sub(r'\{\{\s*\r?\n\s*', '{{ ', content)
    content = re.sub(r'\s*\r?\n\s*\}\}', ' }}', content)
    
    # 2. Join split {% ... %} tags
    content = re.sub(r'\{%\s*\r?\n\s*', '{% ', content)
    content = re.sub(r'\s*\r?\n\s*%\}', ' %}', content)

    # 3. Specific fix for form fields seen in screenshot
    # Example: {{ \n form.full_name }}
    content = re.sub(r'\{\{\s*form\.', '{{ form.', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Repair complete.")

if __name__ == "__main__":
    target = "/app/travel/templates/travel/form.html"
    if os.path.exists(target):
        fix_template(target)
    else:
        print(f"Error: Target {target} not found inside container.")
