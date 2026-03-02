from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    # This line tells Django to look inside supplies/urls.py for ALL other paths
    path('', include('supplies.urls')),

    # Google SSO (django-allauth) — uses /sso/ to avoid conflict with /accounts/login/
    path('sso/', include('allauth.urls')),
]

# Serve media files (product images, order docs, etc.)
# Note: static() only works with DEBUG=True; re_path+serve works always.
# All environments use runserver (not gunicorn), so this is safe.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]