import subprocess
import os

TEMPLATES = [
    "inventory/templates/inventory/asset_list.html",
    "inventory/templates/inventory/asset_detail.html",
    "inventory/templates/inventory/asset_add.html",
    "inventory/templates/inventory/dashboard.html",
    "inventory/templatetags/inventory_tags.py",
    "inventory/templatetags/__init__.py",
    "inventory/admin.py",
    "inventory/resources.py",
    "inventory/forms.py",
    "inventory/views.py",
    "inventory/models.py",
    "inventory/migrations/0025_alter_asset_asset_class_alter_asset_asset_nature.py",
    "inventory/migrations/0026_remove_asset_assigned_office_and_more.py",
    "inventory/migrations/0027_alter_asset_asset_class_alter_asset_asset_nature.py"
]
CONTAINER = "app_gamit"
SSH_CMD = "ssh -o ConnectTimeout=5 -p 9913 ajbasa@172.20.3.92"

for t in TEMPLATES:
    host_full_path = os.path.join("gamit_app", t)
    print(f"Reading: {host_full_path}")
    if not os.path.exists(host_full_path):
        print(f"Skipping missing file: {host_full_path}")
        continue

    with open(host_full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ensure directory exists in container
    remote_dir = os.path.dirname(f"/app/{t}")
    subprocess.run(f"{SSH_CMD} \"docker exec -i {CONTAINER} mkdir -p {remote_dir}\"", shell=True)

    # Pipe content into the container via SSH
    remote_cmd = f"docker exec -i {CONTAINER} sh -c 'cat > /app/{t}'"
    full_cmd = f"{SSH_CMD} \"{remote_cmd}\""
    
    print(f"Syncing {t} to container...")
    process = subprocess.Popen(full_cmd, stdin=subprocess.PIPE, shell=True)
    process.communicate(input=content.encode('utf-8'))
    
    if process.returncode == 0:
        print(f"Successfully Hard-Synced: {t}")
    else:
        print(f"Failed to Hard-Sync: {t}")

# Restart container to clear cache
print("Restarting container...")
subprocess.run(f"{SSH_CMD} 'docker restart {CONTAINER}'", shell=True)
