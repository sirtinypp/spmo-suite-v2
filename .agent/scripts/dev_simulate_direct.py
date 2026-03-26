import os
import sys
import django
import random
from datetime import date
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image, ImageDraw

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from django.contrib.auth.models import User
from inventory.models import (
    Department, Asset, AssetBatch, BatchItem, AssetTransferRequest,
    InspectionRequest, AssetReturnRequest, AssetLossReport, PropertyClearanceRequest
)
from workflow.models import Role, Persona, WorkflowMovementLog

def create_signature(name, color=(0, 0, 150)):
    # Generate a dummy signature image
    img = Image.new('RGBA', (300, 100), color=(255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    # Just draw some text for a signature
    d.text((10, 30), f"Signed: {name}", fill=color)
    buf = BytesIO()
    img.save(buf, format='PNG')
    return ContentFile(buf.getvalue(), name=f"{name.replace(' ', '_')}_sig.png")

def simulate_direct_injection():
    print("🚀 Starting DIRECT INJECTION to DEV DB...")

    dept, _ = Department.objects.get_or_create(name='SPMO Testing Unit')

    # Re-create SSPMO Actors
    r_ao, _ = Role.objects.get_or_create(name='Admin Officer (SPMO)', code='SPMO_AO')
    r_sup, _ = Role.objects.get_or_create(name='SPMO Inventory Supervisor', code='SPMO_SUPERVISOR')
    r_chief, _ = Role.objects.get_or_create(name='SPMO Chief / Director', code='SPMO_CHIEF')
    r_insp, _ = Role.objects.get_or_create(name='Inspection Officer (SPMO)', code='INSPECTION_OFFICER')
    r_unit, _ = Role.objects.get_or_create(name='Admin Officer (Unit)', code='UNIT_AO')
    r_head, _ = Role.objects.get_or_create(name='Unit Head / Chief', code='UNIT_HEAD')
    r_admin_sup, _ = Role.objects.get_or_create(name='SPMO Admin Supervisor', code='SPMO_ADMIN_SUPERVISOR')

    # Users
    u_unit_head, _ = User.objects.get_or_create(username='dev_unit_head', first_name='Unit', last_name='Chief')
    p_unit_head, _ = Persona.objects.get_or_create(user=u_unit_head, role=r_head)
    if not p_unit_head.signature_image: p_unit_head.signature_image = create_signature('Unit Chief')
    p_unit_head.save()

    u_unit, _ = User.objects.get_or_create(username='dev_unit_ao', first_name='Unit', last_name='Officer')
    p_unit, _ = Persona.objects.get_or_create(user=u_unit, role=r_unit)
    if not p_unit.signature_image: p_unit.signature_image = create_signature('Unit Officer')
    p_unit.save()

    u_ao, _ = User.objects.get_or_create(username='dev_spmo_ao', first_name='Eldefonso', last_name='AO')
    p_ao, _ = Persona.objects.get_or_create(user=u_ao, role=r_ao)
    if not p_ao.signature_image: p_ao.signature_image = create_signature('Eldefonso')
    p_ao.save()

    u_sup, _ = User.objects.get_or_create(username='dev_spmo_sup', first_name='Julius', last_name='Supervisor')
    p_sup, _ = Persona.objects.get_or_create(user=u_sup, role=r_sup)
    if not p_sup.signature_image: p_sup.signature_image = create_signature('Julius')
    p_sup.save()
    
    # Assign Julius to Admin Sup as well
    p_admin_sup, _ = Persona.objects.get_or_create(user=u_sup, role=r_admin_sup)
    if not p_admin_sup.signature_image: p_admin_sup.signature_image = create_signature('Julius')
    p_admin_sup.save()

    u_insp, _ = User.objects.get_or_create(username='dev_spmo_insp', first_name='Mark', last_name='Inspector')
    p_insp, _ = Persona.objects.get_or_create(user=u_insp, role=r_insp)
    if not p_insp.signature_image: p_insp.signature_image = create_signature('Mark')
    p_insp.save()

    u_chief, _ = User.objects.get_or_create(username='dev_spmo_chief', first_name='Isagani L.', last_name='Bagus')
    p_chief, _ = Persona.objects.get_or_create(user=u_chief, role=r_chief)
    if not p_chief.signature_image: p_chief.signature_image = create_signature('Isagani L. Bagus')
    p_chief.save()

    print("✅ SSPMO Actors Ready.")

    def forge_movement(record, record_type, p_actor, action_taken, status_label):
        WorkflowMovementLog.objects.create(
            **{record_type: record},
            user=p_actor.user,
            persona=p_actor,
            role_name=p_actor.role.name,
            unit_name=dept.name,
            action_taken=action_taken,
            status_label=status_label,
            signature_snapshot=p_actor.signature_image
        )

    # 1. BATCH ACQUISITION
    assets = []
    for i in range(2):
        batch, _ = AssetBatch.objects.get_or_create(
            transaction_id=f'DEV-INJ-BATCH-00{i+1}',
            defaults={
                'requestor': u_unit, 'requesting_unit': dept.name,
                'supplier_name': 'Injected Supplier', 'po_number': f'PO-{i+100}',
                'status': 'APPROVED'
            }
        )
        if batch.items.count() == 0:
            BatchItem.objects.create(batch=batch, description=f'Inject Asset {i}', amount=50000.0, quantity=1, assigned_custodian='Dev')
        
        # Forge Logs
        batch.movement_logs.all().delete()
        
        # 11 Steps of Official Procurement Flow
        forge_movement(batch, 'batch', p_unit, 'Drafted Batch Request', 'Draft / Anticipatory')
        forge_movement(batch, 'batch', p_unit_head, 'Endorsed Unit Request', 'For Unit Chief Approval')
        forge_movement(batch, 'batch', p_ao, 'Verified Documents', 'Verify Completeness (SPMO)')
        forge_movement(batch, 'batch', p_ao, 'Signed Receipt', 'For SPMO AO Signature')
        forge_movement(batch, 'batch', p_insp, 'Initiated Inspection', 'Initiate Inspection')
        forge_movement(batch, 'batch', p_insp, 'Generated IAR', 'Release / Save IAR')
        forge_movement(batch, 'batch', p_insp, 'Signed IAR', 'For Inspection Signature')
        forge_movement(batch, 'batch', p_sup, 'Verified IAR and Returns', 'Verify Completeness (Supv)')
        forge_movement(batch, 'batch', p_sup, 'Signed Inspection Log', 'For Supervisor Signature')
        forge_movement(batch, 'batch', p_chief, 'Approved PAR Generation', 'For Chief Final Approval')
        forge_movement(batch, 'batch', p_unit, 'Accepted Finished PAR', 'Awaiting Unit Acceptance')
        
        # Manually invoke IAR generator
        from inventory.services import ICSGenerator
        try:
            generator = ICSGenerator(batch.id)
            generator.generate_iar()
        except:
            pass # Failsafe
        
        # Create corresponding Asset
        asset, _ = Asset.objects.get_or_create(property_number=f"INJ-PAR-2026-{i+100}", defaults={'name': f"Injected Asset {i}", 'asset_class': 'ICT EQUIPMENT', 'department': dept, 'date_acquired': date.today(), 'acquisition_cost': 50000.0})
        assets.append(asset)
    print("✅ 2 Batches + IAR Injected.")

    # 2. TRANSFERS (8 Steps)
    for i in range(2):
        trans, _ = AssetTransferRequest.objects.get_or_create(
            transaction_id=f'DEV-INJ-TRANS-00{i+1}',
            defaults={
                'requestor': u_unit, 'asset': assets[i],
                'current_officer': 'Old Custodian', 'new_officer_firstname': 'New', 'new_officer_surname': 'Officer',
                'status': 'APPROVED'
            }
        )
        trans.movement_logs.all().delete()
        forge_movement(trans, 'transfer', p_unit, "Initiated Transfer Request", "Transfer Request")
        forge_movement(trans, 'transfer', p_unit_head, "Approved at Unit Level", "For Unit Chief Approval")
        forge_movement(trans, 'transfer', p_ao, "Prepared PTR", "For SPMO AO Signature")
        forge_movement(trans, 'transfer', p_sup, "Verified PTR", "Verify Completeness (Supv)")
        forge_movement(trans, 'transfer', p_sup, "Signed PTR", "For Supervisor Signature")
        forge_movement(trans, 'transfer', p_chief, "Approved PTR", "For Chief Final Signature")
        forge_movement(trans, 'transfer', p_ao, "System Values Updated", "Update Values/Confirm")
        forge_movement(trans, 'transfer', p_unit, "Acknowledged Transfer", "For Unit AO Receipt")

    # 3. INSPECTIONS (3 Steps)
    for i in range(2):
        insp, _ = InspectionRequest.objects.get_or_create(
            transaction_id=f'DEV-INJ-INSPECT-00{i+1}',
            defaults={'requestor': u_unit, 'asset': assets[i], 'status': 'Approved', 'notes': 'Direct Injected'}
        )
        insp.movement_logs.all().delete()
        forge_movement(insp, 'inspection', p_unit, "Requested Inspection", "Inspection Request")
        forge_movement(insp, 'inspection', p_insp, "Conducted Physical Inspection", "Conduct Inspection")
        forge_movement(insp, 'inspection', p_insp, "Released IAR", "Release Inspection Report")

    # 4. RETURNS (5 Steps)
    for i in range(2):
        ret, _ = AssetReturnRequest.objects.get_or_create(
            transaction_id=f'DEV-INJ-RET-00{i+1}',
            defaults={'requestor': u_unit, 'asset': assets[i], 'status': 'Approved', 'reason': 'Direct Injected'}
        )
        ret.movement_logs.all().delete()
        forge_movement(ret, 'return_request', p_unit, "Initiated Return", "Request Return")
        forge_movement(ret, 'return_request', p_unit_head, "Endorsed Return", "Unit Head Approval")
        forge_movement(ret, 'return_request', p_unit, "Signed Return Form", "For Unit AO Signature")
        forge_movement(ret, 'return_request', p_sup, "Verified Condition", "For Supervisor Signature")
        forge_movement(ret, 'return_request', p_chief, "Authorized Return", "For Chief Approval")

    # 5. LOSS REPORTS (5 Steps)
    for i in range(2):
        loss, _ = AssetLossReport.objects.get_or_create(
            transaction_id=f'DEV-INJ-LOSS-00{i+1}',
            defaults={'requestor': u_unit, 'asset': assets[i], 'status': 'Approved', 'description': 'Direct Injected (Simulated Loss)'}
        )
        loss.movement_logs.all().delete()
        forge_movement(loss, 'loss_report', p_unit, "Reported Deficit", "Request Loss Report")
        forge_movement(loss, 'loss_report', p_unit_head, "Endorsed Affidavit", "Unit Head Approval")
        forge_movement(loss, 'loss_report', p_unit, "Signed Loss Report", "For Unit AO Signature")
        forge_movement(loss, 'loss_report', p_admin_sup, "Reviewed Investigation", "For Admin Supervisor Signature")
        forge_movement(loss, 'loss_report', p_chief, "Cleared Accountability", "For Chief Approval")

    # 6. CLEARANCES (4 Steps)
    for i in range(2):
        clear, _ = PropertyClearanceRequest.objects.get_or_create(
            transaction_id=f'DEV-INJ-CLEAR-00{i+1}',
            defaults={'requestor': u_unit, 'status': 'Approved', 'purpose': 'Direct Injected'}
        )
        clear.movement_logs.all().delete()
        forge_movement(clear, 'clearance', p_unit_head, "Initiated Clearance", "Unit Head Clearance")
        forge_movement(clear, 'clearance', p_ao, "Checked Accountability", "SPMO Verification")
        forge_movement(clear, 'clearance', p_admin_sup, "Verified No Obligations", "Admin Supervisor Signature")
        forge_movement(clear, 'clearance', p_chief, "Granted Property Clearance", "Chief Final Clearance")

    print("🎉 ALL DIRECT INJECTIONS COMPLETE: Verified Signatures Attached.")

if __name__ == "__main__":
    simulate_direct_injection()
