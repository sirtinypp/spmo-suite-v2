
import os
import django
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.base import ContentFile

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from django.contrib.auth.models import User
from inventory.models import AssetBatch, UserSignature, BatchItem
from workflow.models import Role, Persona, Workflow, WorkflowStep
from inventory.workflow import WorkflowEngine

def setup_test_environment():
    # Reuse setup from previous or just do minimal
    roles_to_get = ['UNIT_AO', 'UNIT_HEAD', 'SPMO_AO', 'INSPECTION_OFFICER', 'SPMO_SUPERVISOR', 'SPMO_CHIEF']
    roles = {code: Role.objects.get(code=code) for code in roles_to_get}

    def create_user_with_sig(username, role, pos):
        user, _ = User.objects.get_or_create(username=username, email=f"{username}@example.com")
        persona = Persona.objects.filter(user=user, role=role, is_active=True).first()
        if not persona:
            persona = Persona.objects.create(user=user, role=role, is_active=True)
        return user

    users = {
        'AO': create_user_with_sig('par_unit_ao', roles['UNIT_AO'], 'Unit Admin Officer'),
        'HEAD': create_user_with_sig('par_unit_head', roles['UNIT_HEAD'], 'Unit Head'),
        'SPMO_AO': create_user_with_sig('par_spmo_ao', roles['SPMO_AO'], 'SPMO Admin Officer'),
        'INSP': create_user_with_sig('par_inspector', roles['INSPECTION_OFFICER'], 'SPMO Inspector'),
        'SUPV': create_user_with_sig('par_supervisor', roles['SPMO_SUPERVISOR'], 'SPMO Supervisor'),
        'CHIEF': create_user_with_sig('par_chief', roles['SPMO_CHIEF'], 'SPMO Chief/Director')
    }
    return users

def run_ics_test():
    users = setup_test_environment()
    print("\n--- Starting Full ICS Flow Test (< 50k) ---")
    
    import uuid
    batch = AssetBatch.objects.create(
        transaction_id=f"ICS-{uuid.uuid4().hex[:8].upper()}",
        requestor=users['AO'],
        requesting_unit="Dept of Math",
        supplier_name="ICS Test Supplier",
        po_number="PO-ICS-TEST-123"
    )
    
    # Low Value item
    BatchItem.objects.create(
        batch=batch,
        description="Office Chair",
        quantity=1,
        amount=5000.00 # Below 50k
    )
    
    WorkflowEngine.initialize_transaction(batch, "BATCH_ACQUISITION")
    
    # Fast forward to FINALIZE
    steps = WorkflowStep.objects.filter(phase__workflow__process__code='BATCH_ACQUISITION').order_by('order')
    user_sequence = ['AO', 'HEAD', 'SPMO_AO', 'SPMO_AO', 'INSP', 'INSP', 'INSP', 'SUPV', 'SUPV', 'CHIEF', 'AO']

    for i, u_key in enumerate(user_sequence):
        target = str(steps[i+1].id) if i < len(steps)-1 else 'FINALIZE'
        WorkflowEngine.transition(batch, target, users[u_key])

    batch.refresh_from_db()
    print(f"✅ ICS Finalized: {batch.status}")
    if batch.par_file:
        print(f"✅ ICS File Generated: {batch.par_file.name}")
        # Note: ICSGenerator.finalize_ics currently might use a different name or same field
        if "ICS_" in batch.par_file.name:
            print("✅ Correct ICS Naming used.")
    else:
        print("❌ ICS File NOT Generated.")

if __name__ == "__main__":
    run_ics_test()
