import os
import django
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from django.contrib.auth.models import User, Group
from inventory.models import AssetBatch, UserSignature, ApprovalLog
from inventory.workflow import WorkflowEngine

# 1. Setup Test Users & Roles
def setup_users():
    print("--- Setting up Users & Roles ---")
    roles = ['USER_AO', 'SPMO_ADMIN', 'INSPECTOR', 'SUPERVISOR', 'CHIEF']
    users = {}
    
    for role in roles:
        group, _ = Group.objects.get_or_create(name=role)
        username = f"test_{role.lower()}"
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password('password')
            user.save()
        user.groups.add(group)
        
        # Create Signature
        if not hasattr(user, 'signature'):
            # Create a dummy image
            img_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
            sig_file = SimpleUploadedFile("sig.png", img_data, content_type="image/png")
            UserSignature.objects.create(user=user, position_title=f"{role} Officer", signature_image=sig_file)
        
        users[role] = user
        print(f"User {username} ready with role {role}")
        
    return users

# 2. Test Workflow
def test_workflow():
    users = setup_users()
    
    print("\n--- Starting Workflow Test ---")
    
    # A. Create Batch
    user_ao = users['USER_AO']
    batch = AssetBatch.objects.create(
        requestor=user_ao,
        status=WorkflowEngine.ANTICIPATORY,
        supplier_name="Test Supplier",
        po_number="PO-12345",
        doc_1_file=SimpleUploadedFile("po.pdf", b"dummy pdf", content_type="application/pdf")
    )
    print(f"Batch {batch.transaction_id} created in state: {batch.status}")

    # B. Transition 1: Submit -> Awaiting Delivery
    # Role: USER_AO
    print("\n[Step 1] ANTICIPATORY -> AWAITING_DELIVERY")
    WorkflowEngine.transition(batch, WorkflowEngine.AWAITING_DELIVERY, user_ao)
    print(f"Success. Current State: {batch.status}")
    
    # C. Transition 2: Awaiting -> Delivery Validation
    # Role: SPMO_ADMIN
    print("\n[Step 2] AWAITING_DELIVERY -> DELIVERY_VALIDATION")
    WorkflowEngine.transition(batch, WorkflowEngine.DELIVERY_VALIDATION, users['SPMO_ADMIN'])
    print(f"Success. Current State: {batch.status}")

    # D. Transition 3: Validation -> For Inspection
    # Role: SPMO_ADMIN, requires doc_2
    print("\n[Step 3] DELIVERY_VALIDATION -> FOR_INSPECTION")
    batch.doc_2_file = SimpleUploadedFile("dr.pdf", b"dummy pdf", content_type="application/pdf")
    batch.save()
    WorkflowEngine.transition(batch, WorkflowEngine.FOR_INSPECTION, users['SPMO_ADMIN'])
    print(f"Success. Current State: {batch.status}")

    # E. Transition 4: For Inspection -> Supervisor
    # Role: INSPECTOR
    print("\n[Step 4] FOR_INSPECTION -> FOR_SUPERVISOR_APPROVAL")
    WorkflowEngine.transition(batch, WorkflowEngine.FOR_SUPERVISOR_APPROVAL, users['INSPECTOR'])
    print(f"Success. Current State: {batch.status}")

    # F. Transition 5: Supervisor -> Chief Pre-Approval
    # Role: SUPERVISOR
    print("\n[Step 5] FOR_SUPERVISOR_APPROVAL -> FOR_CHIEF_PRE_APPROVAL")
    WorkflowEngine.transition(batch, WorkflowEngine.FOR_CHIEF_PRE_APPROVAL, users['SUPERVISOR'])
    print(f"Success. Current State: {batch.status}")

    # G. Transition 6: Chief Pre -> AO Signature (Trigger Draft)
    # Role: CHIEF
    print("\n[Step 6] FOR_CHIEF_PRE_APPROVAL -> FOR_AO_SIGNATURE")
    WorkflowEngine.transition(batch, WorkflowEngine.FOR_AO_SIGNATURE, users['CHIEF'])
    print(f"Success. Current State: {batch.status}")
    
    # Trigger Draft Gen (Simulate View)
    from inventory.services import PARGenerator
    PARGenerator.generate_draft(batch)
    print("Draft PDF Generated.")

    # H. Transition 7: AO Sign -> Chief Final
    # Role: USER_AO
    print("\n[Step 7] FOR_AO_SIGNATURE -> FOR_CHIEF_FINAL_SIGNATURE")
    WorkflowEngine.transition(batch, WorkflowEngine.FOR_CHIEF_FINAL_SIGNATURE, users['USER_AO'])
    print(f"Success. Current State: {batch.status}")

    # I. Transition 8: Chief Final -> RELEASED
    # Role: CHIEF
    print("\n[Step 8] FOR_CHIEF_FINAL_SIGNATURE -> PAR_RELEASED")
    WorkflowEngine.transition(batch, WorkflowEngine.PAR_RELEASED, users['CHIEF'])
    # Trigger Finalize (Simulate View)
    PARGenerator.finalize_par(batch)
    print(f"Success. Final State: {batch.status}")
    print(f"PAR Hash: {batch.par_hash}")
    print(f"PAR File: {batch.par_file.name}")
    
    # Verify Hash logic
    if not batch.par_hash:
        raise Exception("PAR Hash missing!")

if __name__ == '__main__':
    try:
        test_workflow()
        print("\n✅ WORKFLOW VERIFICATION PASSED")
    except Exception as e:
        print(f"\n❌ WORKFLOW VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
