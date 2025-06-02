# core/middleware.py
from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.contrib import messages


class RoleBasedAccessMiddleware:
    """
    Middleware to control access to views based on user roles
    """

    def __init__(self, get_response):
        self.get_response = get_response

        # Admin-only URL name patterns
        self.admin_urls = [
            'management_dashboard',
            'product_list', 'product_create', 'product_update', 'product_delete',
            'category_list', 'category_create', 'category_update', 'category_delete',
            'order_list', 'order_detail',
            'user_list', 'user_update'
        ]

        # Authenticated-only URL name patterns (accessible by both CLIENT and ADMIN)
        self.authenticated_urls = [
            'order_history',
            # Add other URLs that require authentication
        ]

    def __call__(self, request):
        # Check if the current URL requires specific permissions
        url_name = resolve(request.path_info).url_name

        # For admin-only URLs
        if url_name in self.admin_urls:
            if not request.user.is_authenticated:
                messages.error(request, "Necesitas ingresar para acceder a esta página.")
                return redirect('account_login')

            # If user is authenticated but not an admin
            if not hasattr(request.user, 'role') or request.user.role is None or request.user.role.role_name != 'ADMIN':
                messages.error(request, "No tienes permiso para acceder a esta página.")
                return redirect('shop')

        # For authenticated-only URLs
        elif url_name in self.authenticated_urls:
            if not request.user.is_authenticated:
                messages.error(request, "Necesitas ingresar para acceder a esta página.")
                return redirect('account_login')

        return self.get_response(request)