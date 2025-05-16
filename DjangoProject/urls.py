from allauth.account.views import SignupView
# your_project/urls.py (main project file)
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from core.views import account_dashboard, update_profile, email_management, email_verification_sent, verify_email, CustomConfirmEmailView


class CustomSignupView(SignupView):
    template_name = 'account/signup.html'


urlpatterns = [
    # Admin interface
    #path('admin/', admin.site.urls),

    # Authentication URLs (login/logout/password reset)
    path('account/profile/', account_dashboard, name='account_dashboard'),

    path('account/signup/', CustomSignupView.as_view(), name='account_signup'),

    path('account/', include('allauth.urls')),

    path('account/update-profile/', update_profile, name='update_profile'),
    re_path(r"^confirm-email/(?P<key>[-:\w]+)/$",CustomConfirmEmailView.as_view(),name="account_confirm_email",),
    #path("confirm-email/", email_verification_sent,name="account_email_verification_sent",),
    path('account/email/', email_management, name='account_email'),
    path('account/email/verification-sent/', email_verification_sent, name='account_email_verification_sent'),
    path('account/email/verify/<uidb64>/<token>/', verify_email, name='account_email_verify'),

    # Your app's URLs
    path('', include('core.urls')),  # Include your app's URLs at root level
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)