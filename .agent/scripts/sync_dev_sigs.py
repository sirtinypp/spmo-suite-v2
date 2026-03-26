import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from workflow.models import Persona, WorkflowMovementLog

# Mapping of dev usernames to their real signature filenames
sig_map = {
    'dev_unit_ao': 'sig_aaron-removebg-preview.png',
    'dev_unit_head': 'sig_aaron-removebg-preview.png', # Placeholder
    'dev_spmo_ao': 'sig_eldefonso-removebg-preview.png',
    'dev_spmo_sup': 'sig_julius-removebg-preview.png',
    'dev_spmo_insp': 'sig_mark-removebg-preview.png',
    'dev_spmo_chief': 'sig_isagani-removebg-preview.png'
}

print("🔗 Linking True Signatures on Dev Server...")

updated_count = 0
for username, sig_filename in sig_map.items():
    p = Persona.objects.filter(user__username=username).first()
    if p:
        # Attach the media path
        path = f'signatures/personas/{sig_filename}'
        p.signature_image = path
        p.save()
        
        # Retroactively lock the snapshots in the audit logs
        logs_updated = WorkflowMovementLog.objects.filter(persona=p).update(signature_snapshot=path)
        print(f"✅ {username} -> {sig_filename} (Updated {logs_updated} logs)")
        updated_count += 1

print(f"🎉 Successfully linked {updated_count} real signatures!")
