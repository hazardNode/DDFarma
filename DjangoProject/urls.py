from allauth.account.views import SignupView
# your_project/urls.py (main project file)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import account_dashboard, update_profile


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

    # Your app's URLs
    path('', include('core.urls')),  # Include your app's URLs at root level
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)