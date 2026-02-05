# Fix Django template syntax errors
template_path = "/app/inventory/templates/inventory/dashboard.html"

with open(template_path, "r") as f:
    content = f.read()

# Fix spacing in template conditionals
content = content.replace("selected_class==c", "selected_class == c")
content = content.replace("selected_nature==n", "selected_nature == n")
content = content.replace("selected_status==s", "selected_status == s")

with open(template_path, "w") as f:
    f.write(content)

print("Template syntax fixed successfully")
