# inventory/resources.py

from import_export import resources, fields, widgets
from .models import Asset, Department
import tablib
from django.db import IntegrityError
import math

# --- Custom Widget for Safe Date Conversion ---
class CustomDateWidget(widgets.DateWidget):
    """Simple date widget that handles basic null values."""
    def clean(self, value, row=None, *args, **kwargs):
        if value in ['', 'NULL', 'null', 'N/A', None]:
            return None
        return super().clean(value, row, *args, **kwargs)

# --- Global Monkeypatch for CSV Encoding Robustness ---
from import_export.formats import base_formats

def patch_csv_format():
    """
    Monkeypatches the base CSV format class to handle non-UTF-8 files globally.
    Forces binary read mode to bypass early decoding crashes.
    """
    def robust_create_dataset(self, in_stream, **kwargs):
        if isinstance(in_stream, bytes):
            raw_bytes = in_stream
        elif hasattr(in_stream, 'read'):
            raw_bytes = in_stream.read()
            if hasattr(in_stream, 'seek'):
                in_stream.seek(0)
        else:
            return super(base_formats.CSV, self).create_dataset(in_stream, **kwargs)

        # Try multiple common encodings for Philippines/Windows/Excel environments
        for encoding in ('utf-8', 'utf-8-sig', 'cp1252', 'latin-1'):
            try:
                decoded = raw_bytes.decode(encoding)
                dataset = tablib.Dataset()
                dataset.csv = decoded
                return dataset
            except Exception:
                continue
        
        return super(base_formats.CSV, self).create_dataset(in_stream, **kwargs)

    base_formats.CSV.create_dataset = robust_create_dataset
    base_formats.CSV.get_read_mode = lambda self: "rb"

# Execute the patch on module load
patch_csv_format()

# --- Asset Resource Definition ---
class AssetResource(resources.ModelResource):
    """
    Simplified resource for direct mapping.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Track property numbers processed in the CURRENT session to prevent internal-CSV duplicates
        self._processed_numbers = set()

    # Map 'ppe_category' column to 'asset_class'
    asset_class = fields.Field(
        attribute='asset_class',
        column_name='ppe_category',
    )
    
    # Map 'asset_type' column to 'asset_nature'
    asset_nature = fields.Field(
        attribute='asset_nature',
        column_name='asset_type',
    )


    # Map 'date_acquired' with our simple date widget
    date_acquired = fields.Field(
        attribute='date_acquired',
        column_name='date_acquired',
        widget=CustomDateWidget(format='%m/%d/%Y'),
    )

    # Map 'assigned_office' column to the 'department' ForeignKey
    department = fields.Field(
        attribute='department',
        column_name='assigned_office',
        widget=widgets.ForeignKeyWidget(Department, 'name')
    )

    def before_import_row(self, row, **kwargs):
        # 0. CATEGORY MAPPING & NORMALIZATION
        # PPE CATEGORY MAPPING
        # PPE CATEGORY MAPPING (1:1 with standard CSV)
        ppe_map = {
            'ICT EQUIPMENT': 'ICT EQUIPMENT',
            'MACHINERY': 'MACHINERY',
            'MOTOR VEHICLE': 'MOTOR VEHICLE',
            'VEHICLE': 'MOTOR VEHICLE',
            'OFFICE EQUIPMENT': 'OFFICE EQUIPMENT',
            'TECHNICAL AND SCIENTIFIC EQUIPMENT': 'TECHNICAL AND SCIENTIFIC EQUIPMENT',
            'FURNITURE AND FIXTURES': 'FURNITURE AND FIXTURES',
            'AIRCONDITIONING': 'AIRCONDITIONING',
        }

        # Apply PPE Category Mapping
        raw_ppe = str(row.get('ppe_category', '')).strip().upper()
        row['asset_class'] = ppe_map.get(raw_ppe, 'OTHER')

        # Map Asset Type
        raw_type = str(row.get('asset_type', '')).strip()
        if raw_type:
            row['asset_nature'] = raw_type.replace(' ', '_').replace('&', 'AND').replace('/', '_').upper()
        else:
            row['asset_nature'] = 'OTHER'

        # 1. Automated PAR prefixing for property numbers
        prop_no = row.get('property_number')
        if prop_no:
            prop_no = str(prop_no).strip()
            if not prop_no.upper().startswith('PAR-'):
                prop_no = f"PAR-{prop_no}"
            row['property_number'] = prop_no

        # 2. Handle Status (Case-Insensitive)
        status = row.get('status')
        if status:
            row['status'] = str(status).strip().upper()
        
        # 3. Handle Department (Auto-Creation if missing)
        office_name = row.get('assigned_office') # CSV Header name
        if office_name:
            dept_obj, created = Department.objects.get_or_create(name=str(office_name).strip())
            row['department'] = dept_obj.id

        # 4. TRUNCATION: Prevent "Value too long" (max 255 for CharField)
        name = row.get('name')
        if name and len(str(name)) > 250:
            row['name'] = str(name)[:250] # Truncate to 250 for safety

        return row

    def skip_row(self, instance, original, row, import_validation_errors=None, **kwargs):
        # A. ONLY skip if both critical IDs are missing
        prop_no = row.get('property_number')
        date_acq = row.get('date_acquired')
        if not prop_no and not date_acq:
            return True
        
        # B. DEDUPLICATION: Skip if we've already seen this Property Number in this file
        # This prevents the "Duplicate Key" error during a single bulk transaction.
        if prop_no in self._processed_numbers:
            return True
        
        self._processed_numbers.add(prop_no)
        return False

    class Meta:
        model = Asset
        import_id_fields = ('property_number',)
        fields = (
            'id', 'item_id', 'property_number', 'name', 'date_acquired', 
            'acquisition_cost', 'department', 'asset_class', 'asset_nature',
            'status', 'accountable_firstname', 
            'accountable_surname', 'description'
        )
        skip_diff = True
