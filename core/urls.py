# core/urls.py
from django.urls import path

from core import views

urlpatterns = [
    # Management Dashboard
    path('management/', views.management_dashboard, name='management_dashboard'),
    # Products
    path('management/products/', views.product_list, name='product_list'),
    path('management/products/new/', views.product_create, name='product_create'),
    path('management/products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('management/products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # Categories
    path('management/categories/', views.category_list, name='category_list'),
    path('management/categories/new/', views.category_create, name='category_create'),
    path('management/categories/<int:pk>/edit/', views.category_update, name='category_update'),
    path('management/categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Orders
    path('management/orders/', views.order_list, name='order_list'),
    path('management/orders/<int:pk>/detail/', views.order_detail, name='order_detail'),

    # Users
    path('management/users/', views.user_list, name='user_list'),
    path('management/users/<int:pk>/edit/', views.user_update, name='user_update'),
    path('account/orders/', views.order_history, name='order_history'),
    path('', views.landing_page, name='landing_page'),
    path('shop/', views.shop, name='shop'),
]