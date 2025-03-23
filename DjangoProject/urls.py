
# your_project/urls.py (main project file)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),

    # Authentication URLs (login/logout/password reset)
    path('accounts/', include('django.contrib.auth.urls')),

    # Your app's URLs
    path('', include('core.urls')),  # Include your app's URLs at root level
]