from django import forms
from .models import Product, StockBatch, APRRequest, Settlement, Supplier, Category, Department, News

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'urgency', 'is_active', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Announcement Title'}),
            'content': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Global broadcast message...'}),
            'urgency': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'brand', 'item_code', 'category', 'supplier', 'description', 'price', 'unit', 'reorder_point', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'item_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., pc, box'}),
            'reorder_point': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class StockBatchForm(forms.ModelForm):
    class Meta:
        model = StockBatch
        fields = ['product', 'supplier_name', 'batch_number', 'quantity_initial', 'cost_per_item', 'date_received', 'apr_reference']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'date_received': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'supplier_name': forms.TextInput(attrs={'class': 'form-control'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity_initial': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost_per_item': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'apr_reference': forms.Select(attrs={'class': 'form-select'}),
        }

class APRRequestForm(forms.ModelForm):
    class Meta:
        model = APRRequest
        fields = ['apr_no', 'control_no', 'supplier', 'mode_of_delivery', 'insufficient_fund_action', 'total_amount', 'remarks']
        widgets = {
            'apr_no': forms.TextInput(attrs={'class': 'form-control'}),
            'control_no': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'mode_of_delivery': forms.Select(attrs={'class': 'form-select'}),
            'insufficient_fund_action': forms.Select(attrs={'class': 'form-select'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

class SettlementForm(forms.ModelForm):
    class Meta:
        model = Settlement
        fields = ['settlement_type', 'order_id', 'reference_no', 'amount_paid', 'attachment', 'remarks']
        widgets = {
            'settlement_type': forms.Select(attrs={'class': 'form-select'}),
            'order_id': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Order/APR ID'}),
            'reference_no': forms.TextInput(attrs={'class': 'form-control'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'is_ps_dbm']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_ps_dbm': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }