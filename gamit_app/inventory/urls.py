# inventory/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    # --- AUTHENTICATION ---
    path('login/', auth_views.LoginView.as_view(template_name='inventory/login.html'), name='login'),
    path('logout/', csrf_exempt(auth_views.LogoutView.as_view()), name='logout'),

    # --- DASHBOARD & ASSETS ---
    path('dashboard/', views.dashboard, name='dashboard'),
    path('assets/', views.asset_list, name='asset_list'),
    path('asset/<int:pk>/', views.asset_detail, name='asset_detail'),
    path('sitemap/', views.sitemap, name='sitemap'),
    
    # --- SERVICE LOGS ---
    path('asset/<int:pk>/add-log/', views.add_service_log, name='add_service_log'),
    path('asset/<int:pk>/print-log/', views.print_service_log, name='print_service_log'),
    path('service-log/<int:pk>/delete/', views.delete_service_log, name='delete_service_log'), # <--- ADDED THIS LINE

    # --- TRANSACTION CREATION (User Actions) ---
    path('transaction/add/', views.add_asset_transaction, name='add_asset_transaction'), 
    path('transaction/request/', views.create_inspection_request, name='create_inspection_request'), 
    path('transaction/batch/', views.create_batch_request, name='create_batch_request'), 
    path('transaction/transfer/', views.create_transfer_request, name='create_transfer_request'),

    # --- TRANSACTION HISTORY & MANAGEMENT ---
    path('transactions/history/', views.transaction_history, name='transaction_history'), 
    
    # --- STATUS UPDATES (Admin Actions) ---
    path('transaction/<int:pk>/status/<str:action>/', views.update_request_status, name='update_request_status'),
    path('transaction/batch/<int:pk>/status/<str:action>/', views.update_batch_status, name='update_batch_status'),
    path('transaction/transfer/<int:pk>/status/<str:action>/', views.update_transfer_status, name='update_transfer_status'),
    
    # --- BATCH PROCESSING & PRINTING ---
    path('transaction/batch/<int:pk>/process/', views.process_batch_admin, name='process_batch_admin'),
    path('transaction/batch/<int:pk>/print/', views.print_acceptance_report, name='print_acceptance_report'),
    path('transaction/batch/<int:pk>/print-par/', views.print_par, name='print_par'),

    # --- API HELPERS ---
    path('api/asset-info/<int:asset_id>/', views.get_asset_info, name='get_asset_info'),
]