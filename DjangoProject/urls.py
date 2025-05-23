# Update your main urls.py file

from allauth.account.views import SignupView
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from core.views import (
    account_dashboard, update_profile, email_management,
    email_verification_sent, verify_email, CustomConfirmEmailView,
    CustomPasswordResetView, CustomPasswordResetFromKeyView, SimplePasswordResetFromKeyView,
)


class CustomSignupView(SignupView):
    template_name = 'account/signup.html'


# Create a view that blocks access to certain URLs
def blocked_view(request, *args, **kwargs):
    """Redirect blocked URLs to landing page with message"""
    messages.warning(request, "Sorry, that page is not available. You've been redirected to the home page.")
    return redirect('landing_page')


# Make password reset require authentication
@method_decorator(login_required, name='dispatch')
class AuthenticatedPasswordResetView(CustomPasswordResetView):
    """Password reset view that requires authentication"""
    pass


urlpatterns = [
    # Admin interface
    # path('admin/', admin.site.urls),

    # Block specific allauth URLs by overriding them BEFORE including allauth.urls
    path('account/logout/', blocked_view, name='account_logout'),
    path('account/password/reset/done/', blocked_view, name='account_reset_password_done'),
    path('account/password/reset/key/done/', blocked_view, name='account_reset_password_from_key_done'),
    path('account/confirm-email/', blocked_view, name='account_confirm_email_sent'),
    path('account/inactive/', blocked_view, name='account_inactive'),

    # Custom views - these override the default allauth ones
    path('account/signup/', CustomSignupView.as_view(), name='account_signup'),
    path('account/password/reset/', AuthenticatedPasswordResetView.as_view(), name='account_reset_password'),

    # Custom password reset from key
    re_path(r"^account/password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
            SimplePasswordResetFromKeyView.as_view(),
            name="account_reset_password_from_key"),

    # Authentication URLs (login/logout/password reset)
    path('account/profile/', account_dashboard, name='account_dashboard'),

    # Custom email confirmation
    re_path(r"^confirm-email/(?P<key>[-:\w]+)/$", CustomConfirmEmailView.as_view(), name="account_confirm_email"),

    # Custom profile and email management
    path('account/update-profile/', update_profile, name='update_profile'),
    path('account/email/', email_management, name='account_email'),
    path('account/email/verification-sent/', email_verification_sent, name='account_email_verification_sent'),
    path('account/email/verify/<uidb64>/<token>/', verify_email, name='account_email_verify'),

    # Allauth URLs - this handles everything else (the blocked URLs above will override the defaults)
    path('account/', include('allauth.urls')),

    # Your app's URLs
    path('', include('core.urls')),  # Include your app's URLs at root level
]

# Custom error handlers (these work when DEBUG=False)
handler404 = 'core.error_handlers.handler404'
handler403 = 'core.error_handlers.handler403'
handler500 = 'core.error_handlers.handler500'
handler400 = 'core.error_handlers.handler400'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)