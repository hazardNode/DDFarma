# core/urls.py
from django.urls import path
from core import views, receipts

from django.http import HttpResponse
from core.models import ProductImage

urlpatterns = [
    # Management Dashboard
    path('management/', views.management_dashboard, name='management_dashboard'),

    # Products
    path('management/products/', views.product_list, name='product_list'),
    path('management/products/new/', views.product_create, name='product_create'),
    path('management/products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('management/products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('management/products/<int:pk>/set-primary/<int:image_id>/', views.set_primary_image, name='set_primary_image'),
    path('management/products/<int:pk>/delete-image/<int:image_id>/', views.delete_image, name='delete_image'),

    # Categories
    path('management/categories/', views.category_list, name='category_list'),
    path('management/categories/new/', views.category_create, name='category_create'),
    path('management/categories/<int:pk>/edit/', views.category_update, name='category_update'),
    path('management/categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Orders
    path('management/orders/', views.order_list, name='order_list'),
    path('management/orders/<int:pk>/detail/', views.order_detail, name='order_detail'),
    path('management/orders/<int:order_id>/receipt/', receipts.download_receipt, name='admin_download_receipt'),
    path('management/receipts/bulk/', receipts.bulk_download_receipts, name='bulk_download_receipts'),

    # Users
    path('management/users/', views.user_list, name='user_list'),
    path('management/users/<int:pk>/edit/', views.user_update, name='user_update'),
    path('account/orders/', views.order_history, name='order_history'),
    path('account/orders/<int:order_id>/receipt/', receipts.download_receipt, name='user_download_receipt'),

    # Address Management
    path('account/addresses/', views.address_management, name='address_management'),
    path('account/addresses/create/', views.address_create, name='address_create'),
    path('account/addresses/<int:address_id>/', views.address_detail, name='address_detail'),
    path('account/addresses/<int:address_id>/update/', views.address_update, name='address_update'),
    path('account/addresses/<int:address_id>/delete/', views.address_delete, name='address_delete'),
    path('account/addresses/<int:address_id>/default/', views.address_set_default, name='address_set_default'),

    # Payment Management
    path('account/payments/', views.payment_management, name='payment_management'),
    path('account/payments/create/', views.payment_create, name='payment_create'),
    path('account/payments/<int:payment_id>/delete/', views.payment_delete, name='payment_delete'),
    path('account/payments/<int:payment_id>/default/', views.payment_set_default, name='payment_set_default'),

    # Main site
    path('', views.landing_page, name='landing_page'),
    path('shop/', views.shop, name='shop'),
    path('shop/<int:product_id>/', views.product_detail, name='product_detail'),

    # Cart URLs
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/update-ajax/', views.cart_update_ajax, name='cart_update_ajax'),
    path('cart/count/', views.get_cart_count, name='get_cart_count'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),

    # Checkout related URLs
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/address-save/', views.checkout_address_save, name='checkout_address_save'),
    path('checkout/payment/', views.checkout_payment, name='checkout_payment'),
    path('checkout/create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('checkout/complete/', views.checkout_complete, name='checkout_complete'),
    path('orders/<int:order_id>/confirmation/', views.order_confirmation, name='order_confirmation'),

    # SECURE MEDIA SERVING URLs - Replace direct media access
    # Debug view (remove this after testing)
    path('debug-image/<int:image_id>/', views.debug_product_image, name='debug_product_image'),

    # Secure media files (with authentication/permission checks)
    path('secure-media/<path:file_path>/', views.serve_media, name='secure_media'),

    # Public product images (no authentication required for shop display)
    path('product-image/<int:image_id>/', views.serve_product_image, name='product_image'),
    path('faq/', views.faq, name='faq'),
    path('acerca-de/', views.about_us, name='about_us'),
]

