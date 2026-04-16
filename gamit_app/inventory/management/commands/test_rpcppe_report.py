from django.core.management.base import BaseCommand
from inventory.models import Asset, Department
from django.db.models import Sum

class Command(BaseCommand):
    help = 'Tests RPCPPE grouping by department with totals'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- RPCPPE Grouping Test ---'))

        # 1. Ensure test departments exist
        dept_it, _ = Department.objects.get_or_create(name='INFORMATION TECHNOLOGY')
        dept_hr, _ = Department.objects.get_or_create(name='HUMAN RESOURCES')
        dept_spmo, _ = Department.objects.get_or_create(name='SPMO ADMIN')

        # 2. Update or Create some assets for testing
        test_data = [
            {'name': 'MacBook Pro 16', 'dept': dept_it, 'cost': 120000.00, 'brand': 'Apple'},
            {'name': 'Dell XPS 15', 'dept': dept_it, 'cost': 95000.00, 'brand': 'Dell'},
            {'name': 'Office Chair Ergonomic', 'dept': dept_hr, 'cost': 15000.00, 'brand': 'Steelcase'},
            {'name': 'Filing Cabinet 4-Drawer', 'dept': dept_hr, 'cost': 8500.00, 'brand': 'Generic'},
            {'name': 'Server Rack 42U', 'dept': dept_spmo, 'cost': 45000.00, 'brand': 'APC'},
        ]

        for item in test_data:
            Asset.objects.update_or_create(
                name=item['name'],
                defaults={
                    'department': item['dept'],
                    'acquisition_cost': item['cost'],
                    'brand': item['brand'],
                    'unit_of_measure': 'unit',
                    'quantity_physical_count': 1,
                    'status': 'SERVICEABLE',
                    'date_acquired': '2025-01-01'
                }
            )

        # 3. Verify Grouping & Totals
        assets = Asset.objects.filter(status='SERVICEABLE').select_related('department').order_by('department__name')
        
        grouped = {}
        for a in assets:
            d_name = a.department.name if a.department else "UNASSIGNED"
            if d_name not in grouped:
                grouped[d_name] = {'items': [], 'total': 0}
            grouped[d_name]['items'].append(a)
            grouped[d_name]['total'] += (a.acquisition_cost or 0)

        # 4. Print Summary
        grand_total = 0
        for dept, data in grouped.items():
            self.stdout.write(f"\nDEPARTMENT: {dept}")
            for item in data['items']:
                name = item.name or ""
                brand = item.brand or ""
                cost = item.acquisition_cost or 0
                self.stdout.write(f"  - {name:30} | {brand:15} | PHP {cost:12,.2f}")
            self.stdout.write(self.style.MIGRATE_HEADING(f"  SUBTOTAL: PHP {data['total']:12,.2f}"))
            grand_total += data['total']

        self.stdout.write(self.style.SUCCESS(f"\nGRAND TOTAL: PHP {grand_total:12,.2f}"))
        self.stdout.write(self.style.SUCCESS('--- Test Completed ---'))
