# core/forms.py
from django import forms
from allauth.account.forms import SignupForm
from core.models import Product, Supplier, Category, User


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'price',
            'category',
            'stock_quantity',
            'sku',
            'is_active',
            'image'
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

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role']  # Include editable fields
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'}),
            'first_name': forms.TextInput(attrs={'class': 'mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'}),
            'last_name': forms.TextInput(attrs={'class': 'mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'}),
            'role': forms.Select(attrs={'class': 'mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already in use.")
        return email
