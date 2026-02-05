
import os

SETTINGS_FILES = [
    r"c:\Users\Aaron\spmo-suite - Copy\gamit_app\gamit_core\settings.py",
    r"c:\Users\Aaron\spmo-suite - Copy\gfa_app\config\settings.py",
    r"c:\Users\Aaron\spmo-suite - Copy\suplay_app\office_supplies_project\settings.py",
    r"c:\Users\Aaron\spmo-suite - Copy\spmo_website\config\settings.py"
]

LOCAL_SETTINGS_BLOCK = """
# --- LOCAL DEV OVERRIDES (Added by Agent) ---
DEBUG = True
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://localhost:8001', 'http://localhost:8002', 'http://localhost:8003', 'http://127.0.0.1:8000', 'http://127.0.0.1:8001', 'http://127.0.0.1:8002', 'http://127.0.0.1:8003']
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
# --------------------------------------------
"""

for file_path in SETTINGS_FILES:
    try:
        with open(file_path, "a") as f:
            f.write(LOCAL_SETTINGS_BLOCK)
        print(f"Patched {file_path}")
    except Exception as e:
        print(f"Error patching {file_path}: {e}")
