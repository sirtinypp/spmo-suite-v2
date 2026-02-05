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
            'doc_1_name', 'doc_1_file',
            'doc_2_name', 'doc_2_file',
            'doc_3_name', 'doc_3_file',
            'doc_4_name', 'doc_4_file',
            'doc_5_name', 'doc_5_file'
        ]
        widgets = {
            # 1. AUTO / READ-ONLY FIELDS
            'requesting_unit': forms.TextInput(attrs={
                'class': 'form-control bg-light', 
                'readonly': 'readonly',
                'placeholder': 'Auto-generated'
            }),

            # 2. NEW TEXT INPUTS
            'supplier_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier Name'}),
            'po_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PO Number'}),
            'sales_invoice_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Invoice No.'}),
            'acceptance_report_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IAR No.'}),

            # 3. EXISTING FIELDS
            'remarks': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Purpose of acquisition...'}),
            'doc_1_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Doc 1 Name'}),
            'doc_1_file': forms.FileInput(attrs={'class': 'form-control'}),
            'doc_2_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Doc 2 Name'}),
            'doc_2_file': forms.FileInput(attrs={'class': 'form-control'}),
            'doc_3_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Doc 3 Name'}),
            'doc_3_file': forms.FileInput(attrs={'class': 'form-control'}),
            'doc_4_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Doc 4 Name'}),
            'doc_4_file': forms.FileInput(attrs={'class': 'form-control'}),
            'doc_5_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Doc 5 Name'}),
            'doc_5_file': forms.FileInput(attrs={'class': 'form-control'}),
        }

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