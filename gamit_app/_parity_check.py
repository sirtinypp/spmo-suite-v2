import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()
from workflow.models import ActionProcess, Workflow, WorkflowPhase, WorkflowStep, SignatorySlot, Role

print('=== CANONICAL 5 PROCESS AUDIT ===\n')
codes = ['BATCH_ACQUISITION', 'ASSET_TRANSFER', 'ASSET_INSPECT', 'ASSET_LOSS', 'ASSET_CLEARANCE']

for code in codes:
    ap = ActionProcess.objects.filter(code=code).first()
    if not ap:
        print(f'[{code}] MISSING')
        continue
    
    print(f'[{ap.code}] {ap.name}')
    wf = Workflow.objects.filter(process=ap).first()
    if wf:
        phases = WorkflowPhase.objects.filter(workflow=wf).count()
        steps = WorkflowStep.objects.filter(phase__workflow=wf).count()
        slots = SignatorySlot.objects.filter(step__phase__workflow=wf).count()
        print(f'  Phases: {phases} | Steps: {steps} | Signatory Slots: {slots}')
    print()

print('=== ROLES ===')
print(f'Total Roles: {Role.objects.count()}')
for r in Role.objects.all().order_by('code'):
    print(f'  {r.code}')
