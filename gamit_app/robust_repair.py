import os
import re

def robust_template_repair(directory):
    # Regex to find any {{ ... }} or {% ... %} tags that span multiple lines
    # or have excessive/missing internal whitespace.
    # Flags=re.DOTALL allows the dot to match newlines inside the tag.
    
    re_var = re.compile(r'\{\{(.*?)\}\}', re.DOTALL)
    re_tag = re.compile(r'\{%(.*?)%\}', re.DOTALL)
    
    repaired_count = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content = content
                    
                    # 1. Rejoin {{ ... }}
                    new_content = re_var.sub(
                        lambda m: '{{ ' + ' '.join(m.group(1).split()) + ' }}', 
                        new_content
                    )
                    
                    # 2. Rejoin {% ... %}
                    # Also handles operator spacing indirectly by normalizing internal spaces
                    # But we'll be careful: ' '.join(m.group(1).split()) is very safe.
                    new_content = re_tag.sub(
                        lambda m: '{% ' + ' '.join(m.group(1).split()) + ' %}', 
                        new_content
                    )
                    
                    # 3. Special fix for comparison operators if still joined
                    # (e.g., if content was var==val without ANY spaces, split() won't help)
                    def fix_ops(match):
                        inner = match.group(1)
                        # Space out operators if joined to alpha-numeric chars
                        for op in ['==', '!=', '>=', '<=', '>', '<']:
                            # Replace operator with spaced version
                            inner = inner.replace(op, f' {op} ')
                        # Clean up any potential double spaces introduced
                        return '{% ' + ' '.join(inner.split()) + ' %}'

                    new_content = re_tag.sub(fix_ops, new_content)

                    if new_content != content:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Repaired: {path}")
                        repaired_count += 1
                except Exception as e:
                    print(f"Error repairing {path}: {e}")
    
    print(f"Total files repaired: {repaired_count}")

if __name__ == "__main__":
    # Target directory (supports both host and container if /app exists)
    templates_dir = "/app/inventory/templates/inventory" if os.path.exists("/app") else r"c:\Users\Aaron\spmo-suite - Copy\gamit_app\inventory\templates\inventory"
    robust_template_repair(templates_dir)
