# gamit-core/urls.py

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views 
from django.views.decorators.csrf import csrf_exempt # Import the CSRF wrapper

urlpatterns = [
    # 1. Admin Panel
    path('admin/', admin.site.urls),

    # 2. Custom Login View (Standard setup)
    path('login/', auth_views.LoginView.as_view(template_name='inventory/login.html'), name='login'),

    # 3. Logout View (FIXED: Wrapped in csrf_exempt to bypass stale token checks)
    path('logout/', csrf_exempt(auth_views.LogoutView.as_view(next_page='/login/?next=/dashboard/')), name='logout'),

    # 4. Inventory App URLs
    path('', include('inventory.urls')),

    # 5. Root Redirect
    path('', RedirectView.as_view(url='dashboard/', permanent=False)),

    # 6. Google SSO (django-allauth)
    path('sso/', include('allauth.urls')),
]

# Serve media files regardless of DEBUG setting
# static() returns empty list when DEBUG=False; re_path+serve always works.
from django.urls import re_path
from django.views.static import serve
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
