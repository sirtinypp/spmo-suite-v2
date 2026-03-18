import os
import sys
import django

# Add spmo_website to sys.path
sys.path.append(os.path.join(os.getcwd(), 'spmo_website'))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from gamit_app.inventory.models import AssetBatch, BatchItem, Department
from gamit_app.workflow.models import Role, Persona, Workflow, ActionProcess

def simulate_batch():
    # 1. Get or Create User & Persona
    user, _ = User.objects.get_or_create(username='test_admin', is_staff=True)
    user.set_password('password123')
    user.save()
    
    dept, _ = Department.objects.get_or_create(name='College of Engineering', code='COE')
    role, _ = Role.objects.get_or_create(name='Administrative Officer', code='UNIT_AO')
    Persona.objects.get_or_create(user=user, role=role, department=dept)

    # 2. Create Batch
    batch = AssetBatch.objects.create(
        requestor=user,
        requesting_unit='College of Engineering',
        requesting_unit_obj=dept,
        fund_cluster='01',
        supplier_name='Test Supplier',
        po_number='PO-2026-001',
        transaction_id='BATCH-TEST-001'
    )

    # 3. Add 3 Items with Custodians
    BatchItem.objects.create(
        batch=batch,
        description='High-End Laptop',
        assigned_custodian='Juan Dela Cruz (JO)',
        amount=75000.00,
        quantity=1
    )
    BatchItem.objects.create(
        batch=batch,
        description='Ergonomic Chair',
        assigned_custodian='Maria Clara (COS)',
        amount=15000.00,
        quantity=1
    )
    BatchItem.objects.create(
        batch=batch,
        description='Laser Printer',
        assigned_custodian='Pedro Penduko (Staff)',
        amount=25000.00,
        quantity=1
    )

    print(f"Simulation Batch Created: {batch.transaction_id}")
    return batch.id

if __name__ == "__main__":
    simulate_batch()
