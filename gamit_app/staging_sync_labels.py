from inventory.models import Asset

def fix_labels():
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
    }
    
    # Generic Case-Insensitive Sweep
    print("Starting database label sync...")
    updated_total = 0
    
    for old, new in mapping.items():
        # Update Asset Class
        c1 = Asset.objects.filter(asset_class__iexact=old).update(asset_class=new)
        if c1:
            print(f"Updated {c1} records for class: [{old}] -> [{new}]")
            updated_total += c1
            
        # Update Asset Nature
        c2 = Asset.objects.filter(asset_nature__iexact=old).update(asset_nature=new)
        if c2:
            print(f"Updated {c2} records for nature: [{old}] -> [{new}]")
            updated_total += c2
            
    print(f"Sync complete. Total records updated: {updated_total}")

if __name__ == "__main__":
    fix_labels()
