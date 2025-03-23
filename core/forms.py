# core/forms.py
from django import forms
from core.models import Product, Supplier, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'price',
            'category',
            'stock_quantity',
            'sku',
            'is_active'
        ]
        widgets = {
            'sku': forms.TextInput(attrs={'placeholder': 'e.g. INTOL-001'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional: Add form field styling or custom validation
        self.fields['sku'].required = True

    # core/forms.py (continued)
    class SupplierForm(forms.ModelForm):
        class Meta:
            model = Supplier
            fields = ['name', 'contact_email', 'phone']

    class CategoryForm(forms.ModelForm):
        class Meta:
            model = Category
            fields = ['name']
