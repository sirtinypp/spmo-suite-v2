# gamit-core/urls.py

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views 
from django.views.decorators.csrf import csrf_exempt # Import the CSRF wrapper
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.http import HttpResponseForbidden

def impersonate_user(request, username):
    if not request.user.is_authenticated or request.user.username != 'grootadmin':
        return HttpResponseForbidden("Access Denied: Only grootadmin can impersonate users.")
    
    try:
        user = User.objects.get(username=username)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('dashboard')
    except User.DoesNotExist:
        return HttpResponseForbidden(f"User {username} does not exist.")


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

    # 5.5 Impersonate User (grootadmin only)
    path('impersonate-user/<str:username>/', impersonate_user, name='impersonate_user'),


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
