# core/urls.py
from django.urls import path

from core import views, receipts

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

    path('', views.landing_page, name='landing_page'),
    path('shop/', views.shop, name='shop'),
    path('shop/<int:product_id>/', views.product_detail, name='product_detail'),

    # Cart URLs
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/update-ajax/', views.cart_update_ajax, name='cart_update_ajax'),
    path('cart/count/', views.get_cart_count, name='get_cart_count'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),

]