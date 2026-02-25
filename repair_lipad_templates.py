import re
import os

# Comprehensive Repair and UI Upgrade Script for LIPAD Templates

TEMPLATES_DIR = "/app/travel/templates/travel/"
FILES_TO_FIX = [
    "form.html",
    "admin_attach.html",
    "booking_summary.html",
    "index.html",
    "base.html",
    "dashboard.html",
    "user_transactions.html",
    "requisition_slip.html"
]

def clean_and_upgrade(path):
    if not os.path.exists(path):
        return

    print(f"Repairing & Upgrading {path}...")
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # 1. REJOIN SPLIT TAGS
    content = re.sub(r'\{\{\s*\r?\n\s*', '{{ ', content)
    content = re.sub(r'\{\{\s*form\.', '{{ form.', content)
    content = re.sub(r'\s*\r?\n\s*\}\}', ' }}', content)
    content = re.sub(r'\{%\s*\r?\n\s*', '{% ', content)
    content = re.sub(r'\s*\r?\n\s*%\}', ' %}', content)

    # 2. REPLACE MANGLED "BACK TO HOME" WITH HOME ICON
    # Targeting the specific pattern found in the header
    home_icon_link = """<a href="{% url 'index' %}" title="Back to Home" class="p-2 rounded-lg bg-slate-50 text-slate-500 hover:bg-blue-50 hover:text-blue-700 transition border border-slate-200 shadow-sm flex items-center justify-center"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg></a>"""
    
    # regex to find the old link (handling mangling and potential spaces)
    mangled_pattern = r'<a href="{% url \'index\' %}"[^>]*>.*?Back to Home.*?</a>'
    content = re.sub(mangled_pattern, home_icon_link, content, flags=re.DOTALL | re.IGNORECASE)

    # 3. REPLACE "BACK TO DASHBOARD" WITH DASHBOARD ICON
    dash_icon_link = """<a href="{% url 'gfa_dashboard' %}" title="Back to Dashboard" class="p-2 rounded-lg bg-slate-50/50 text-slate-600 hover:bg-[#7b1113]/10 hover:text-[#7b1113] transition border border-slate-200 shadow-sm flex items-center justify-center no-print"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path></svg></a>"""
    
    dash_pattern = r'<a href="{% url \'gfa_dashboard\' %}"[^>]*>.*?Back to Dashboard.*?</a>'
    content = re.sub(dash_pattern, dash_icon_link, content, flags=re.DOTALL | re.IGNORECASE)

    # 4. Final cleanup
    if content.startswith('\ufeff'): content = content[1:]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Upgraded {path}")

if __name__ == "__main__":
    for f in FILES_TO_FIX:
        clean_upgrade(TEMPLATES_DIR + f)
