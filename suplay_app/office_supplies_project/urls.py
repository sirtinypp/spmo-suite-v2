from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # This line tells Django to look inside supplies/urls.py for ALL other paths
    path('', include('supplies.urls')),

    # Google SSO (django-allauth) — uses /sso/ to avoid conflict with /accounts/login/
    path('sso/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)