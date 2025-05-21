# core/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


class Role(models.Model):
    role_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.role_name


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


# Add this to your models.py User class:

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Important for admin access
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def get_short_name(self):
        return self.first_name or self.email

# core/models.py (continued)
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stock_quantity = models.IntegerField(default=0)
    sku = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def primary_image(self):
        try:
            # Try to get the primary image
            primary_image = self.images.filter(is_primary=True).first()

            # If a primary image exists, return it
            if primary_image:
                return primary_image

            # Otherwise, return the first image (if any)
            return self.images.first()
        except Exception:
            # If any error occurs, return None
            return None

    '''def __str__(self):
        return f"{self.payment_method} Payment for Order {self.order.id}"'''

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        # If this is marked as primary, unmark all other primary images for this product
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)
        # If this is the first image for the product, make it primary
        elif not ProductImage.objects.filter(product=self.product).exists():
            self.is_primary = True
        super().save(*args, **kwargs)




class ShippingMethod(models.Model):
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    street = models.TextField()
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(
        max_length=5,
        validators=[RegexValidator(r'^\d{5}$', 'Enter a valid 5-digit postal code')]
    )
    phone = models.CharField(max_length=20, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'street', 'postal_code')
# Updated PaymentMethod model for SEPA support
# Replace the existing PaymentMethod model in models.py

class PaymentMethod(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('sepa_debit', 'Bank Account (SEPA)'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Stripe specific fields
    payment_method_id = models.CharField(max_length=100, unique=True)

    # Display information (not sensitive data)
    display_name = models.CharField(max_length=100)  # e.g., "Visa ending in 4242"

    # Additional metadata for display purposes
    expiry_month = models.CharField(max_length=2, blank=True, null=True)  # MM format
    expiry_year = models.CharField(max_length=4, blank=True, null=True)  # YYYY format
    card_brand = models.CharField(max_length=20, blank=True, null=True)  # Visa, Mastercard, etc.
    last4 = models.CharField(max_length=4, blank=True, null=True)  # Last 4 digits

    # Bank account specific display fields (no sensitive data)
    bank_name = models.CharField(max_length=100, blank=True, null=True)  # For bank accounts

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        # If this is marked as default, unmark all other default payment methods for this user
        if self.is_default:
            PaymentMethod.objects.filter(user=self.user, is_default=True).update(is_default=False)
        # If this is the first payment method for the user, make it default
        elif not PaymentMethod.objects.filter(user=self.user).exists():
            self.is_default = True
        super().save(*args, **kwargs)

    # Helper methods to generate display name based on payment type
    def set_card_details(self, brand, last4, exp_month, exp_year):
        """Set the display information for a card payment method"""
        self.card_brand = brand
        self.last4 = last4
        self.expiry_month = exp_month
        self.expiry_year = exp_year
        self.display_name = f"{brand} ending in {last4}"

    def set_bank_account_details(self, bank_name, last4):
        """Set the display information for a bank account payment method"""
        self.bank_name = bank_name
        self.last4 = last4
        self.display_name = f"{bank_name} ending in {last4}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='shipping_orders')
    billing_address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='billing_orders', null=True,
                                        blank=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)

    # Order information
    order_number = models.CharField(max_length=20, unique=True)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default='pending')

    # Financial information
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Stripe payment information
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_payment_method_id = models.CharField(max_length=100, blank=True, null=True)

    # Shipping information
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.SET_NULL, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)

    # Notes
    customer_notes = models.TextField(blank=True, null=True)
    internal_notes = models.TextField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order {self.order_number}"

    def get_absolute_url(self):
        return reverse('order_detail', args=[self.id])

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

    def generate_order_number(self):
        """Generate a unique order number."""
        import datetime
        import random
        date_str = datetime.date.today().strftime('%Y%m%d')
        random_num = random.randint(1000, 9999)
        return f"ORD-{date_str}-{random_num}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def calculate_totals(self):
        """Calculate order totals."""
        self.subtotal = sum(item.get_cost() for item in self.items.all())
        # Add shipping cost if not already set
        if not self.shipping_cost and self.shipping_method:
            self.shipping_cost = self.shipping_method.cost
        self.total_amount = self.subtotal + self.shipping_cost
        self.save()

    def set_paid(self, payment_intent_id=None):
        """Mark the order as paid."""
        self.payment_status = 'paid'
        if payment_intent_id:
            self.stripe_payment_intent_id = payment_intent_id
        self.status = 'processing'
        self.save()

    def mark_as_shipped(self, tracking_number=None):
        """Mark the order as shipped."""
        self.status = 'shipped'
        if tracking_number:
            self.tracking_number = tracking_number
        self.save()


# You already have an OrderItem model, but make sure it has these fields
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_cost(self):
        return self.price_at_purchase * self.quantity
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
# Add to core/models.py
class Receipt(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='receipt')
    receipt_number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    billing_name = models.CharField(max_length=255)
    billing_address = models.TextField()
    billing_city = models.CharField(max_length=100)
    billing_province = models.CharField(max_length=100)
    billing_postal_code = models.CharField(max_length=5)
    payment_method = models.CharField(max_length=50)
    payment_transaction_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Receipt #{self.receipt_number} for Order #{self.order.id}"

    def generate_receipt_number(self):
        """Generate a unique receipt number"""
        import datetime
        import uuid
        today = datetime.date.today()
        prefix = f"REC-{today.year}{today.month:02d}"
        random_suffix = str(uuid.uuid4()).split('-')[0].upper()
        return f"{prefix}-{random_suffix}"

    def save(self, *args, **kwargs):
        # Generate receipt number if not provided
        if not self.receipt_number:
            self.receipt_number = self.generate_receipt_number()
        super().save(*args, **kwargs)