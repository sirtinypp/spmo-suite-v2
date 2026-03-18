import os
import django
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from django.contrib.auth.models import User
from inventory.models import AssetBatch, BatchItem, Department
from workflow.models import Workflow, WorkflowStep, Role

def create_test_batch():
    # 1. Get or Create User
    admin_user, _ = User.objects.get_or_create(username='grootadmin', is_staff=True)
    
    # 2. Get Department
    dept, _ = Department.objects.get_or_create(name='Accounting Office')
    
    # 3. Create Asset Batch
    batch = AssetBatch.objects.create(
        transaction_id='BATCH-TEST-004',
        requestor=admin_user,
        requesting_unit='Accounting Office',
        requesting_unit_obj=dept,
        supplier_name='Tech Solutions Inc.',
        po_number='PO-2026-0001',
        sales_invoice_number='SI-9988',
        acceptance_report_number='IAR-2026-0012',
        fund_cluster='01',
        ups_dv_number='DV-2026-4455',
        status='ANTICIPATORY'
    )
    
    # 4. Create 3 Batch Items
    items_data = [
        {'desc': 'High-End Laptop', 'qty': 1, 'price': 75000, 'custodian': 'Maria Clara'},
        {'desc': 'Ergonomic Office Chair', 'qty': 1, 'price': 15000, 'custodian': 'Elias'},
        {'desc': 'HD Projector', 'qty': 1, 'price': 45000, 'custodian': 'Crisostomo Ibarra'}
    ]
    
    for item in items_data:
        BatchItem.objects.create(
            batch=batch,
            description=item['desc'],
            quantity=item['qty'],
            amount=item['price'],
            assigned_custodian=item['custodian']
        )
    
    print(f"Batch {batch.transaction_id} created with 3 items.")
    return batch

if __name__ == "__main__":
    create_test_batch()
