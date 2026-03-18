import os
import django
import sys
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from django.contrib.auth.models import User
from inventory.models import AssetBatch, BatchItem
from inventory.workflow import WorkflowEngine
from workflow.models import Workflow, WorkflowStep, Persona, Role

def create_dummy_signature():
    img = Image.new('RGBA', (200, 100), color=(255, 255, 255, 0))
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    d.text((10,10), "TEST SIGNATURE", fill=(0,0,0))
    buf = BytesIO()
    img.save(buf, format='PNG')
    return ContentFile(buf.getvalue(), name='test_sig.png')

def run_workflow_sim():
    batch = AssetBatch.objects.get(transaction_id='BATCH-TEST-004')
    engine = WorkflowEngine()
    
    def get_step_id(label):
        return WorkflowStep.objects.get(phase__workflow__name='Standard Acquisition', label=label).id

    # 1. ANTICIPATORY -> DELIVERY_VALIDATION
    engine.transition(batch, get_step_id('Delivery Validation'), user=batch.requestor)
    
    # 2. DELIVERY_VALIDATION -> FOR_INSPECTION
    engine.transition(batch, get_step_id('For Inspection'), user=batch.requestor)
    
    # 3. FOR_INSPECTION -> FOR_SUPERVISOR_APPROVAL
    # We need an Inspection Officer
    inspector_role, _ = Role.objects.get_or_create(code='INSPECTION_OFFICER')
    inspector_user, _ = User.objects.get_or_create(username='inspector_test')
    p_inspector, _ = Persona.objects.get_or_create(user=inspector_user, role=inspector_role)
    engine.active_persona = p_inspector
    engine.transition(batch, get_step_id('For Supervisor Approval'), user=inspector_user, manual_signature=create_dummy_signature())
    
    # 4. FOR_SUPERVISOR_APPROVAL -> FOR_CHIEF_PRE_APPROVAL
    supervisor_role, _ = Role.objects.get_or_create(code='SPMO_SUPERVISOR')
    supervisor_user, _ = User.objects.get_or_create(username='supervisor_test')
    p_supervisor, _ = Persona.objects.get_or_create(user=supervisor_user, role=supervisor_role)
    engine.active_persona = p_supervisor
    engine.transition(batch, get_step_id('For Chief Pre-Approval'), user=supervisor_user)
    
    # 5. FOR_CHIEF_PRE_APPROVAL -> FOR_AO_SIGNATURE
    chief_role, _ = Role.objects.get_or_create(code='SPMO_CHIEF')
    chief_user, _ = User.objects.get_or_create(username='chief_test')
    p_chief, _ = Persona.objects.get_or_create(user=chief_user, role=chief_role)
    # Give Persona a signature for "SSPMO team" logic
    if not p_chief.signature_image:
        p_chief.signature_image = create_dummy_signature()
        p_chief.save()
    engine.active_persona = p_chief
    engine.transition(batch, get_step_id('For AO Signature'), user=chief_user)
    
    # 6. FOR_AO_SIGNATURE -> FOR_CHIEF_FINAL_SIGNATURE
    ao_role, _ = Role.objects.get_or_create(code='UNIT_AO')
    ao_user, _ = User.objects.get_or_create(username='ao_test')
    p_ao, _ = Persona.objects.get_or_create(user=ao_user, role=ao_role)
    engine.active_persona = p_ao
    engine.transition(batch, get_step_id('For Chief Final Signature'), user=ao_user, manual_signature=create_dummy_signature())
    
    # 7. FOR_CHIEF_FINAL_SIGNATURE -> PAR_RELEASED
    # Chief signs again for final release
    engine.active_persona = p_chief
    engine.transition(batch, 'FINALIZE', user=chief_user)
    
    batch.refresh_from_db()
    print(f"Final State: {batch.status}")
    if batch.par_file:
        print(f"PAR Generated: {batch.par_file.url}")

if __name__ == "__main__":
    run_workflow_sim()
