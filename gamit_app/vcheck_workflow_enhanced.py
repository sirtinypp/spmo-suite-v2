
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

def setup_test_environment():
    print("--- Setting up Test Environment ---")
    
    # Grab Roles
    role_ao = Role.objects.get(code='UNIT_AO')
    role_head = Role.objects.get(code='UNIT_HEAD')
    role_spmo_ao = Role.objects.get(code='SPMO_AO')
    role_insp = Role.objects.get(code='INSPECTION_OFFICER')
    role_supv = Role.objects.get(code='SPMO_SUPERVISOR')
    role_chief = Role.objects.get(code='SPMO_CHIEF')

    # Setup Users
    def create_user_with_sig(username, role, pos):
        user, _ = User.objects.get_or_create(username=username, email=f"{username}@example.com")
        user.set_password('password')
        user.save()
        Persona.objects.get_or_create(user=user, role=role, is_active=True)
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

def run_enhanced_test():
    users = setup_test_environment()
    print("\n--- Starting Enhanced Workflow Test (Return/Reject/Remarks) ---")
    
    # 1. Initialize Batch
    batch = AssetBatch.objects.create(
        requestor=users['AO'],
        requesting_unit="Dept of Science",
        supplier_name="Enhanced Tech",
        po_number="PO-ENH-001"
    )
    WorkflowEngine.initialize_transaction(batch, "BATCH_ACQUISITION")
    print(f"Batch {batch.transaction_id} Step 1: {batch.status}")

    # Helper to transition
    def move(user_key, target, remarks=""):
        user = users[user_key]
        WorkflowEngine.transition(batch, target, user, remarks=remarks)
        print(f"-> {user.username} moved to {batch.status} | Remarks: {remarks}")

    # SCENARIO A: Normal Advance
    # Step 1 -> 2
    step2_id = WorkflowStep.objects.get(phase__workflow__process__code='BATCH_ACQUISITION', order=20).id
    move('AO', step2_id, "Submitting for endorsement")

    # Step 2 -> 3
    step3_id = WorkflowStep.objects.get(phase__workflow__process__code='BATCH_ACQUISITION', order=30).id
    move('HEAD', step3_id, "Endorsed. Please proceed.")

    # SCENARIO B: Return (Step 3 -> 2)
    print("\n--- Testing RETURN Logic ---")
    move('SPMO_AO', step2_id, "Incorrect PO number format. Please check.")
    
    if batch.status == "For Unit Chief Approval":
        print("✅ RETURN Success: Status correctly reverted.")
    else:
        print(f"❌ RETURN Failed: Status is {batch.status}")

    # Endorse again
    move('HEAD', step3_id, "PO fixed. Endorsing again.")

    # SCENARIO C: Multiple Advances
    move('SPMO_AO', WorkflowStep.objects.get(phase__workflow__process__code='BATCH_ACQUISITION', order=40).id, "Verified completeness.")

    # SCENARIO D: Reject (Step 4 -> Terminal)
    print("\n--- Testing REJECT Logic ---")
    move('SPMO_AO', 'REJECT', "Invalid supplier documentation. Rejecting batch.")

    if batch.status == "REJECTED":
        print("✅ REJECT Success: Status is REJECTED.")
    else:
        print(f"❌ REJECT Failed: Status is {batch.status}")

    # Verify Logs
    logs = batch.movement_logs.all().order_by('timestamp')
    print("\n--- Audit Trail Verification ---")
    for log in logs:
        print(f"[{log.timestamp.strftime('%H:%M:%S')}] {log.role_name} ({log.user.username}): {log.action_taken} | Remarks: {log.remarks}")

    # Final Check: Remarks presence
    if logs.filter(remarks="Incorrect PO number format. Please check.").exists():
        print("\n✅ REMARKS Success: Feedback captured in audit trail.")
    else:
        print("\n❌ REMARKS Failed: Missing feedback in logs.")

if __name__ == "__main__":
    try:
        run_enhanced_test()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
