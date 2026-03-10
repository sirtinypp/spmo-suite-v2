from django.core.management.base import BaseCommand
from inventory.models import Asset

class Command(BaseCommand):
    help = 'Synchronizes asset labels from "and" to "&" (Case-Insensitive)'

    def handle(self, *args, **options):
        mapping = {
            'Technical and Scientific Equipment': 'Technical & Scientific Equipment',
            'Furniture and Fixures': 'Furniture & Fixtures',
            'Furniture and Fixtures': 'Furniture & Fixtures',
            'Audio/Video and Broadcast': 'Audio/Video & Broadcast',
            'Communication and Audio Devices': 'Communication & Audio Devices',
            'Computer Peripherals and Servers': 'Computer Peripherals & Servers',
            'Computer Peripherals And Servers': 'Computer Peripherals & Servers',
            'Copier and Printing Devices': 'Copier & Printing Devices',
            'Desktops and All-in-one PCs': 'Desktops & All-in-one PCs',
            'Monitor and Display Devices': 'Monitor & Display Devices',
            'Network and Security Devices': 'Network & Security Devices',
            'HVAC Systems': 'HVAC System',
            'Sports & Display Systems': 'Sports & Display System',
            'Water Systems': 'Water System',
            'Cars': 'Four-Wheel Vehicle',
            'Tricycle': 'Three-Wheel Vehicle',
        }
        
        updated_total = 0
        self.stdout.write(self.style.SUCCESS("Starting database label sync..."))
        
        for old, new in mapping.items():
            # Class
            c1 = Asset.objects.filter(asset_class__iexact=old).update(asset_class=new)
            if c1:
                self.stdout.write(f"Updated {c1} records for class: [{old}] -> [{new}]")
                updated_total += c1
                
            # Nature
            c2 = Asset.objects.filter(asset_nature__iexact=old).update(asset_nature=new)
            if c2:
                self.stdout.write(f"Updated {c2} records for nature: [{old}] -> [{new}]")
                updated_total += c2
                
        self.stdout.write(self.style.SUCCESS(f"Sync complete. Total records updated: {updated_total}"))
