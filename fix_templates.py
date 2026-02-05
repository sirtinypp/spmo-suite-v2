import re

# Fix form.html
with open("gfa_app/travel/templates/travel/form.html", "r", encoding="utf-8") as f:
    content = f.read()

# Replace split template tags with single-line versions
content = re.sub(r"\{\{\s*\r?\n\s+", "{{ ", content)

with open(
    "gfa_app/travel/templates/travel/form.html", "w", encoding="utf-8", newline="\r\n"
) as f:
    f.write(content)

print("Fixed form.html")

# Fix dashboard.html
with open("gfa_app/travel/templates/travel/dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(r"\{\{\s*\r?\n\s+", "{{ ", content)

with open(
    "gfa_app/travel/templates/travel/dashboard.html",
    "w",
    encoding="utf-8",
    newline="\r\n",
) as f:
    f.write(content)

print("Fixed dashboard.html")
