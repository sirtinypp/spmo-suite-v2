# inventory/resources.py

from import_export import resources, fields, widgets
from .models import Asset
from decimal import Decimal
from django.db import IntegrityError
import re
import math  # For isnan() check instead of pandas
import tablib

# --- Custom Widget for Safe Date Conversion ---
class CustomDateWidget(widgets.DateWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if value in ['', 'NULL', 'null', 'N/A']:
            return None
        return super().clean(value, row, *args, **kwargs)

# --- Asset Resource Definition ---
class AssetResource(resources.ModelResource):
    """
    Final, most robust resource definition for bulk import.
    The clean_value method now acts as the final gatekeeper for all Decimal conversions.
    """
    
    # We redefine these fields without explicit widgets/attributes, relying entirely on clean_value and Python types.
    # The clean_value method will handle all string-to-Decimal conversions.
    
    # Custom Date Field Definition
    date_acquired = fields.Field(
        attribute='date_acquired',
        column_name='date_acquired',
        widget=CustomDateWidget(format='%m/%d/%Y'),
    )

    def create_dataset(self, in_stream, file_format=None, **kwargs):
        """
        Override to handle non-UTF-8 CSV files (e.g., Excel exports on Windows).
        Tries multiple encodings: utf-8 → utf-8-sig (BOM) → cp1252 → latin-1.
        """
        # Extract raw bytes from the input stream
        if hasattr(in_stream, 'read'):
            raw_bytes = in_stream.read()
            if hasattr(in_stream, 'seek'):
                in_stream.seek(0)
        elif isinstance(in_stream, bytes):
            raw_bytes = in_stream
        else:
            # Not bytes or stream — let the parent handle it
            return super().create_dataset(in_stream, file_format, **kwargs)

        # Try each encoding in order; latin-1 never fails (1:1 byte mapping)
        for encoding in ('utf-8', 'utf-8-sig', 'cp1252', 'latin-1'):
            try:
                decoded = raw_bytes.decode(encoding)
                dataset = tablib.Dataset()
                dataset.csv = decoded
                return dataset
            except (UnicodeDecodeError, Exception):
                continue

        # All fallbacks exhausted — let the parent try its default
        return super().create_dataset(in_stream, file_format, **kwargs)


    def clean_value(self, value, field_name):
        """
        Final robust cleaning method: Safely cleans and converts fields.
        Handles coordinates (lat/long) differently from monetary fields.
        """
        # Handle latitude/longitude (coordinates) - simple float conversion
        COORDINATE_FIELDS = ['latitude', 'longitude']
        if field_name in COORDINATE_FIELDS:
            # For coordinates, just check for empty/invalid and convert to float
            if value is None or (isinstance(value, float) and math.isnan(value)):
                return None
            if isinstance(value, str):
                # Strip whitespace AND trailing commas (CSV formatting issue)
                cleaned = value.strip().rstrip(',').strip()
                if not cleaned or cleaned.upper() in ['N/A', '-', 'NULL']:
                    return None
                value = cleaned
            try:
                return str(float(value)) if value else None
            except (ValueError, TypeError):
                return None
        
        # Handle monetary fields (acquisition_cost) - needs currency symbol removal
        MONETARY_FIELDS = ['acquisition_cost']
        if field_name in MONETARY_FIELDS:
            # Check for non-string types (like Python's NaN if pandas read it that way)
            if value is None or (isinstance(value, float) and math.isnan(value)):
                return None
                
            if isinstance(value, str):
                # 1. Aggressively strip non-standard formatting, currency, and symbols.
                cleaned_value = value.strip().replace(',', '').replace('₱', '').replace('$', '').replace('(', '').replace(')', '')
            else:
                cleaned_value = str(value) 
            
            # 2. Check for invalid text or empty string after cleaning
            if not cleaned_value or cleaned_value.upper() in ['N/A', '-']:
                return None 
            
            # 3. Final conversion safety check: If it can't be Decimal, return None.
            try:
                # Attempt to create a Decimal instance (must succeed)
                Decimal(cleaned_value)
                return cleaned_value # Return the clean string for the field to process
            except Exception:
                # FIX: If we reach here, the input is garbage. Force the field to NULL.
                return None
            
        # Ensure any non-decimal blank values are set to None
        if isinstance(value, str) and value.strip() == '':
            return None
            
        return value
    
    
    def before_save_instance(self, instance, *args, **kwargs):
        """
        Checks for UNIQUE constraint violations only when creating a new record.
        """
        if not instance.pk:
            if Asset.objects.filter(property_number=instance.property_number).exists():
                raise IntegrityError(f"Property Number '{instance.property_number}' already exists in the database.")
        
        return super().before_save_instance(instance, *args, **kwargs)


    def skip_row(self, instance, original, row, import_validation_errors=None, **kwargs):
        """
        Skips rows where the mandatory 'date_acquired' or 'property_number' is missing or blank.
        """
        if not row.get('date_acquired'):
             return True
        
        if not row.get('property_number'):
            return True
            
        return super().skip_row(instance, original, row, import_validation_errors, **kwargs)

    
    def before_import_row(self, row, **kwargs):
        """
        Ensures the property_number follows the 'PAR-(number)' format.
        """
        property_number = row.get('property_number')
        
        if property_number:
            property_number = str(property_number).strip()
            
            if not property_number.upper().startswith('PAR-'):
                row['property_number'] = f"PAR-{property_number}"
            
        return row
    
    class Meta:
        model = Asset 
        
        fields = (
            'id',
            'property_number', 
            'name', 
            'acquisition_cost',
            'date_acquired', 
            'asset_class',
            'asset_nature',
            'status',
            'assigned_office',
            'accountable_firstname',
            'accountable_surname',
            'description',
            # latitude and longitude removed - can be added manually in admin if needed
        )
        
        import_id_fields = ('property_number',)
        skip_diff = True 
        export_order = fields
        
        import_from_legacy_system = True