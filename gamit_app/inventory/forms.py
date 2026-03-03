from django import forms
from django.forms import inlineformset_factory

# Updated Imports to include ServiceLog
from .models import Asset, InspectionRequest, AssetBatch, AssetTransferRequest, BatchItem, ServiceLog

# ==========================================
# 1. ASSET FORM (Admin/Staff)
# ==========================================
class AssetTransactionForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values(): field.widget.attrs.update({'class': 'form-control'})

# ==========================================
# 2. INSPECTION REQUEST FORM
# ==========================================
class InspectionRequestForm(forms.ModelForm):
    class Meta:
        model = InspectionRequest
        fields = ['asset', 'notes', 'document_1', 'document_2']
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user and not user.is_staff and hasattr(user, 'userprofile'):
            try: self.fields['asset'].queryset = Asset.objects.filter(assigned_office__iexact=user.userprofile.office)
            except: pass
        for field in self.fields.values(): field.widget.attrs.update({'class': 'form-control'})

# ==========================================
# 3. BATCH FORM (User View)
# ==========================================
class AssetBatchForm(forms.ModelForm):
    # Dummy field for display only (since model auto-adds date)
    date_created = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control bg-light', 'readonly': 'readonly'})
    )

    class Meta:
        model = AssetBatch
        fields = [
            'requesting_unit', # Read-only
            'supplier_name', 
            'po_number', 
            'sales_invoice_number', 
            'acceptance_report_number',
            'remarks', 
            # Doc 1 & 2 are REQUIRED for AO
            'doc_1_file', 
            'doc_2_file',
            'doc_3_file',
            # doc_4 and doc_5 hidden/unused for now
        ]
        widgets = {
            # 1. AUTO / READ-ONLY FIELDS
            'requesting_unit': forms.TextInput(attrs={
                'class': 'form-control bg-light', 
                'readonly': 'readonly',
                'placeholder': 'Auto-generated'
            }),

            # 2. DETAILS
            'supplier_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier Name'}),
            'po_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PO Number'}),
            'sales_invoice_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Invoice No.'}),
            'acceptance_report_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IAR No.'}),

            'remarks': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Justification / Purpose of acquisition...'}),
            
            # 3. DOCUMENTS
            # Doc 1: PO
            'doc_1_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.png'}),
            # Doc 2: PR
            'doc_2_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.png'}),
            # Doc 3: Optional
            'doc_3_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.png'}),
        }
        labels = {
            'doc_1_file': 'Purchase Order (Required)',
            'doc_2_file': 'Purchase Request (Required)',
            'doc_3_file': 'Additional Document (Optional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make Doc 1 & 2 Required
        self.fields['doc_1_file'].required = True
        self.fields['doc_2_file'].required = True
        self.fields['doc_3_file'].required = False

# ==========================================
# 4. TRANSFER REQUEST FORM
# ==========================================
class AssetTransferRequestForm(forms.ModelForm):
    class Meta:
        model = AssetTransferRequest
        fields = [
            'asset', 
            'new_officer_firstname', 'new_officer_surname',
            'remarks', 'document_1', 'document_2'
        ]
        widgets = {
            # 'id_asset_select' is used by JS to fetch current officer info
            'asset': forms.Select(attrs={'class': 'form-select', 'id': 'id_asset_select'}),
            'new_officer_firstname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'new_officer_surname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Surname'}),
            'remarks': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Reason for transfer...'}),
            'document_1': forms.FileInput(attrs={'class': 'form-control'}), # Transfer Form
            'document_2': forms.FileInput(attrs={'class': 'form-control'}), # ID
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter assets: Users only see assets in their office
        if user and not user.is_staff and hasattr(user, 'userprofile'):
            self.fields['asset'].queryset = Asset.objects.filter(assigned_office__iexact=user.userprofile.office)

# ==========================================
# 5. ADMIN BATCH PROCESS FORM
# ==========================================
class AdminBatchProcessForm(forms.ModelForm):
    class Meta:
        model = AssetBatch
        fields = [
            'supplier_name', 'po_number', 'sales_invoice_number', 
            'requesting_unit', 'acceptance_report_number', 
            'fund_cluster', 'ups_dv_number', 
            'remarks'
        ]
        widgets = {
            'supplier_name': forms.TextInput(attrs={'class': 'form-control'}),
            'po_number': forms.TextInput(attrs={'class': 'form-control'}),
            'sales_invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
            'requesting_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'acceptance_report_number': forms.TextInput(attrs={'class': 'form-control fw-bold border-success'}),
            
            'fund_cluster': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fund Cluster'}),
            'ups_dv_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UPS DV No.'}),
            
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

# ==========================================
# 6. BATCH ITEM FORMSET
# ==========================================
class BatchItemForm(forms.ModelForm):
    class Meta:
        model = BatchItem
        fields = ['unit', 'quantity', 'image', 'description', 'nature_of_expense', 'reference_number', 'amount']
        widgets = {
            'unit': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Unit'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Qty'}),
            'image': forms.FileInput(attrs={'class': 'form-control form-control-sm', 'accept': 'image/*'}),
            'description': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Item Description'}),
            'nature_of_expense': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Expense Nature'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Ref No.'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Amount'}),
        }

BatchItemFormSet = inlineformset_factory(
    AssetBatch, BatchItem, form=BatchItemForm,
    extra=1, can_delete=True
)

# ==========================================
# 7. SERVICE LOG FORM (NEW)
# ==========================================
class ServiceLogForm(forms.ModelForm):
    class Meta:
        model = ServiceLog
        fields = ['service_date', 'service_type', 'service_provider', 'cost', 'next_service_date', 'description', 'service_document']
        widgets = {
            'service_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'service_type': forms.Select(attrs={'class': 'form-select'}),
            'service_provider': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Technician/Company Name'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'next_service_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Details of work done...'}),
            'service_document': forms.FileInput(attrs={'class': 'form-control'}),
        }

# ==========================================
# 8. USER SIGNATURE FORM (NEW)
# ==========================================
from .models import UserSignature

class UserSignatureForm(forms.ModelForm):
    class Meta:
        model = UserSignature
        fields = ['position_title', 'signature_image']
        widgets = {
            'position_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Administrative Officer V'}),
            'signature_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/png'}),
        }
        help_texts = {
            'signature_image': 'Upload a clear PNG image of your signature on a transparent background.'
        }

# ==========================================
# 9. TAB-SPECIFIC ASSET FORMS (NEW — Phase 5)
# ==========================================

class PropertyTabForm(forms.ModelForm):
    """Fields editable by SPMO Admin: basic property info, classification, accountability."""
    class Meta:
        model = Asset
        fields = [
            'property_number', 'name', 'description', 'status',
            'date_acquired', 'acquisition_cost',
            'asset_class', 'asset_nature',
            'assigned_office', 'accountable_firstname', 'accountable_middle_initial', 'accountable_surname',
        ]
        widgets = {
            'date_acquired': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get('class', '')
            if 'form-select' not in css:
                field.widget.attrs['class'] = 'form-control' + (' ' + css if css else '')

class FinanceTabForm(forms.ModelForm):
    """Fields editable by Accounting Admin: depreciation, valuation."""
    class Meta:
        model = Asset
        fields = [
            'fair_market_value', 'salvage_value', 'useful_life_years',
            'depreciation_method', 'accumulated_depreciation', 'depreciation_start_date',
        ]
        widgets = {
            'depreciation_start_date': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get('class', '')
            if 'form-select' not in css:
                field.widget.attrs['class'] = 'form-control' + (' ' + css if css else '')

class LifecycleTabForm(forms.ModelForm):
    """Fields editable by SPMO Admin: warranty, insurance, disposal."""
    class Meta:
        model = Asset
        fields = [
            'warranty_expiry', 'insurance_value',
            'disposal_date', 'disposal_method', 'disposal_proceeds',
        ]
        widgets = {
            'warranty_expiry': forms.DateInput(attrs={'type': 'date'}),
            'disposal_date': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get('class', '')
            if 'form-select' not in css:
                field.widget.attrs['class'] = 'form-control' + (' ' + css if css else '')

class GovernmentTabForm(forms.ModelForm):
    """Fields editable by SPMO Admin: COA codes, fund source, appraisal."""
    class Meta:
        model = Asset
        fields = [
            'uacs_object_code', 'fund_source', 'property_classification',
            'appraisal_date', 'appraised_value',
        ]
        widgets = {
            'appraisal_date': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get('class', '')
            if 'form-select' not in css:
                field.widget.attrs['class'] = 'form-control' + (' ' + css if css else '')