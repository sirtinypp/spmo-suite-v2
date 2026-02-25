import subprocess
import os
import sys

def sync_file(container, host_path, container_path):
    if not os.path.exists(host_path):
        print(f"Skipping: Host file {host_path} not found")
        return

    with open(host_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"Hard-Syncing {host_path} -> {container}:{container_path}...")
    try:
        process = subprocess.Popen(
            ["docker", "exec", "-i", container, "sh", "-c", f"cat > {container_path}"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        stdout, stderr = process.communicate(input=content)

        if process.returncode == 0:
            print(f"Successfully synced to {container}")
        else:
            print(f"Error syncing: {stderr}")
    except Exception as e:
        print(f"Exception during sync: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 4:
        # Manual mode: python sync_hard.py <container> <host_path> <container_path>
        sync_file(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        # Default mode: LIPAD (previously hardcoded)
        LIPAD_TEMPLATES = [
            "form.html", "admin_attach.html", "booking_summary.html", 
            "dashboard.html", "user_transactions.html", "index.html", 
            "base.html", "requisition_slip.html"
        ]
        HOST_DIR = "gfa_app/travel/templates/travel/"
        CONTAINER_DIR = "/app/travel/templates/travel/"
        for t in LIPAD_TEMPLATES:
            sync_file("app_gfa", os.path.join(HOST_DIR, t), os.path.join(CONTAINER_DIR, t))

        # SUPLAY Repaired templates
        sync_file("app_store", "suplay_app/supplies/templates/supplies/home.html", "/app/supplies/templates/supplies/home.html")
