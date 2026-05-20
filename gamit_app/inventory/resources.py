# inventory/resources.py

from import_export import resources, fields, widgets
from .models import Asset, Department
from workflow.models import Persona, Role
from django.contrib.auth.models import User

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

    # --- DEHYDRATE METHODS: Computed Properties for Export ---
    def dehydrate_book_value(self, asset):
        """Acquisition Cost - Accumulated Depreciation"""
        val = asset.book_value
        return f"{val:.2f}" if val is not None else ''

    def dehydrate_annual_depreciation(self, asset):
        """(Acquisition Cost - Salvage Value) / Useful Life"""
        val = asset.annual_depreciation
        return f"{val:.2f}" if val is not None else ''

    def dehydrate_is_fully_depreciated(self, asset):
        return 'Yes' if asset.is_fully_depreciated else 'No'

    def dehydrate_depreciation_method(self, asset):
        return asset.get_depreciation_method_display() if asset.depreciation_method else ''

    def dehydrate_disposal_method(self, asset):
        return asset.get_disposal_method_display() if asset.disposal_method else ''

    def dehydrate_fund_source(self, asset):
        return asset.get_fund_source_display() if asset.fund_source else ''

    def dehydrate_property_classification(self, asset):
        return asset.get_property_classification_display() if asset.property_classification else ''

    def dehydrate_status(self, asset):
        return asset.get_status_display() if asset.status else ''

    def dehydrate_asset_class(self, asset):
        return asset.get_asset_class_display() if asset.asset_class else ''

    def dehydrate_asset_nature(self, asset):
        return asset.get_asset_nature_display() if asset.asset_nature else ''

    # --- Computed (virtual) fields ---
    book_value = fields.Field(column_name='book_value', readonly=True)
    annual_depreciation = fields.Field(column_name='annual_depreciation', readonly=True)
    is_fully_depreciated = fields.Field(column_name='is_fully_depreciated', readonly=True)

    class Meta:
        model = Asset
        import_id_fields = ('property_number',)
        fields = (
            # --- TAB 1: PROPERTY DETAILS ---
            'id', 'item_id', 'property_number', 'name', 'description',
            'brand', 'unit_of_measure', 'quantity_physical_count',
            'date_acquired', 'acquisition_cost',
            'department', 'asset_class', 'asset_nature', 'status',
            'accountable_firstname', 'accountable_surname',
            'accountable_middle_initial', 'assigned_custodian', 'cu',
            # --- TAB 2: FINANCE & VALUATION ---
            'fair_market_value', 'salvage_value', 'useful_life_years',
            'depreciation_method', 'accumulated_depreciation',
            'depreciation_start_date',
            'book_value', 'annual_depreciation', 'is_fully_depreciated',
            # --- TAB 3: LIFECYCLE ---
            'warranty_expiry', 'insurance_value',
            'disposal_date', 'disposal_method', 'disposal_proceeds',
            # --- TAB 4: GOVERNMENT / COA ---
            'uacs_object_code', 'fund_source', 'property_classification',
            'appraisal_date', 'appraised_value',
        )
        export_order = (
            # Property
            'id', 'item_id', 'property_number', 'name', 'description',
            'brand', 'unit_of_measure', 'quantity_physical_count',
            'date_acquired', 'acquisition_cost',
            'department', 'asset_class', 'asset_nature', 'status',
            'accountable_firstname', 'accountable_surname',
            'accountable_middle_initial', 'assigned_custodian', 'cu',
            # Finance
            'fair_market_value', 'salvage_value', 'useful_life_years',
            'depreciation_method', 'accumulated_depreciation',
            'depreciation_start_date',
            'book_value', 'annual_depreciation', 'is_fully_depreciated',
            # Lifecycle
            'warranty_expiry', 'insurance_value',
            'disposal_date', 'disposal_method', 'disposal_proceeds',
            # Government / COA
            'uacs_object_code', 'fund_source', 'property_classification',
            'appraisal_date', 'appraised_value',
        )
        skip_diff = True


# --- Persona Resource for Easy Staff Tagging ---
class PersonaResource(resources.ModelResource):
    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=widgets.ForeignKeyWidget(User, 'username')
    )
    role = fields.Field(
        column_name='role',
        attribute='role',
        widget=widgets.ForeignKeyWidget(Role, 'code')
    )
    department = fields.Field(
        column_name='department',
        attribute='department',
        widget=widgets.ForeignKeyWidget(Department, 'name')
    )

    class Meta:
        model = Persona
        fields = ('id', 'user', 'role', 'department', 'is_active', 'signature_image', 'position_title')
        export_order = ('id', 'user', 'role', 'department', 'is_active', 'position_title', 'signature_image')
