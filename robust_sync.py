import re
import os
import subprocess

TEMPLATES = [
    ("gamit_app/inventory/templates/inventory/asset_list.html", "/app/inventory/templates/inventory/asset_list.html"),
    ("gamit_app/inventory/templates/inventory/asset_detail.html", "/app/inventory/templates/inventory/asset_detail.html"),
    ("gamit_app/inventory/templates/inventory/asset_add.html", "/app/inventory/templates/inventory/asset_add.html"),
]
SSH_CMD = "ssh -o ConnectTimeout=5 -p 9913 ajbasa@172.20.3.92"
CONTAINER = "app_gamit"

def clean_template(content):
    # 1. Rejoin split tags
    def rejoin(m):
        return m.group(1) + " " + m.group(2).strip().replace("\n", " ") + " " + m.group(3)
    
    # Rejoin {% ... %}
    content = re.sub(r'\{%(.*?)%\}', rejoin, content, flags=re.DOTALL)
    # Rejoin {{ ... }}
    content = re.sub(r'\{\{(.*?)\}\}', rejoin, content, flags=re.DOTALL)
    
    # 2. Fix comparison operators: var==val -> var == val
    # Only inside tags. But tagging them above already made them one line.
    # Pattern to find == with no spaces around it within {% ... %}
    def fix_ops(m):
        tag_content = m.group(1)
        # Fix ==
        tag_content = re.sub(r'([^\s!<>])==([^\s])', r'\1 == \2', tag_content)
        # Fix !=
        tag_content = re.sub(r'([^\s])!=([^\s])', r'\1 != \2', tag_content)
        return "{%" + tag_content + "%}"
    
    content = re.sub(r'\{%(.*?)%\}', fix_ops, content)
    
    # Eliminate double spaces introduced by rejoin
    content = re.sub(r'([\{%|\{\{])\s+', r'\1 ', content)
    content = re.sub(r'\s+([\%\}|\}\}])', r' \1', content)
    
    return content

for host_path, remote_path in TEMPLATES:
    print(f"Cleaning: {host_path}")
    with open(host_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    cleaned = clean_template(content)
    
    # Save back to host
    with open(host_path, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    
    # Hard-Write to container
    print(f"Hard-Writing to Staging: {remote_path}")
    remote_cmd = f"docker exec -i {CONTAINER} sh -c 'cat > {remote_path}'"
    full_cmd = f"{SSH_CMD} \"{remote_cmd}\""
    
    process = subprocess.Popen(full_cmd, stdin=subprocess.PIPE, shell=True)
    process.communicate(input=cleaned.encode('utf-8'))
    if process.returncode == 0:
        print(f"Successfully synced: {host_path}")

print("Restarting Container...")
subprocess.run(f"{SSH_CMD} 'docker restart {CONTAINER}'", shell=True)
print("Complete.")
