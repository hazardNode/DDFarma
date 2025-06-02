# core/forms.py
from django import forms
from allauth.account.forms import SignupForm
from core.models import Product, Supplier, Category, User, ProductImage
from allauth.account.forms import ResetPasswordKeyForm
from .validators import validate_image, validate_multiple_images


# Custom widget for multiple file uploads with validation
class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        # Set default attributes for multiple file selection
        default_attrs = {
            'multiple': True,
            'accept': 'image/jpeg,image/jpg,image/png,image/gif,image/webp,image/bmp,image/tiff'
        }
        default_attrs.update(attrs)
        super().__init__(default_attrs)


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)
        # Add our custom validator
        self.validators.append(validate_multiple_images)

    # WITH THIS FIXED VERSION:
    def clean(self, data, initial=None):
        # Handle the case where no files are uploaded
        if not data:
            return []

        # Convert single file to list for consistent processing
        if not isinstance(data, (list, tuple)):
            files = [data] if data else []
        else:
            files = [f for f in data if f]  # Filter out empty files

        # Check file count limit
        if len(files) > 5:
            raise forms.ValidationError(
                f'Demasiados archivos seleccionados. Máximo permitido: 5, seleccionados: {len(files)}'
            )

        # Validate each file individually
        cleaned_files = []
        for i, file in enumerate(files):
            try:
                cleaned_file = super().clean(file, initial)
                if cleaned_file:
                    cleaned_files.append(cleaned_file)
            except forms.ValidationError as e:
                # Extract the error message properly
                error_msg = str(e) if hasattr(e, 'message') else str(e)
                raise forms.ValidationError(f'Archivo {i + 1}: {error_msg}')

        return cleaned_files


# Updated form with enhanced validation
class MultipleImageUploadForm(forms.Form):
    images = MultipleFileField(
        label='Añadir Imágenes (Máx 5)',
        required=False,
        help_text='Selecciona hasta 5 imágenes (JPEG, PNG, GIF, WebP, BMP, TIFF). Máx 10MB cada una.'
        # Note: No widget specified - uses the default MultipleFileInput from MultipleFileField
    )
    set_primary = forms.BooleanField(
        required=False,
        initial=False,
        label='Establecer la primera imagen como principal',
        help_text='Marque esta casilla para que la primera imagen cargada sea la imagen principal del producto.'
    )

    def clean_images(self):
        images = self.cleaned_data.get('images')
        if images:
            # Additional validation at form level
            if isinstance(images, list):
                if len(images) > 5:
                    raise forms.ValidationError('Máximo 5 imágenes por subida')

                # Check total size
                total_size = sum(img.size for img in images if img)
                max_total_size = 50 * 1024 * 1024  # 50MB total
                if total_size > max_total_size:
                    raise forms.ValidationError(
                        f'El tamaño total de archivos ({total_size / (1024 * 1024):.1f}MB) excede el '
                        f'máximo permitido ({max_total_size / (1024 * 1024):.0f}MB)'
                    )
        return images


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'category', 'stock_quantity', 'sku', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Nombre del Producto'}),
            'price': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01', 'min': '0.01', 'max': '1000'}),
            'stock_quantity': forms.NumberInput(attrs={'placeholder': '0', 'min': '1', 'max': '1000'}),
            'sku': forms.TextInput(attrs={'placeholder': 'Código SKU'}),
        }

    def clean_price(self):
        """Validate that price is between 0.01 and 1000"""
        price = self.cleaned_data.get('price')

        if price is not None:
            if price <= 0:
                raise forms.ValidationError('El precio debe ser mayor que 0.')
            if price > 1000:
                raise forms.ValidationError('El precio no puede ser mayor que 1000.')

        return price

    def clean_stock_quantity(self):
        """Validate that stock quantity is between 1 and 1000"""
        stock_quantity = self.cleaned_data.get('stock_quantity')

        if stock_quantity is not None:
            if stock_quantity <= 0:
                raise forms.ValidationError('El stock no puede ser menor que 1.')
            if stock_quantity > 1000:
                raise forms.ValidationError('El stock no puede ser mayor que 1000.')

        return stock_quantity


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'is_primary']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add image validation to the image field
        self.fields['image'].validators.append(validate_image)
        self.fields['image'].widget.attrs.update({
            'accept': 'image/jpeg,image/jpg,image/png,image/gif,image/webp,image/bmp,image/tiff'
        })

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
            'email': forms.EmailInput(attrs={
                'class': 'mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'}),
            'first_name': forms.TextInput(attrs={
                'class': 'mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'}),
            'last_name': forms.TextInput(attrs={
                'class': 'mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'}),
            'role': forms.Select(attrs={
                'class': 'mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este correo electrónico ya está en uso.")
        return email


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
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