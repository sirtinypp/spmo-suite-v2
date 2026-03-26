import os
import sys
import django
import random
from datetime import date

# Set up Django environment manually since we run this as a standalone script
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from django.contrib.auth.models import User
from inventory.models import (
    Department, Asset, AssetBatch, BatchItem, AssetTransferRequest,
    InspectionRequest, AssetReturnRequest, AssetLossReport, PropertyClearanceRequest
)
from workflow.models import Role, Persona

def simulate_dev_data():
    print("🚀 Starting DEV SERVER Data Simulation...")

    # 1. Setup Base Entities (Department, Roles, Users)
    dept, _ = Department.objects.get_or_create(name='College of Science')
    dept2, _ = Department.objects.get_or_create(name='College of Arts')
    
    role_ao, _ = Role.objects.get_or_create(name='Administrative Officer', code='UNIT_AO')
    role_head, _ = Role.objects.get_or_create(name='Unit Head / Chief', code='UNIT_HEAD')

    user_ao, _ = User.objects.get_or_create(username='dev_unit_ao', first_name='Unit', last_name='AO')
    user_ao.set_password('password123')
    user_ao.save()
    Persona.objects.get_or_create(user=user_ao, role=role_ao, department=dept, position_title='Admin Officer I')

    user_head, _ = User.objects.get_or_create(username='dev_unit_head', first_name='Unit', last_name='Head')
    user_head.set_password('password123')
    user_head.save()
    Persona.objects.get_or_create(user=user_head, role=role_head, department=dept, position_title='College Dean')

    print("✅ Base identities established.")

    # 2. Setup Assets
    assets = []
    for i in range(5):
        asset, _ = Asset.objects.get_or_create(
            property_number=f"DEV-PAR-2026-{i+100}",
            defaults={
                'name': f'Dev Sample Asset {i+1} (Simulated)',
                'description': f'A fully simulated asset for dev testing {i+1}',
                'department': dept,
                'asset_class': 'ICT',
                'acquisition_cost': 25000.00 + (i * 1000),
                'date_acquired': date.today(),
                'status': 'ACTIVE',
                'assigned_custodian': 'Dev Custodian'
            }
        )
        assets.append(asset)
    print("✅ Base assets injected.")

    # 3. Simulate 2 Batches
    for i in range(2):
        batch, _ = AssetBatch.objects.get_or_create(
            transaction_id=f'DEV-BATCH-00{i+1}',
            defaults={
                'requestor': user_ao,
                'requesting_unit': 'College of Science',
                'requesting_unit_obj': dept,
                'supplier_name': f'Dev Supplier Corp {i+1}',
                'po_number': f'PO-DEV-2026-00{i+1}',
                'fund_cluster': '01',
                'status': 'PENDING'
            }
        )
        if hasattr(batch, 'items') and batch.items.count() == 0:
            BatchItem.objects.create(batch=batch, description=f'Item A for Batch {i+1}', amount=15000.00, quantity=1, assigned_custodian='Dev Custodian A')
            BatchItem.objects.create(batch=batch, description=f'Item B for Batch {i+1}', amount=12000.00, quantity=1, assigned_custodian='Dev Custodian B')

    # 4. Simulate 2 Transfers
    for i in range(2):
        AssetTransferRequest.objects.get_or_create(
            transaction_id=f'DEV-TRANS-00{i+1}',
            defaults={
                'requestor': user_ao,
                'asset': assets[i],
                'current_officer': 'Dev Custodian',
                'new_officer_firstname': 'New',
                'new_officer_surname': f'Officer {i+1}',
                'remarks': 'Simulated dev transfer request.',
                'status': 'PENDING'
            }
        )

    # 5. Simulate 2 Inspections
    for i in range(2):
        InspectionRequest.objects.get_or_create(
            transaction_id=f'DEV-INSPECT-00{i+1}',
            defaults={
                'requestor': user_ao,
                'asset': assets[i+2],
                'notes': 'Device requires technical inspection. Simulated.',
                'status': 'PENDING'
            }
        )

    # 6. Simulate 2 Returns
    for i in range(2):
        AssetReturnRequest.objects.get_or_create(
            transaction_id=f'DEV-RET-00{i+1}',
            defaults={
                'requestor': user_ao,
                'asset': assets[i+1],
                'reason': 'Item is defective / End of Life. Simulated.',
                'status': 'PENDING'
            }
        )

    # 7. Simulate 1 Loss Report
    AssetLossReport.objects.get_or_create(
        transaction_id='DEV-LOSS-001',
        defaults={
            'requestor': user_ao,
            'asset': assets[4],
            'reason': 'Lost during transit. Affidavit attached (simulated).',
            'status': 'PENDING'
        }
    )

    # 8. Simulate 2 Clearances
    for i in range(2):
        PropertyClearanceRequest.objects.get_or_create(
            transaction_id=f'DEV-CLEAR-00{i+1}',
            defaults={
                'requestor': user_ao,
                'purpose': 'Resignation clearance testing (DEV).',
                'status': 'PENDING'
            }
        )

    print("🎉 DEV SIMULATION COMPLETE: Injected Batches, Transfers, Inspections, Returns, Losses, and Clearances.")

if __name__ == "__main__":
    simulate_dev_data()
