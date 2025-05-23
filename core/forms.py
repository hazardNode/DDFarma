# core/forms.py
from django import forms
from allauth.account.forms import SignupForm
from core.models import Product, Supplier, Category, User, ProductImage
from allauth.account.forms import ResetPasswordKeyForm


# Custom widget for multiple file uploads
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

# Updated form with custom field
class MultipleImageUploadForm(forms.Form):
    images = MultipleFileField(
        label='Upload Images',
        required=False,
    )
    set_primary = forms.BooleanField(
        required=False,
        initial=False,
        label='Set first uploaded image as primary'
    )

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'category', 'stock_quantity', 'sku', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Product Name'}),
            'price': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
            'stock_quantity': forms.NumberInput(attrs={'placeholder': '0'}),
            'sku': forms.TextInput(attrs={'placeholder': 'SKU Code'}),
        }

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'is_primary']


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

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
        }


class CustomResetPasswordKeyForm(ResetPasswordKeyForm):
    """Custom form to handle debugging and add any customizations"""

    def clean(self):
        """Debug what's happening in the validation"""
        print(f"DEBUG: Form clean called with fields: {self.cleaned_data}")
        try:
            cleaned_data = super().clean()
            print(f"DEBUG: Parent clean succeeded: {cleaned_data}")
            return cleaned_data
        except Exception as e:
            print(f"DEBUG: Error in parent clean: {str(e)}")
            raise