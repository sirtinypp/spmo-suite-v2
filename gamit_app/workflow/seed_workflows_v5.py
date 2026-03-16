
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from workflow.models import Role, ActionProcess, Workflow, WorkflowPhase, WorkflowStep, SignatorySlot
from inventory.models import Department

def seed_v5():
    print("🚀 Starting Phase 5 Official Workflow Seeding...")

    # 1. PERSONA ROLES (7 Mandatory Roles)
    roles = [
        ('Admin Officer (Unit)', 'UNIT_AO', 'Initiates and receives unit-level assets.'),
        ('Unit Head / Chief', 'UNIT_HEAD', 'Endorses unit-level requests.'),
        ('Admin Officer (SPMO)', 'SPMO_AO', 'Primary encoder and verifier for SPMO.'),
        ('Inspection Officer (SPMO)', 'INSPECTION_OFFICER', 'Conducts technical inspections and releases IAR.'),
        ('SPMO Inventory Supervisor', 'SPMO_SUPERVISOR', 'Verifies completeness for Inventory Team.'),
        ('SPMO Admin Supervisor', 'SPMO_ADMIN_SUPERVISOR', 'Verifies Personnel Clearance and Loss reports.'),
        ('SPMO Chief / Director', 'SPMO_CHIEF', 'Final approving authority.')
    ]
    
    role_map = {}
    for name, code, desc in roles:
        obj, _ = Role.objects.update_or_create(code=code, defaults={'name': name, 'description': desc})
        role_map[code] = obj
        print(f"✅ Role Ready: {code}")

    # 2. HELPER: Build Comprehensive Workflow
    def build_wf(proc_code, proc_name, wf_name, steps_data):
        proc, _ = ActionProcess.objects.get_or_create(code=proc_code, defaults={'name': proc_name})
        wf, created = Workflow.objects.get_or_create(process=proc, name=wf_name)
        
        # Clear existing phases/steps to ensure "Pristine" seed
        wf.phases.all().delete()
        
        phase = WorkflowPhase.objects.create(workflow=wf, name="Official Process", order=10)
        
        for i, (label, role_code) in enumerate(steps_data):
            WorkflowStep.objects.create(
                phase=phase,
                label=label,
                order=(i+1)*10,
                required_persona_role=role_map.get(role_code)
            )
        print(f"📦 Workflow Seeded: {wf_name} ({len(steps_data)} steps)")

    # --- 3. THE 6 OFFICIAL PROCESSES ---

    # A. BATCH ACQUISITION (11 Steps + Finalize)
    build_wf("BATCH_ACQUISITION", "Batch Acquisition / Procurement", "Official Procurement Flow", [
        ("Draft / Anticipatory", "UNIT_AO"),
        ("For Unit Chief Approval", "UNIT_HEAD"),
        ("Verify Completeness (SPMO)", "SPMO_AO"),
        ("For SPMO AO Signature", "SPMO_AO"),
        ("Initiate Inspection", "INSPECTION_OFFICER"),
        ("Release / Save IAR", "INSPECTION_OFFICER"),
        ("For Inspection Signature", "INSPECTION_OFFICER"),
        ("Verify Completeness (Supv)", "SPMO_SUPERVISOR"),
        ("For Supervisor Signature", "SPMO_SUPERVISOR"),
        ("For Chief Final Approval", "SPMO_CHIEF"),
        ("Awaiting Unit Acceptance", "UNIT_AO"),
    ])
    # Mapping correction for steps that share roles but need clear labels
    # Actually, the labels ARE the steps. Role can be same.
    # Correcting the INSPECTION_OFF_SIGN to INSPECTION_OFFICER
    
    # B. INSPECTION (R&M)
    build_wf("ASSET_INSPECT", "Inspection (Repair & Maintenance)", "Standard R&M Inspection", [
        ("Inspection Request", "UNIT_AO"),
        ("Conduct Inspection", "INSPECTION_OFFICER"),
        ("Release Inspection Report", "INSPECTION_OFFICER"),
    ])

    # C. TRANSFER (Inter-System / Unit to Unit)
    build_wf("ASSET_TRANSFER", "Asset Transfer (Unit to Unit)", "Inter-System Transfer", [
        ("Transfer Request", "UNIT_AO"),
        ("For Unit Chief Approval", "UNIT_HEAD"),
        ("For SPMO AO Signature", "SPMO_AO"),
        ("Verify Completeness (Supv)", "SPMO_SUPERVISOR"),
        ("For Supervisor Signature", "SPMO_SUPERVISOR"),
        ("For Chief Final Signature", "SPMO_CHIEF"),
        ("Update Values/Confirm", "SPMO_AO"),
        ("For Unit AO Receipt", "UNIT_AO"),
    ])

    # D. TRANSFER (Inter-CU / Cross-Campus)
    build_wf("ASSET_TRANSFER_CU", "Asset Transfer (Inter-CU)", "Cross-Campus Transfer", [
        ("Transfer Request", "UNIT_AO"),
        ("For Unit Chief Approval", "UNIT_HEAD"),
        ("For SPMO AO Signature", "SPMO_AO"),
        ("Verify Completeness (Supv)", "SPMO_SUPERVISOR"),
        ("For Supervisor Signature", "SPMO_SUPERVISOR"),
        ("For Chief Final Signature", "SPMO_CHIEF"),
        ("For VP Approval", "SPMO_CHIEF"), # VP proxy per Matrix
        ("Update Values/Confirm", "SPMO_AO"),
        ("For Unit AO Receipt", "UNIT_AO"),
    ])

    # E. RETURN
    build_wf("ASSET_RETURN", "Asset Return", "Standard Return Flow", [
        ("Request Return", "UNIT_AO"),
        ("Unit Head Approval", "UNIT_HEAD"),
        ("For Unit AO Signature", "UNIT_AO"),
        ("For Supervisor Signature", "SPMO_SUPERVISOR"),
        ("For Chief Approval", "SPMO_CHIEF"),
    ])

    # F. LOSS REPORT
    build_wf("ASSET_LOSS", "Asset Loss Report", "Standard Loss Flow", [
        ("Request Loss Report", "UNIT_AO"),
        ("Unit Head Approval", "UNIT_HEAD"),
        ("For Unit AO Signature", "UNIT_AO"),
        ("For Admin Supervisor Signature", "SPMO_ADMIN_SUPERVISOR"),
        ("For Chief Approval", "SPMO_CHIEF"),
    ])

    # G. PERSONNEL CLEARANCE
    build_wf("ASSET_CLEARANCE", "Personnel Property Clearance", "Official Clearance Flow", [
        ("Unit Head Clearance", "UNIT_HEAD"),
        ("SPMO Verification", "SPMO_AO"),
        ("Admin Supervisor Signature", "SPMO_ADMIN_SUPERVISOR"),
        ("Chief Final Clearance", "SPMO_CHIEF"),
    ])

    print("✨ Phase 5 Seeding Complete!")

if __name__ == "__main__":
    seed_v5()
