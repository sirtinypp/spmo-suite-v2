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