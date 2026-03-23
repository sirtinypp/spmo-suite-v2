# inventory/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    # --- AUTHENTICATION ---
    path('login/', auth_views.LoginView.as_view(template_name='inventory/login.html'), name='login'),
    path('logout/', csrf_exempt(auth_views.LogoutView.as_view(next_page='login')), name='logout'),

    # --- DASHBOARD & ASSETS ---
    path('dashboard/', views.dashboard, name='dashboard'),
    path('assets/', views.asset_list, name='asset_list'),
    path('asset/<int:pk>/', views.asset_detail, name='asset_detail'),
    path('sitemap/', views.sitemap, name='sitemap'),
    
    # --- SERVICE LOGS ---
    path('asset/<int:pk>/add-log/', views.add_service_log, name='add_service_log'),
    path('asset/<int:pk>/print-log/', views.print_service_log, name='print_service_log'),
    path('asset/<int:pk>/print-card/', views.print_property_card, name='print_property_card'),
    path('service-log/<int:pk>/delete/', views.delete_service_log, name='delete_service_log'), # <--- ADDED THIS LINE

    # --- TRANSACTION CREATION (User Actions) ---
    path('assets/add/', views.add_asset_transaction, name='add_asset'),
    path('transaction/add/', views.add_asset_transaction, name='add_asset_transaction'),  # Legacy alias
    path('transaction/request/', views.create_inspection_request, name='create_inspection_request'), 
    path('transaction/batch/', views.create_batch_request, name='create_batch_request'), 
    path('transaction/transfer/', views.create_transfer_request, name='create_transfer_request'),
    path('transaction/return/', views.create_return_request, name='create_return_request'),
    path('transaction/loss/', views.create_loss_report, name='create_loss_report'),
    path('transaction/clearance/', views.create_clearance_request, name='create_clearance_request'),

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
    path('transaction/batch/<int:pk>/print-par-v2/', views.print_par_v2, name='print_par_v2'),

    # --- ADMINISTRATION ---
    path('administration/activity-log/', views.activity_log, name='activity_log'),

    # --- WORKFLOW ---
    path('profile/signature/', views.upload_signature, name='upload_signature'),
    path('batch/<int:pk>/', views.batch_detail, name='batch_detail'),
    path('batch/<int:pk>/workflow/<str:target_state>/', views.approve_batch_workflow, name='approve_batch_workflow'),
    path('return/<int:pk>/', views.return_detail, name='return_detail'),
    path('return/<int:pk>/workflow/<str:target_state>/', views.approve_return_workflow, name='approve_return_workflow'),
    path('loss/<int:pk>/', views.loss_detail, name='loss_detail'),
    path('loss/<int:pk>/workflow/<str:target_state>/', views.approve_loss_workflow, name='approve_loss_workflow'),
    path('clearance/<int:pk>/', views.clearance_detail, name='clearance_detail'),
    path('clearance/<int:pk>/workflow/<str:target_state>/', views.approve_clearance_workflow, name='approve_clearance_workflow'),

    # --- API HELPERS ---
    path('api/asset-info/<int:asset_id>/', views.get_asset_info, name='get_asset_info'),
]