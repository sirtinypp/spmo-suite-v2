from inventory.models import Asset, AssetBatch, InspectionRequest, AssetTransferRequest
from django.db.models import Count
import os

print('--- ASSET SUMMARY ---')
print(f'Total Assets: {Asset.objects.count()}')
print(f'By Status: {list(Asset.objects.values("status").annotate(count=Count("id")))}')

print('\n--- TRANSACTION SUMMARY ---')
print(f'Batches: {AssetBatch.objects.count()}')
print(f'Inspections: {InspectionRequest.objects.count()}')
print(f'Transfers: {AssetTransferRequest.objects.count()}')

print('\n--- INJECTED DATA AUDIT (DEV-INJ PREFIX) ---')
inj_batches = AssetBatch.objects.filter(transaction_id__icontains='DEV-INJ')
print(f'Injected Batches: {inj_batches.count()}')
for b in inj_batches:
    print(f'  - {b.transaction_id}: {b.status} (Supplier: {b.supplier_name})')

inj_inspections = InspectionRequest.objects.filter(transaction_id__icontains='DEV-INJ')
print(f'Injected Inspections: {inj_inspections.count()}')
for i in inj_inspections:
    asset_str = i.asset.property_number if i.asset else "N/A"
    print(f'  - {i.transaction_id}: {i.status} (Asset: {asset_str})')
