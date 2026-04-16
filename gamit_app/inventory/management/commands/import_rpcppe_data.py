import csv
import decimal
from django.core.management.base import BaseCommand
from inventory.models import Asset, Department

class Command(BaseCommand):
    help = 'Imports actual RPCPPE data from the COA CSV file'

    def handle(self, *args, **options):
        csv_file_path = "/app/rpcppe_data.csv"
        self.stdout.write(f'Importing from {csv_file_path}...')

        with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            # Skip header rows (1-7)
            for _ in range(7):
                next(reader)
            
            count = 0
            for row in reader:
                if not row or len(row) < 13:
                    continue
                
                article = row[0].strip()
                brand = row[1].strip()
                description = row[2].strip()
                prop_num = row[3].strip()
                uom = row[4].strip()
                cost_str = row[5].replace(',', '').replace('"', '').strip()
                qty_card = row[6].strip()
                qty_physical = row[7].strip()
                office_name = row[12].strip()
                
                if not prop_num or not office_name:
                    continue

                # 1. Get or create Department
                dept, _ = Department.objects.get_or_create(name=office_name)

                # 2. Cleanup cost
                try:
                    cost = decimal.Decimal(cost_str) if cost_str else 0
                except decimal.InvalidOperation:
                    cost = 0

                # 3. Create Asset
                Asset.objects.update_or_create(
                    property_number=prop_num,
                    defaults={
                        'name': article,
                        'brand': brand,
                        'description': description,
                        'unit_of_measure': uom or 'Unit',
                        'acquisition_cost': cost,
                        'quantity_physical_count': int(qty_physical) if qty_physical.isdigit() else 1,
                        'department': dept,
                        'asset_class': article, # Article maps to Category in GAMIT context
                        'status': 'SERVICEABLE',
                        'date_acquired': '2026-01-01', # Placeholder for date
                    }
                )
                count += 1
                if count % 100 == 0:
                    self.stdout.write(f'Imported {count} assets...')

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} assets.'))
