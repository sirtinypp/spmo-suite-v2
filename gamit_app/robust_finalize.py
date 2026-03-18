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
from workflow.models import Persona, Role, WorkflowStep

def create_dummy_signature(text="PROCESSED"):
    img = Image.new('RGBA', (200, 100), color=(255, 255, 255, 0))
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    d.text((10,10), text, fill=(0,0,0))
    buf = BytesIO()
    img.save(buf, format='PNG')
    return ContentFile(buf.getvalue(), name=f'sig_{text}.png')

def finalize_batch():
    try:
        batch = AssetBatch.objects.get(transaction_id='BATCH-TEST-004')
        print(f"Found batch: {batch.transaction_id}")
    except AssetBatch.DoesNotExist:
        print("Error: BATCH-TEST-004 not found.")
        return

    # Ensure we have the necessary roles and users
    roles_to_create = [
        ('INSPECTION_OFFICER', 'Inspection Officer'),
        ('SPMO_SUPERVISOR', 'SPMO Supervisor'),
        ('SPMO_CHIEF', 'SPMO Chief'),
        ('UNIT_AO', 'Unit Admin Officer'),
        ('SPMO_CLERK', 'SPMO Clerk')
    ]
    
    auth_user, _ = User.objects.get_or_create(username='grootadmin', is_staff=True)
    
    for code, name in roles_to_create:
        role, _ = Role.objects.get_or_create(code=code, defaults={'name': name})
        persona, _ = Persona.objects.get_or_create(user=auth_user, role=role)
        if not persona.signature_image:
            persona.signature_image = create_dummy_signature(code)
            persona.save()

    engine = WorkflowEngine()
    
    # Define steps order for Standard Asset Acquisition
    steps = WorkflowStep.objects.filter(phase__workflow__name='Standard Asset Acquisition').order_by('order')
    
    if not steps.exists():
        print("Error: Workflow steps for 'Standard Asset Acquisition' not found.")
        return

    print(f"Advancing batch through {steps.count()} steps...")
    
    for step in steps:
        if batch.current_step == step:
            continue
        try:
            print(f"Transitioning to: {step.label}")
            engine.transition(batch, step.id, user=auth_user, manual_signature=create_dummy_signature(step.label))
        except Exception as e:
            print(f"Step {step.label} error: {e}")
    
    # Finalize
    print("Executing final transition...")
    try:
        engine.transition(batch, 'FINALIZE', user=auth_user)
        print("Batch finalized successfully.")
    except Exception as e:
        print(f"Finalization error: {e}")

    batch.refresh_from_db()
    print(f"Status: {batch.status}")
    if batch.par_file:
        print(f"PAR: {batch.par_file.url}")

if __name__ == "__main__":
    finalize_batch()
