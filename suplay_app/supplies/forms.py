from django import forms
from .models import Product, StockBatch

# --- PRODUCT FORM (For Add/Edit Product Page) ---
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # Added 'brand' to the fields list
        fields = ['name', 'category', 'brand', 'price', 'stock', 'item_code', 'supplier', 'description', 'image']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brand Name'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'item_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

# --- APR REQUEST FORM ---
from .models import APRRequest, Settlement

class APRRequestForm(forms.ModelForm):
    class Meta:
        model = APRRequest
        fields = ['apr_no', 'control_no', 'date_prepared', 'supplier', 'mode_of_delivery', 'insufficient_fund_action', 'remarks']
        widgets = {
            'apr_no': forms.TextInput(attrs={'class': 'form-control'}),
            'control_no': forms.TextInput(attrs={'class': 'form-control'}),
            'date_prepared': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'mode_of_delivery': forms.Select(attrs={'class': 'form-select'}),
            'insufficient_fund_action': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

# --- SETTLEMENT FORM ---
class SettlementForm(forms.ModelForm):
    class Meta:
        model = Settlement
        fields = ['settlement_type', 'order_id', 'is_settled', 'date_settled', 'reference_no', 'amount_paid', 'attachment', 'remarks']
        widgets = {
            'settlement_type': forms.Select(attrs={'class': 'form-select'}),
            'order_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_settled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'date_settled': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reference_no': forms.TextInput(attrs={'class': 'form-control'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

# --- STOCK BATCH FORM (For Incoming Deliveries) ---
class StockBatchForm(forms.ModelForm):
    class Meta:
        model = StockBatch
        fields = ['product', 'supplier_name', 'batch_number', 'quantity_initial', 'cost_per_item', 'date_received']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'supplier_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier Name'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DR / Invoice Number'}),
            'quantity_initial': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost_per_item': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'date_received': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }