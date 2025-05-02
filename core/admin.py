from django.contrib import admin
from django.utils.html import format_html
from .models import (
    User, Role, Category, Supplier, Product,
    Address, Order, OrderItem, Payment, ShippingMethod
)


# Helper functions
def format_price(amount):
    """Format decimal as price with dollar sign"""
    return f"${amount}"


def status_badge(status, status_text=None):
    """Generate a colored status badge"""
    colors = {
        'active': 'green',
        'inactive': 'red',
        'pending': 'yellow',
        'processing': 'blue',
        'shipped': 'blue',
        'delivered': 'green',
        'cancelled': 'red',
        'completed': 'green',
        'failed': 'red',
        'default': 'green',
        'non-default': 'gray',
    }
    text = status_text or status
    color = colors.get(status.lower(), 'gray')
    return format_html(
        '<span class="status-badge status-{}">{}</span>',
        color, text
    )


# Admin classes
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_name',)
    search_fields = ('role_name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'phone')
    search_fields = ('name', 'contact_email')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'display_price', 'category', 'stock_quantity', 'status')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'sku')

    def display_price(self, obj):
        return format_price(obj.price)

    display_price.short_description = 'Price'

    def status(self, obj):
        status_text = 'Active' if obj.is_active else 'Inactive'
        status_key = 'active' if obj.is_active else 'inactive'
        return status_badge(status_key, status_text)

    status.short_description = 'Status'


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'street', 'city', 'province', 'postal_code', 'default_status')
    list_filter = ('is_default', 'city', 'province')
    search_fields = ('user__email', 'street', 'city')

    def default_status(self, obj):
        status_key = 'default' if obj.is_default else 'non-default'
        status_text = 'Default' if obj.is_default else 'No'
        return status_badge(status_key, status_text)

    default_status.short_description = 'Default'


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    max_num = 3


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'status')
    list_filter = ('is_active', 'is_staff', 'role')
    search_fields = ('email', 'first_name', 'last_name')
    inlines = [AddressInline]

    def status(self, obj):
        status_text = 'Active' if obj.is_active else 'Inactive'
        status_key = 'active' if obj.is_active else 'inactive'
        return status_badge(status_key, status_text)

    status.short_description = 'Status'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'formatted_date', 'display_status', 'display_total')
    list_filter = ('status', 'order_date')
    search_fields = ('user__email', 'id')
    inlines = [OrderItemInline]
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']

    def formatted_date(self, obj):
        return obj.order_date.strftime('%Y-%m-%d %H:%M')

    formatted_date.short_description = 'Date'

    def display_total(self, obj):
        return format_price(obj.total_amount)

    display_total.short_description = 'Total'

    def display_status(self, obj):
        return status_badge(obj.status, obj.get_status_display())

    display_status.short_description = 'Status'

    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} orders marked as "Processing".')

    mark_as_processing.short_description = "Mark selected orders as Processing"

    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} orders marked as "Shipped".')

    mark_as_shipped.short_description = "Mark selected orders as Shipped"

    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} orders marked as "Delivered".')

    mark_as_delivered.short_description = "Mark selected orders as Delivered"

    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} orders marked as "Cancelled".')

    mark_as_cancelled.short_description = "Mark selected orders as Cancelled"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'display_price')
    list_filter = ('order__status',)
    search_fields = ('order__id', 'product__name')

    def display_price(self, obj):
        return format_price(obj.price_at_purchase)

    display_price.short_description = 'Price'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_method', 'display_amount', 'display_status', 'formatted_date')
    list_filter = ('status', 'payment_method')
    search_fields = ('order__id', 'transaction_id')

    def display_amount(self, obj):
        return format_price(obj.amount)

    display_amount.short_description = 'Amount'

    def display_status(self, obj):
        return status_badge(obj.status, obj.get_status_display())

    display_status.short_description = 'Status'

    def formatted_date(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')

    formatted_date.short_description = 'Date'


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_cost')
    search_fields = ('name',)

    def display_cost(self, obj):
        return format_price(obj.cost)

    display_cost.short_description = 'Cost'


# Register User model
admin.site.register(User, UserAdmin)