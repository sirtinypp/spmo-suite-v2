import os
import re

def comprehensive_repair(directory):
    split_patterns = [
        (r'\{\s+\{', '{{'),
        (r'\}\s+\}', '}}'),
        (r'\{\s+\%', '{%'),
        (r'\%\s+\}', '%}'),
    ]
    
    def fix_operators(text):
        def replace_tag(match):
            tag_content = match.group(1)
            # Find comparison operators inside tags and ensure they have spaces
            # Using regex to find ops not surrounded by spaces
            # ops are ==, !=, >=, <=, >, <
            for op in ['==', '!=', '>=', '<=', '>', '<']:
                # Replace with spaced version
                tag_content = tag_content.replace(op, f' {op} ')
            
            # Condense multiple spaces
            tag_content = re.sub(r'\s+', ' ', tag_content).strip()
            
            # Re-join combined ops incorrectly split by the simple replace above
            tag_content = tag_content.replace('> =', '>=').replace('< =', '<=').replace('! =', '!=').replace('= =', '==')
            return f'{{% {tag_content} %}}'

        return re.sub(r'\{%(.*?)%\}', replace_tag, text, flags=re.DOTALL)

    repaired_count = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content = content
                    for pattern, replacement in split_patterns:
                        new_content = re.sub(pattern, replacement, new_content)
                    new_content = fix_operators(new_content)
                    
                    if new_content != content:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Repaired: {path}")
                        repaired_count += 1
                except Exception as e:
                    print(f"Error repairing {path}: {e}")
    
    print(f"Total files repaired internally: {repaired_count}")

if __name__ == "__main__":
    templates_dir = "/app/inventory/templates/inventory"
    comprehensive_repair(templates_dir)
