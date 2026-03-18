
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
    print("--- Setting up Test Environment ---")
    
    # Roles
    roles_to_get = ['UNIT_AO', 'UNIT_HEAD', 'SPMO_AO', 'INSPECTION_OFFICER', 'SPMO_SUPERVISOR', 'SPMO_CHIEF']
    roles = {code: Role.objects.get(code=code) for code in roles_to_get}

    # Setup Users with real-ish signatures
    def create_user_with_sig(username, role, pos):
        user, _ = User.objects.get_or_create(username=username, email=f"{username}@example.com")
        user.set_password('password')
        user.save()
        
        persona, _ = Persona.objects.get_or_create(user=user, role=role, is_active=True)
        
        # Add signature to Persona if missing
        if not persona.signature_image:
            img_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
            sig_content = ContentFile(img_data, name=f"sig_{username}.png")
            persona.signature_image = sig_content
            persona.position_title = pos
            persona.save()
            
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

def run_par_test():
    users = setup_test_environment()
    print("\n--- Starting Full PAR Flow Test ---")
    
    # 1. Initialize Batch
    import uuid
    batch = AssetBatch.objects.create(
        transaction_id=f"BCH-{uuid.uuid4().hex[:8].upper()}",
        requestor=users['AO'],
        requesting_unit="College of Engineering",
        supplier_name="PAR Generator Test Inc.",
        po_number="PO-PAR-TEST-999",
        fund_cluster="101",
        ups_dv_number="DV-2026-0001"
    )
    
    # Add an item (Required for realization)
    BatchItem.objects.create(
        batch=batch,
        description="High-Speed Server Node",
        quantity=2,
        amount=75000.00, # Above 50k for PAR
        unit="unit",
        assigned_custodian="Engr. John Doe"
    )
    
    WorkflowEngine.initialize_transaction(batch, "BATCH_ACQUISITION")
    print(f"Batch {batch.transaction_id} Initialized.")

    # Get all steps in order
    steps = WorkflowStep.objects.filter(phase__workflow__process__code='BATCH_ACQUISITION').order_by('order')
    
    # We need to map step -> user
    # Step 1: Draft (AO) -> Move to 2
    # Step 2: For Unit Chief (HEAD) -> Move to 3
    # Step 3: Verify Completeness (SPMO_AO) -> Move to 4
    # Step 4: For SPMO AO Signature (SPMO_AO) -> Move to 5
    # Step 5: Initiate Inspection (INSP) -> Move to 6
    # Step 6: Release IAR (INSP) -> Move to 7
    # Step 7: For Inspection Signature (INSP) -> Move to 8
    # Step 8: Verify Completeness (Supv) (SUPV) -> Move to 9
    # Step 9: For Supervisor Signature (SUPV) -> Move to 10
    # Step 10: For Chief Final Approval (CHIEF) -> Move to 11
    # Step 11: Awaiting Unit Acceptance (AO) -> FINALIZE
    
    user_sequence = [
        ('AO', 'Draft'),
        ('HEAD', 'Endorsed'),
        ('SPMO_AO', 'Verified'),
        ('SPMO_AO', 'Signed'),
        ('INSP', 'Inspected'),
        ('INSP', 'IAR Released'),
        ('INSP', 'Inspector Signed'),
        ('SUPV', 'Verified By Supervisor'),
        ('SUPV', 'Supervisor Signed'),
        ('CHIEF', 'Chief Approved'),
        ('AO', 'Final Receipt')
    ]

    for i, (u_key, remark) in enumerate(user_sequence):
        # Determine target
        if i < len(steps) - 1:
            target = str(steps[i+1].id)
        else:
            target = 'FINALIZE'
            
        print(f"[{i+1}/12] {u_key} performing action: {remark} (Target: {target})")
        WorkflowEngine.transition(batch, target, users[u_key], remarks=remark)
        print(f"   -> Status: {batch.status}")

    # Final Verification
    print("\n--- Final Verification ---")
    batch.refresh_from_db()
    
    if batch.status == "PAR_RELEASED" or batch.current_step is None:
        print("✅ Status is FINALIZED / PAR_RELEASED")
    else:
        print(f"❌ Status is {batch.status}")

    if batch.par_file:
        print(f"✅ PAR File Generated: {batch.par_file.name}")
        print(f"   Size: {batch.par_file.size} bytes")
        # Check if size is large enough to contain the template (template is ~418KB)
        if batch.par_file.size > 400000:
            print("✅ SIZE CHECK: Template likely INCLUDED.")
        else:
            print("❌ SIZE CHECK: Template likely MISSING (too small).")
        print(f"✅ PAR Hash: {batch.par_hash}")
    else:
        print("❌ PAR File NOT Generated.")

    if batch.generated_assets.count() == 2:
        print(f"✅ Assets Realized: {batch.generated_assets.count()}")
    else:
        print(f"❌ Assets count mismatch: {batch.generated_assets.count()}")

    # Check Signature snapshots in logs
    logs_with_sigs = batch.movement_logs.exclude(signature_snapshot='').count()
    print(f"✅ Logs with Signature Snapshots: {logs_with_sigs}")

if __name__ == "__main__":
    try:
        run_par_test()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
