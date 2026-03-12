
import os
import django
import datetime
from django.utils.crypto import get_random_string

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from django.contrib.auth.models import User
from workflow.models import Role, Persona, ActionProcess, Workflow, WorkflowPhase, WorkflowStep
from inventory.models import Asset, Department, InspectionRequest, AssetBatch, BatchItem, AssetTransferRequest, AssetReturnRequest, AssetLossReport, PropertyClearanceRequest

def seed_demo():
    print("Starting Demo Seeding...")
    
    # 1. Ensure Roles (simplified list for speed)
    roles_to_create = [
        ('Inspector', 'INSPECTOR'),
        ('Admin Officer (SPMO)', 'SPMO_AO'),
        ('Head of Unit', 'HEAD_OF_UNIT'),
        ('Inventory Custodian', 'CUSTODIAN')
    ]
    role_objs = {}
    for name, code in roles_to_create:
        obj, _ = Role.objects.get_or_create(code=code, defaults={'name': name})
        role_objs[code] = obj

    # 2. Ensure Departments
    dept_cs, _ = Department.objects.get_or_create(name='College of Science')
    dept_eng, _ = Department.objects.get_or_create(name='College of Engineering')

    # 3. Get or Create Admin User
    admin_user = User.objects.get(username='grootadmin')
    
    # 4. Create Personas for Admin (so they can see everything)
    for code, role in role_objs.items():
        Persona.objects.get_or_create(user=admin_user, role=role, is_active=True)

    # 5. Helper to Build Workflow
    def build_workflow(proc_name, proc_code, wf_name, steps):
        proc, _ = ActionProcess.objects.get_or_create(code=proc_code, defaults={'name': proc_name})
        wf, created = Workflow.objects.get_or_create(process=proc, name=wf_name)
        if created:
            phase, _ = WorkflowPhase.objects.get_or_create(workflow=wf, name="Processing", order=10)
            for i, (label, role_code) in enumerate(steps):
                WorkflowStep.objects.create(
                    phase=phase,
                    label=label,
                    order=(i+1)*10,
                    required_persona_role=role_objs.get(role_code)
                )
        return wf

    # --- Create Workflows ---
    wf_inspect = build_workflow("Asset Inspection", "ASSET_INSPECT", "Standard Inspection", [
        ("Pending Inspection", "INSPECTOR"),
        ("Final Validation", "SPMO_AO")
    ])
    
    wf_transfer = build_workflow("Asset Transfer", "ASSET_TRANSFER", "Standard Transfer", [
        ("Awaiting SPMO Approval", "SPMO_AO")
    ])
    
    wf_return = build_workflow("Asset Return", "ASSET_RETURN", "Standard Return", [
        ("Unit Head Approval", "HEAD_OF_UNIT"),
        ("SPMO Receiving", "SPMO_AO")
    ])
    
    wf_loss = build_workflow("Asset Loss", "ASSET_LOSS", "Standard Loss Report", [
        ("Investigation Phase", "HEAD_OF_UNIT"),
        ("Final Adjustment", "SPMO_AO")
    ])
    
    wf_clearance = build_workflow("Property Clearance", "ASSET_CLEARANCE", "Personnel Clearance", [
        ("Unit Head Clearance", "HEAD_OF_UNIT"),
        ("SPMO Final Clearance", "SPMO_AO")
    ])

    # --- Create Samples ---
    
    # Assets
    a1, _ = Asset.objects.get_or_create(
        property_number='PN-2026-001',
        defaults={
            'name': 'MacBook Pro 16" (M3)', 
            'date_acquired': datetime.date(2025, 1, 1),
            'acquisition_cost': 145000.00,
            'department': dept_cs,
            'asset_class': 'ICT EQUIPMENT',
            'asset_nature': 'LAPTOPS'
        }
    )
    
    a2, _ = Asset.objects.get_or_create(
        property_number='PN-2026-002',
        defaults={
            'name': 'Epson EB-X06 Projector', 
            'date_acquired': datetime.date(2025, 2, 1),
            'acquisition_cost': 22000.00,
            'department': dept_eng,
            'asset_class': 'OFFICE EQUIPMENT',
            'asset_nature': 'AUDIO_VIDEO_AND_BROADCAST'
        }
    )

    # 1. Inspection
    step_ins = wf_inspect.phases.first().steps.filter(label="Pending Inspection").first()
    InspectionRequest.objects.update_or_create(
        asset=a2,
        defaults={
            'requestor': admin_user,
            'notes': 'Demo: Projector lens needs cleaning check.',
            'status': 'Pending Inspection',
            'current_step': step_ins
        }
    )

    # 2. Transfer
    step_trf = wf_transfer.phases.first().steps.first()
    AssetTransferRequest.objects.update_or_create(
        asset=a1,
        defaults={
            'requestor': admin_user,
            'current_officer': 'Juan Dela Cruz',
            'new_officer_firstname': 'Maria',
            'new_officer_surname': 'Clara',
            'remarks': 'Demo: Transferring laptop for CS Dean office use.',
            'status': 'PENDING',
            'current_step': step_trf
        }
    )

    # 3. Return
    step_ret = wf_return.phases.first().steps.filter(label="Unit Head Approval").first()
    AssetReturnRequest.objects.update_or_create(
        asset=a2,
        defaults={
            'requestor': admin_user,
            'reason': 'Demo: End of project. Returning projector to central storage.',
            'status': 'Pending',
            'current_step': step_ret
        }
    )

    # 4. Loss Report
    a3, _ = Asset.objects.get_or_create(
        property_number='PN-2026-LOST',
        defaults={
            'name': 'Samsung Galaxy Tab S9', 
            'date_acquired': datetime.date(2024, 6, 1),
            'acquisition_cost': 45000.00,
            'department': dept_cs,
            'asset_nature': 'TABLETS'
        }
    )
    step_loss = wf_loss.phases.first().steps.filter(label="Investigation Phase").first()
    AssetLossReport.objects.update_or_create(
        asset=a3,
        defaults={
            'requestor': admin_user,
            'incident_date': datetime.date(2026, 3, 1),
            'description': 'Demo: Tablet misplaced during field visit.',
            'status': 'Pending',
            'current_step': step_loss
        }
    )

    # 5. Clearance
    step_clr = wf_clearance.phases.first().steps.filter(label="Unit Head Clearance").first()
    PropertyClearanceRequest.objects.update_or_create(
        requestor=admin_user,
        defaults={
            'purpose': 'Demo: Retirement Clearance Requirement.',
            'status': 'Pending',
            'current_step': step_clr
        }
    )

    print("Seeding Complete!")

if __name__ == "__main__":
    seed_demo()
