from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

# !!! CHANGED: Import from the current folder (.)
from . import views 

urlpatterns = [
    # Public Landing Page
    path('', views.home, name='home'),
    path('news/archive/', views.NewsArchiveView.as_view(), name='news_archive'),

    # Login Page (We will create this template next)
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    
    # Logout Action
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Internal Dashboard
    path('dashboard/', views.admin_portal, name='dashboard'),
    
    path('admin/', admin.site.urls),]

    

# ... existing urlpatterns ...

# Add this snippet at the end
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
