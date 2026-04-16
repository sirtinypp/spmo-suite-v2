import os

path = r'c:\Users\Aaron\spmo-suite - Copy\gfa_app\travel\views.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = 0
for i, line in enumerate(lines):
    if skip > 0:
        skip -= 1
        continue
    
    # Update Stats
    if 'pending_reqs = all_transactions.filter(status=\'PENDING\').count()' in line:
        new_lines.append(line)
        new_lines.append("    # Multi-Role Pending Stats (Phase 11)\n")
        new_lines.append("    pending_admin = all_transactions.filter(status='FOR_ADMIN').count()\n")
        new_lines.append("    pending_supervisor = all_transactions.filter(status='FOR_SUPERVISOR').count()\n")
        new_lines.append("    pending_chief = all_transactions.filter(status='FOR_CHIEF').count()\n")
    
    # Update context
    elif "'settled_count': settled_count," in line:
        new_lines.append(line)
        new_lines.append("        'pending_admin': pending_admin,\n")
        new_lines.append("        'pending_supervisor': pending_supervisor,\n")
        new_lines.append("        'pending_chief': pending_chief,\n")
    
    else:
        new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("SUCCESS")
