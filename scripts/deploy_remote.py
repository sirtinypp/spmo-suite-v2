import os
import sys
import subprocess
import time
from pathlib import Path

# CONFIGURATION
REMOTE_USER = "ajbasa"
REMOTE_HOST = "172.20.3.91"
REMOTE_PORT = "9913"
# Based on check: /home/ajbasa/spmo_suite
REMOTE_BASE_DIR = "/home/ajbasa/spmo_suite" 

def sync_file(local_path):
    """
    Syncs a single file to the remote server relative to the project root.
    """
    # 1. Resolve absolute path
    abs_path = Path(local_path).resolve()
    
    # 2. Determine relative path from project root (c:\Users\Aaron\spmo-suite - Copy)
    project_root = Path(os.getcwd()).resolve()
    
    try:
        relative_path = abs_path.relative_to(project_root)
    except ValueError:
        print(f"Error: File {local_path} is not inside the project root.")
        return False

    # 3. Construct Remote Path
    # Convert windows path separators to linux
    remote_path = f"{REMOTE_BASE_DIR}/{relative_path.as_posix()}"

    # 4. Construct SCP command
    # Using -P for port, -o BatchMode=yes to fail fast if auth fails
    cmd = [
        "scp", 
        "-P", REMOTE_PORT,
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=no", # Optional: convenience
        str(abs_path),
        f"{REMOTE_USER}@{REMOTE_HOST}:{remote_path}"
    ]

    print(f"Syncing: {relative_path} -> {REMOTE_HOST}:{remote_path} ...", end="", flush=True)
    
    try:
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f" DONE ({duration:.2f}s)")
            return True
        else:
            print(" FAILED")
            print(f"STDERR: {result.stderr}")
            return False
    except Exception as e:
        print(f" ERROR: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deploy_remote.py <local_file_path>")
        sys.exit(1)

    success = True
    for target_file in sys.argv[1:]:
        if not os.path.exists(target_file):
            print(f"Error: File not found: {target_file}")
            success = False
            continue
            
        if not sync_file(target_file):
            success = False
            
    if not success:
        sys.exit(1)
