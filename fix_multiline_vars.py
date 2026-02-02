# Fix template variables split across lines
template_path = '/app/inventory/templates/inventory/dashboard.html'

with open(template_path, 'r') as f:
    content = f.read()

# Fix variables split across multiple lines
import re

# Fix highest_name
content = re.sub(
    r'{{\s*highest_name\s*}}',
    '{{ highest_name }}',
    content
)

# Fix top_office_name  
content = re.sub(
    r'{{\s*top_office_name\s*}}',
    '{{ top_office_name }}',
    content
)

# Fix asset.get_asset_class_display
content = re.sub(
    r'{{\s*asset\.get_asset_class_display\s*}}',
    '{{ asset.get_asset_class_display }}',
    content
)

with open(template_path, 'w') as f:
    f.write(content)

print("Template variables normalized successfully")
