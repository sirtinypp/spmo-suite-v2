from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

   
    # --- AUTHENTICATION ---
    path('accounts/login/', auth_views.LoginView.as_view(template_name='supplies/login.html', next_page='home'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/accounts/login/'), name='logout'),

    # --- CLIENT PAGES ---
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.view_cart, name='view_cart'),
    path('profile/', views.profile, name='profile'),

    # --- CLIENT ACTIONS ---
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:pk>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),

    # --- CHECKOUT FLOW ---
    path('checkout/', views.checkout_init, name='checkout'),
    path('checkout/finalize/<int:order_id>/', views.checkout_finalize, name='checkout_finalize'),
    path('print-order/<int:order_id>/', views.print_order, name='print_order'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),

    # --- ADMIN ---
    path('console/', views.admin_dashboard, name='admin_dashboard'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('update-status/<int:order_id>/<str:new_status>/', views.update_status, name='update_status'),
    path('return-order/<int:order_id>/', views.return_order, name='return_order'),
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.add_product, name='add_product'),
    path('inventory/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('inventory/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('inventory/detail/<int:pk>/', views.inventory_detail, name='inventory_detail'),
    path('receive-delivery/', views.receive_delivery, name='receive_delivery'),
    path('batch-monitor/', views.batch_list, name='batch_list'),
    path('delivery/', views.delivery_dashboard, name='delivery_dashboard'),
    path('delivery/confirm/<int:order_id>/', views.mark_delivered, name='mark_delivered'),
    path('delivery/manifest/<int:apr_id>/', views.get_apr_manifest, name='get_apr_manifest'),
    path('order-history/', views.delivery_dashboard, name='order_history'),

    path('requisition-slip/', views.requisition_slip, name='requisition_slip'),
    path('requisition-slip/<int:order_id>/', views.requisition_slip, name='requisition_slip_download'),
    path('my-allocation/', views.my_app_status, name='my_app_status'),

    # --- MANAGEMENT CONTROLS ---
    path('apr/', views.apr_list, name='apr_list'),
    path('apr/add/', views.add_apr, name='add_apr'),
    path('apr/detail/<int:pk>/', views.apr_detail, name='apr_detail'),
    path('apr/add-item/<int:apr_id>/', views.add_apr_item, name='add_apr_item'),
    path('apr/delete-item/<int:item_id>/', views.delete_apr_item, name='delete_apr_item'),
    path('apr/print/<int:pk>/', views.apr_print, name='apr_print'),

    path('settlements/', views.settlement_list, name='settlement_list'),
    path('settlements/add/', views.add_settlement, name='add_settlement'),

    path('reports/', views.reports_dashboard, name='reports_dashboard'),

    path('broadcast/', views.broadcast_list, name='broadcast_list'),
    path('broadcast/add/', views.add_broadcast, name='add_broadcast'),
    path('broadcast/edit/<int:pk>/', views.edit_broadcast, name='edit_broadcast'),
    path('broadcast/delete/<int:pk>/', views.delete_broadcast, name='delete_broadcast'),

    # --- CONFIGURATION HUB ---
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    path('suppliers/edit/<int:pk>/', views.edit_supplier, name='edit_supplier'),

    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:pk>/', views.edit_category, name='edit_category'),

    path('units/', views.unit_list, name='unit_list'),
    path('units/add/', views.add_unit, name='add_unit'),
    path('units/edit/<int:pk>/', views.edit_unit, name='edit_unit'),
    path('units/unlink/<int:profile_id>/', views.unlink_user, name='unlink_user'),
]