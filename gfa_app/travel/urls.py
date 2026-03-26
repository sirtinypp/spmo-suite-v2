from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # --- AUTHENTICATION ---
    path('login/', auth_views.LoginView.as_view(template_name='travel/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),

    # --- APP VIEWS ---
    path('', views.index, name='index'),
    path('book/', views.book_flight, name='gfa_create'),
    path('api/airports/', views.airport_search, name='airport_search'),
    path('dashboard/', views.admin_dashboard, name='gfa_dashboard'),
    path('update_status/<int:pk>/', views.update_status, name='update_status'),
    path('print/<int:pk>/', views.print_requisition, name='print_requisition'),
    path('upload/<int:pk>/', views.upload_documents, name='gfa_upload'),
    path('ticket/process/<int:pk>/', views.admin_attach_ticket, name='admin_attach_ticket'),
    path('summary/<int:pk>/', views.booking_summary, name='booking_summary'),
    path('transactions/', views.transaction_list, name='gfa_transactions'),

    # --- FINANCIAL (Phase 10) ---
    path('financial/credit-log/', views.credit_log_list, name='credit_log_list'),
    path('financial/settlements/', views.settlement_list, name='settlement_list'),
    path('financial/settlements/add/', views.settlement_create, name='settlement_create'),
    path('approve/<int:pk>/', views.process_approval, name='process_approval'),
]
