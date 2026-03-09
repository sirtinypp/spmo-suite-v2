import subprocess
import os

TEMPLATES = ["asset_list.html", "asset_detail.html", "asset_add.html"]
CONTAINER = "app_gamit"
INTERNAL_PATH = "/app/inventory/templates/inventory/"
LOCAL_PATH = "gamit_app/inventory/templates/inventory/"

# SSH parameters from credentials/logs
SSH_CMD = "ssh -o ConnectTimeout=5 -p 9913 ajbasa@172.20.3.92"

for t in TEMPLATES:
    host_full_path = os.path.join(LOCAL_PATH, t)
    print(f"Reading: {host_full_path}")
    with open(host_full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pipe content into the container via SSH
    remote_cmd = f"docker exec -i {CONTAINER} sh -c 'cat > {INTERNAL_PATH}{t}'"
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
