import os
import django
import sys

# Setup Django Environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from django.contrib.auth.models import User
from inventory.models import AssetBatch, BatchItem, Asset, Department
from workflow.models import Workflow, WorkflowStep, Persona, Role
from inventory.workflow import WorkflowEngine

def simulate_realization():
    print("=== Phase 7 Simulation: Asset Realization (SOP) ===")
    
    # 1. Setup Data
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        print("❌ Error: No superuser found for simulation.")
        return

    # 2. Create a Mock Batch
    batch = AssetBatch.objects.create(
        requestor=user,
        requesting_unit="SPMO Simulation Unit",
        supplier_name="Global Tech Solutions",
        po_number="PO-2026-TEST",
        status='ANTICIPATORY'
    )
    print(f"Created Batch: {batch.transaction_id}")

    # 3. Add Multiple Items (Total 5 Assets)
    item1 = BatchItem.objects.create(
        batch=batch,
        description="Dell Latitude 5440 Laptop",
        quantity=3,
        amount=65000.00
    )
    item2 = BatchItem.objects.create(
        batch=batch,
        description="Logitech MX Master 3S Mouse",
        quantity=2,
        amount=5500.00
    )
    print(f"Added items: 3x Laptop, 2x Mouse (Expected: 5 Assets)")

    # 4. Initialize Workflow (Set to First Step)
    WorkflowEngine.initialize_transaction(batch, 'BATCH_ACQUISITION')
    if not batch.current_step:
        print("❌ Error: Workflow initialization failed (Check if BATCH_ACQUISITION is seeded).")
        return
    print(f"Workflow initialized. Current Step: {batch.current_step.label}")

    # 5. Drive Workflow to Finalization
    # Official Seeded Labels from seed_workflows_v5.py
    steps_to_run = [
        "For Unit Chief Approval",
        "Verify Completeness (SPMO)",
        "For SPMO AO Signature",
        "Initiate Inspection",
        "Release / Save IAR",
        "For Inspection Signature",
        "Verify Completeness (Supv)",
        "For Supervisor Signature",
        "For Chief Final Approval",
        "Awaiting Unit Acceptance",
        "FINALIZE"
    ]

    for step_label in steps_to_run:
        # Get target ID
        if step_label == 'FINALIZE':
            target = 'FINALIZE'
        else:
            try:
                step_obj = WorkflowStep.objects.get(phase__workflow__process__code='BATCH_ACQUISITION', label=step_label)
                target = str(step_obj.id)
            except WorkflowStep.DoesNotExist:
                print(f"❌ Error: Step '{step_label}' not found in database.")
                return
        
        print(f"Transitioning to: {step_label}...")
        WorkflowEngine.transition(batch, target, user)

    # 6. VERIFICATION
    print("\n--- FINAL VERIFICATION ---")
    generated_assets = batch.generated_assets.all()
    count = generated_assets.count()
    
    if count == 5:
        print(f"✅ Success: {count} assets generated for Batch {batch.transaction_id}")
        for asset in generated_assets:
            print(f"   - Prop #: {asset.property_number} | Item: {asset.name} | Batch Link: {asset.acquisition_batch.transaction_id}")
    else:
        print(f"❌ Failure: Expected 5 assets, found {count}")

    # 7. Cleanup (Optional: keep for manual UI check)
    print("\nSimulation complete. You can now view this in the UI at:")
    print(f"Activity Log: /administration/activity-log/")
    print(f"Batch Detail: /transaction/batch/{batch.id}/")

if __name__ == "__main__":
    simulate_realization()
