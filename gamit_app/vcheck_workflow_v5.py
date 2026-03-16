
import os
import django
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from django.contrib.auth.models import User
from inventory.models import AssetBatch, UserSignature, BatchItem
from workflow.models import Role, Persona, Workflow, WorkflowStep
from inventory.workflow import WorkflowEngine
from inventory.services import PARGenerator

def setup_test_environment():
    print("--- Setting up Test Environment ---")
    
    # 1. Ensure Roles (already seeded, but let's grab them)
    role_ao = Role.objects.get(code='UNIT_AO')
    role_head = Role.objects.get(code='UNIT_HEAD')
    role_spmo_ao = Role.objects.get(code='SPMO_AO')
    role_insp = Role.objects.get(code='INSPECTION_OFFICER')
    role_supv = Role.objects.get(code='SPMO_SUPERVISOR')
    role_chief = Role.objects.get(code='SPMO_CHIEF')

    # 2. Setup Users with Signatures
    def create_user_with_sig(username, role, pos):
        user, _ = User.objects.get_or_create(username=username, email=f"{username}@example.com")
        user.set_password('password')
        user.save()
        
        # Persona
        Persona.objects.get_or_create(user=user, role=role, is_active=True)
        
        # Signature
        if not hasattr(user, 'signature'):
            img_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
            sig_file = SimpleUploadedFile(f"sig_{username}.png", img_data, content_type="image/png")
            UserSignature.objects.create(user=user, position_title=pos, signature_image=sig_file)
        return user

    users = {
        'AO': create_user_with_sig('v5_unit_ao', role_ao, 'Unit Admin Officer'),
        'HEAD': create_user_with_sig('v5_unit_head', role_head, 'Unit Head'),
        'SPMO_AO': create_user_with_sig('v5_spmo_ao', role_spmo_ao, 'SPMO Admin Officer'),
        'INSP': create_user_with_sig('v5_inspector', role_insp, 'SPMO Inspector'),
        'SUPV': create_user_with_sig('v5_supervisor', role_supv, 'SPMO Supervisor'),
        'CHIEF': create_user_with_sig('v5_chief', role_chief, 'SPMO Chief/Director')
    }
    
    return users

def run_v5_test():
    users = setup_test_environment()
    print("\n--- Starting Official 12-Step Flow Test ---")
    
    # A. Initializing Batch
    batch = AssetBatch.objects.create(
        requestor=users['AO'],
        requesting_unit="College of Science",
        supplier_name="V5 Tech Solutions",
        po_number="PO-V5-001",
        doc_1_file=SimpleUploadedFile("po.pdf", b"dummy pdf content", content_type="application/pdf")
    )
    
    # Initialize to Step 1
    WorkflowEngine.initialize_transaction(batch, "BATCH_ACQUISITION")
    print(f"Batch {batch.transaction_id} initialized to: {batch.status}")

    # Helper to transition
    def move(user_key, action_desc):
        user = users[user_key]
        transitions = WorkflowEngine.get_allowed_transitions(batch, user)
        if not transitions:
            raise Exception(f"No allowed transitions for {user.username} at {batch.status}")
        
        target = transitions[0]['target'] # Always take the next sequential step
        WorkflowEngine.transition(batch, target, user, remarks=f"Test: {action_desc}")
        print(f"-> Moved to: {batch.status} (Action by {user.username})")

    # B. Execution of 11 sequential steps
    move('AO', "Submit for Endorsement")             # 1 -> 2
    move('HEAD', "Endorsed by Unit Head")           # 2 -> 3
    move('SPMO_AO', "Verified Completeness")        # 3 -> 4
    move('SPMO_AO', "Signed for SPMO")              # 4 -> 5
    move('INSP', "Inspection Initiated")            # 5 -> 6
    move('INSP', "IAR Released")                    # 6 -> 7
    move('INSP', "Inspector Signed")                # 7 -> 8
    move('SUPV', "Supervisor Verified")             # 8 -> 9
    move('SUPV', "Supervisor Signed")               # 9 -> 10
    move('CHIEF', "Chief Approved")                 # 10 -> 11
    move('AO', "Unit Received Asset")               # 11 -> FINALIZE

    # C. Finalize logic check
    print("\n--- Finalizing and Verifying PDF ---")
    from inventory.services import PARGenerator
    PARGenerator.finalize_par(batch) # This normally happens in transition for FINALIZE, but let's be explicit for test
    
    print(f"Final Status: {batch.status}")
    print(f"PAR File: {batch.par_file.name}")
    print(f"PAR Hash: {batch.par_hash}")
    
    # Check Movement Logs
    log_count = batch.movement_logs.count()
    print(f"Movement Logs Captured: {log_count}")
    
    # Check for Signature Snapshots
    logs_with_sigs = batch.movement_logs.exclude(signature_snapshot='').count()
    print(f"Logs with Signature Snapshots: {logs_with_sigs}")

    if logs_with_sigs > 0 and batch.par_hash:
        print("\n✅ PHASE 5 VERIFICATION PASSED")
    else:
        print("\n❌ PHASE 5 VERIFICATION FAILED: Missing signatures or hash.")

if __name__ == "__main__":
    try:
        run_v5_test()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
