import os
import django
import random
from django.utils import timezone
from django.contrib.auth.models import User
from inventory.models import (
    Asset, AssetBatch, InspectionRequest, AssetTransferRequest, 
    AssetReturnRequest, AssetLossReport, PropertyClearanceRequest
)
from workflow.models import Workflow, WorkflowStep, WorkflowMovementLog, Persona
from inventory.workflow import WorkflowEngine

def inject():
    print("--- STARTING SURGICAL DATA INJECTION ---")
    
    # 1. Setup Initiator
    initiator = User.objects.get(username='dev_unit_ao')
    persona = Persona.objects.filter(user=initiator, role__code='UNIT_AO').first()
    
    # 2. Setup Asset Pool
    asset_pool = list(Asset.objects.filter(status='SERVICEABLE')[:10])
    if not asset_pool:
        print("ERROR: No serviceable assets found for injection.")
        return

    processes = [
        ('INSPECTION', InspectionRequest, 'ASSET_INSPECT'),
        ('TRANSFER', AssetTransferRequest, 'TRANSFER'),
        ('RETURN', AssetReturnRequest, 'RETURN'),
        ('LOSS', AssetLossReport, 'LOSS_REPORT'),
        ('CLEARANCE', PropertyClearanceRequest, 'CLEARANCE'),
    ]

    for label, model, flow_code in processes:
        print(f"Processing {label}...")
        
        for i in range(5):
            is_completed = (i < 3)
            prefix = "SURG-PR-C" if is_completed else "SURG-PR-P"
            t_id = f"{prefix}-{label[:3]}-{random.randint(1000, 9999)}"
            
            # Create instance
            obj = model(requestor=initiator)
            
            # Field specific logic
            if model == InspectionRequest:
                obj.asset = random.choice(asset_pool)
                obj.notes = "Routine maintenance inspection for presentation validation."
            elif model == AssetTransferRequest:
                obj.asset = random.choice(asset_pool)
                obj.current_officer = obj.asset.assigned_custodian or "System Custodian"
                obj.new_officer_firstname = "Demo"
                obj.new_officer_surname = "Recipient"
                obj.remarks = "Inter-departmental transfer for project expansion."
            elif model == AssetReturnRequest:
                obj.asset = random.choice(asset_pool)
                obj.reason = "End of project lifecycle return."
            elif model == AssetLossReport:
                obj.asset = random.choice(asset_pool)
                obj.description = "Accidental damage during site transfer."
                obj.incident_date = timezone.now().date()
            elif model == PropertyClearanceRequest:
                obj.purpose = "Transfer to another CU (Administrative)"

            # Save with manual ID to avoid sequence conflicts during test
            obj.transaction_id = t_id
            obj.save()

            if is_completed:
                # Force Finalized State
                obj.status = 'Approved' if label in ['INSPECTION', 'TRANSFER'] else 'FINALIZED'
                obj.current_step = None
                obj.save()
                
                # Add a legacy log entry
                WorkflowMovementLog.objects.create(
                    user=initiator,
                    persona=persona,
                    role_name="Unit AO",
                    unit_name=persona.department.name if persona and persona.department else "Unit Office",
                    status_label=obj.status,
                    action_taken=f"Finalized {label}",
                    remarks="Automatic historical migration for system audit.",
                    timestamp=timezone.now() - timezone.timedelta(days=2),
                    **{model.__name__.lower() if 'request' not in model.__name__.lower() else model.__name__.lower().replace('request', '_request'): obj}
                )
            else:
                # Initialize active workflow
                WorkflowEngine.initialize_transaction(obj, flow_code)
                print(f"  - Initialized Pending {label}: {obj.transaction_id}")

    print("--- INJECTION COMPLETE ---")

if __name__ == "__main__":
    inject()
