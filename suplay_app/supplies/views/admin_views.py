from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
import csv, io
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, F, Count
from django.utils import timezone
from django.contrib.auth.models import User
from ..models import Product, Category, Supplier, Department, Order, OrderItem, StockBatch, AnnualProcurementPlan, APRRequest, APRItem, Settlement, UserProfile, News, DeliveryRecord
from ..forms import ProductForm, StockBatchForm, APRRequestForm, SettlementForm, SupplierForm, CategoryForm, DepartmentForm, NewsForm, DeliveryRecordForm
from ..decorators import role_required, scope_required

# ==========================================
#             ADMIN VIEWS (STOCK & APP LOGIC)
# ==========================================

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    """The central Command Center for SPMO Staff with Strategic Insights"""
    base_template = "supplies/admin_base.html"
    if request.headers.get('HX-Request'):
        base_template = "supplies/includes/admin_partial.html"
        
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    orders = Order.objects.all().order_by('-created_at')
    
    # 1. Operational Aggragates
    active_orders_count = orders.filter(status='pending').count()
    delivery_queue_count = orders.filter(status='approved').count()
    
    # 2. Financial KPIs
    total_stock_value = sum(float(p.price) * p.stock for p in Product.objects.all())
    
    # Monthly Utilization (Total sum of orders delivered/approved this month)
    monthly_utilization = Order.objects.filter(
        created_at__gte=month_start
    ).exclude(status='cancelled').aggregate(total=Sum('total_amount'))['total'] or 0

    # 3. Inventory Insights
    # Low Stock Alerts: items at or below reorder_point
    low_stock_products = Product.objects.filter(stock__lte=F('reorder_point')).count()
    
    # Top Requested Items (All Time or Month - using All Time for stability)
    top_items = OrderItem.objects.values(
        'product__name', 'product__item_code'
    ).annotate(
        total_delivered=Sum('quantity')
    ).order_by('-total_delivered')[:5]

    # 4. Progress Tracking (APR - Phase 3 Logic)
    pending_apr_count = APRRequest.objects.exclude(status='CLOSED').count()
    
    # 5. Smart Insights & Chart Data
    # 5.1 Category Distribution (Stock Value by Category)
    category_data = Category.objects.annotate(
        total_value=Sum(F('product__price') * F('product__stock'))
    ).values('name', 'total_value').order_by('-total_value')
    
    # 5.2 Order Velocity (Last 7 Days)
    seven_days_ago = now - timezone.timedelta(days=7)
    order_velocity = Order.objects.filter(
        created_at__gte=seven_days_ago
    ).values('created_at__date').annotate(
        count=Count('id')
    ).order_by('created_at__date')
    
    # 5.3 Department Spend
    dept_spend = Order.objects.filter(
        created_at__gte=month_start
    ).values('department__name').annotate(
        total=Sum('total_amount')
    ).order_by('-total')[:5]

    context = {
        'active_orders_count': active_orders_count,
        'delivery_queue_count': delivery_queue_count,
        'pending_apr_count': pending_apr_count,
        'total_stock_value': total_stock_value,
        'monthly_utilization': monthly_utilization,
        'low_stock_count': low_stock_products,
        'top_items': top_items,
        'recent_orders': orders[:8],
        'news_items': News.objects.filter(is_active=True).order_by('-urgency', '-date_posted')[:5],
        'urgent_news': News.objects.filter(is_active=True, urgency='URGENT').order_by('-date_posted')[:3],
        'category_data': list(category_data),
        'order_velocity': list(order_velocity),
        'dept_spend': list(dept_spend),
        'base_template': base_template,
    }
    return render(request, 'supplies/admin_dashboard.html', context)

@user_passes_test(lambda u: u.is_staff)
def reports_dashboard(request):
    """Deep Analytics Hub for Institutional Reporting"""
    base_template = "supplies/admin_base.html"
    if request.headers.get('HX-Request') or request.META.get('HTTP_HX_REQUEST'):
        base_template = "supplies/includes/admin_partial.html"
        
    # Aggregate data for top performing departments
    top_depts = Department.objects.annotate(
        order_count=Count('orders')
    ).order_by('-order_count')[:10]
    
    # Financial aggregate
    total_spend = Order.objects.filter(status='delivered').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    context = {
        'top_depts': top_depts,
        'total_spend': total_spend,
        'base_template': base_template,
    }
    return render(request, 'supplies/reports_dashboard.html', context)

@user_passes_test(lambda u: u.is_staff)
def transaction_list(request):
    base_template = "supplies/admin_base.html"
    if request.headers.get('HX-Request') or request.META.get('HTTP_HX_REQUEST'):
        base_template = "supplies/includes/admin_partial.html"
        
    orders = Order.objects.all().order_by('-created_at')
    departments = Order.objects.values_list('department', flat=True).distinct().order_by('department')

    count_pending = orders.filter(status='pending').count()
    count_approved = orders.filter(status='approved').count()
    count_returned = orders.filter(status='returned').count()
    count_delivered = orders.filter(status='delivered').count()
    count_ready_delivered = count_approved + count_delivered

    status_filter = request.GET.get('status')
    if status_filter: 
        orders = orders.filter(status=status_filter)
        
    dept_filter = request.GET.get('department')
    if dept_filter: 
        orders = orders.filter(department=dept_filter)
        
    date_from = request.GET.get('date_from')
    if date_from: 
        orders = orders.filter(created_at__date__gte=date_from)
        
    date_to = request.GET.get('date_to')
    if date_to: 
        orders = orders.filter(created_at__date__lte=date_to)

    context = {
        'orders': orders, 
        'departments': departments,
        'selected_status': status_filter, 
        'selected_dept': dept_filter,
        'selected_date_from': date_from, 
        'selected_date_to': date_to,
        'count_pending': count_pending, 
        'count_ready_delivered': count_ready_delivered,
        'count_returned': count_returned,
        'base_template': base_template,
    }
    return render(request, 'supplies/transactions.html', context)

@user_passes_test(lambda u: u.is_staff)
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    base_template = "supplies/admin_base.html"
    if request.headers.get('HX-Request') or request.META.get('HTTP_HX_REQUEST'):
        base_template = "supplies/includes/admin_partial.html"
    return render(request, 'supplies/inventory_detail.html', {'order': order, 'base_template': base_template}) # Reusing inventory_detail pattern

@user_passes_test(lambda u: u.is_staff)
def delete_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.delete()
    return redirect('transaction_list')

# --- UPDATE STATUS (Includes Stock & APP Deduction) ---
@user_passes_test(lambda u: u.is_staff)
def update_status(request, order_id, new_status):
    order = get_object_or_404(Order, pk=order_id)
    old_status = order.status
    
    # 1. APPROVING: Deduct Stock (FIFO) AND Consume APP
    if new_status == 'approved' and old_status not in ['approved', 'delivered']:
        order.approved_at = timezone.now()
        
        for item in order.items.all():
            product = item.product
            qty_needed = item.quantity
            
            # A. Deduct Physical Stock (FIFO)
            batches = StockBatch.objects.filter(product=product, quantity_remaining__gt=0).order_by('date_received')
            for batch in batches:
                if qty_needed <= 0: break
                if batch.quantity_remaining >= qty_needed:
                    batch.quantity_remaining -= qty_needed
                    batch.save()
                    qty_needed = 0
                else:
                    qty_needed -= batch.quantity_remaining
                    batch.quantity_remaining = 0
                    batch.save()
                batch.save()
            
            product.stock -= item.quantity
            if product.stock < 0: product.stock = 0
            product.save()

            # B. Consume APP Allocation
            try:
                app_entry = AnnualProcurementPlan.objects.get(
                    department=order.department, 
                    product=product,
                    year=timezone.now().year
                )
                app_entry.quantity_consumed += item.quantity
                app_entry.save()
            except AnnualProcurementPlan.DoesNotExist:
                pass 

    # 2. REVERTING: Restock (Add Back) AND Restore APP
    elif old_status in ['approved', 'delivered'] and new_status == 'pending':
        order.approved_at = None
        
        for item in order.items.all():
            product = item.product
            
            # A. Restore Physical Stock
            product.stock += item.quantity
            product.save()
            
            latest_batch = StockBatch.objects.filter(product=product).order_by('-date_received').first()
            if latest_batch:
                latest_batch.quantity_remaining += item.quantity
                latest_batch.save()

            # B. Restore APP Allocation
            try:
                app_entry = AnnualProcurementPlan.objects.get(
                    department=order.department,
                    product=product,
                    year=timezone.now().year
                )
                if app_entry.quantity_consumed >= item.quantity:
                    app_entry.quantity_consumed -= item.quantity
                else:
                    app_entry.quantity_consumed = 0
                app_entry.save()
            except AnnualProcurementPlan.DoesNotExist:
                pass

    order.status = new_status
    
    if new_status == 'delivered':
        order.completed_at = timezone.now()
    else:
        order.completed_at = None
        
    order.save()
    return redirect('transaction_list')

# --- RETURN ORDER (Restock & Restore APP) ---
@scope_required('can_manage_fulfillment')
def return_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=order_id)
        old_status = order.status
        
        if old_status in ['approved', 'delivered']:
            for item in order.items.all():
                product = item.product
                product.stock += item.quantity
                product.save()
                
                latest_batch = StockBatch.objects.filter(product=product).order_by('-date_received').first()
                if latest_batch:
                    latest_batch.quantity_remaining += item.quantity
                    latest_batch.save()

                try:
                    app_entry = AnnualProcurementPlan.objects.get(
                        department=order.department,
                        product=product,
                        year=timezone.now().year
                    )
                    if app_entry.quantity_consumed >= item.quantity:
                        app_entry.quantity_consumed -= item.quantity
                    else:
                        app_entry.quantity_consumed = 0
                    app_entry.save()
                except AnnualProcurementPlan.DoesNotExist:
                    pass

        order.status = 'returned'
        order.remarks = request.POST.get('remarks', '')
        order.save()
    return redirect('transaction_list')

# --- DELIVERY DASHBOARD ---
@scope_required('can_manage_fulfillment')
def delivery_dashboard(request):
    base_template = "supplies/admin_base.html"
    if request.headers.get('HX-Request'):
        base_template = "supplies/includes/admin_partial.html"
        
    orders = Order.objects.filter(status='approved').order_by('approved_at')
    departments = Order.objects.values_list('department', flat=True).distinct().order_by('department')

    dept_filter = request.GET.get('department')
    if dept_filter: orders = orders.filter(department=dept_filter)
    date_from = request.GET.get('date_from')
    if_date_from = request.GET.get('date_from')
    if date_from: orders = orders.filter(created_at__date__gte=date_from)
    date_to = request.GET.get('date_to')
    if date_to: orders = orders.filter(created_at__date__lte=date_to)

    context = {
        'orders': orders, 
        'departments': departments,
        'count_ready': Order.objects.filter(status='approved').count(),
        'count_today_completed': Order.objects.filter(status='delivered', completed_at__date=timezone.now().date()).count(),
        'selected_dept': dept_filter, 
        'selected_date_from': date_from, 
        'selected_date_to': date_to,
        'base_template': base_template,
    }
    return render(request, 'supplies/delivery.html', context)

@scope_required('can_manage_fulfillment')
def mark_delivered(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    order.status = 'delivered'
    order.completed_at = timezone.now()
    order.save()
    return redirect('delivery_dashboard')

# --- INVENTORY & BATCH MANAGEMENT ---
@user_passes_test(lambda u: u.is_staff)
def inventory_list(request):
    base_template = "supplies/admin_base.html"
    if request.headers.get('HX-Request') or request.META.get('HTTP_HX_REQUEST'):
        base_template = "supplies/includes/admin_partial.html"
        
    products = Product.objects.all().order_by('name')
    categories = Category.objects.all().order_by('name')
    
    total_products_count = Product.objects.count()
    total_stock_quantity = Product.objects.aggregate(Sum('stock'))['stock__sum'] or 0
    out_of_stock_count = Product.objects.filter(stock=0).count()
    low_stock_count = Product.objects.filter(stock__lte=10, stock__gt=0).count()

    category_id = request.GET.get('category')
    if category_id: 
        products = products.filter(category_id=category_id)
        
    stock_status = request.GET.get('stock')
    if stock_status == 'in_stock':
        products = products.filter(stock__gt=0)
    elif stock_status == 'out_of_stock':
        products = products.filter(stock=0)
    elif stock_status == 'low_stock':
        products = products.filter(stock__lte=10, stock__gt=0)

    context = {
        'products': products, 
        'categories': categories,
        'selected_category': int(category_id) if category_id else None, 
        'selected_stock': stock_status,
        'total_products_count': total_products_count, 
        'total_stock_quantity': total_stock_quantity, 
        'out_of_stock_count': out_of_stock_count, 
        'low_stock_count': low_stock_count,
        'base_template': base_template,
    }
    return render(request, 'supplies/inventory.html', context)

@scope_required('can_manage_assets')
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')
    else:
        form = ProductForm()
    return render(request, 'supplies/product_form.html', {'form': form, 'title': 'Add New Product'})

@scope_required('can_manage_assets')
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'supplies/product_form.html', {'form': form, 'title': 'Edit Product'})

@scope_required('can_manage_assets')
def delete_product(request, pk):
    if request.method == 'POST':
        Product.objects.get(pk=pk).delete()
    return redirect('inventory_list')

@user_passes_test(lambda u: u.is_staff)
def inventory_detail(request, pk):
    """Deep Item Intelligence & Batch Audit Trail"""
    base_template = "supplies/admin_base.html"
    if request.headers.get('HX-Request') and not request.GET.get('full_page'):
        base_template = "supplies/includes/admin_partial.html"
        
    product = get_object_or_404(Product, pk=pk)
    batches = product.batches.all().order_by('-date_received')
    
    # Movement History (Orders that included this product)
    movements = OrderItem.objects.filter(product=product).select_related('order', 'order__department').order_by('-order__created_at')[:20]
    
    context = {
        'product': product,
        'batches': batches,
        'movements': movements,
        'base_template': base_template,
    }
    return render(request, 'supplies/inventory_detail.html', context)

@user_passes_test(lambda u: u.is_staff)
def receive_delivery(request):
    base_template = "supplies/admin_base.html"
    if request.headers.get('HX-Request') or request.META.get('HTTP_HX_REQUEST'):
        base_template = "supplies/includes/admin_partial.html"
        
    if request.method == 'POST':
        apr_id = request.POST.get('apr_id')
        apr = get_object_or_404(APRRequest, pk=apr_id)
        
        form = DeliveryRecordForm(request.POST, request.FILES)
        if form.is_valid():
            # 1. Create the Audit Trail 'DeliveryRecord'
            delivery = form.save(commit=False)
            delivery.apr = apr
            delivery.received_by = request.user
            delivery.save()
        else:
            # Handle error (re-render with form)
            active_aprs = APRRequest.objects.exclude(status='CLOSED').order_by('-date_prepared')
            return render(request, 'supplies/receive_delivery.html', {
                'active_aprs': active_aprs, 
                'base_template': base_template,
                'form': form,
                'error': "Invalid delivery record data. Please check files and numbers."
            })
        
        # 2. Process Items
        item_ids = request.POST.getlist('item_id')
        for item_id in item_ids:
            qty_received = int(request.POST.get(f'qty_{item_id}', 0))
            if qty_received > 0:
                apr_item = APRItem.objects.get(pk=item_id)
                product = apr_item.product
                
                # A. Create Stock Batch
                StockBatch.objects.create(
                    product=product,
                    supplier_name=apr.supplier.name,
                    batch_number=delivery.dr_number,
                    quantity_initial=qty_received,
                    quantity_remaining=qty_received,
                    cost_per_item=apr_item.unit_price,
                    delivery_record=delivery,
                    apr_reference=apr
                )
                
                # B. Update Inventory
                product.stock += qty_received
                product.save()
                
                # C. Update APR Item Progress
                apr_item.quantity_received += qty_received
                apr_item.save()
        
        # 3. Intelligent Status Transition
        total_requested = apr.items.aggregate(Sum('quantity_requested'))['quantity_requested__sum'] or 0
        total_received = apr.items.aggregate(Sum('quantity_received'))['quantity_received__sum'] or 0
        
        if total_received >= total_requested:
            apr.status = 'CLOSED'
        elif total_received > 0:
            apr.status = 'PARTIALLY_RECEIVED'
        apr.save()
        
        return redirect('batch_list')
        
    # GET: Just show the form
    active_aprs = APRRequest.objects.exclude(status='CLOSED').order_by('-date_prepared')
    return render(request, 'supplies/receive_delivery.html', {
        'active_aprs': active_aprs, 
        'base_template': base_template
    })

@scope_required('can_manage_fulfillment')
def get_apr_manifest(request, apr_id):
    """HTMX endpoint to fetch items for a specific APR during delivery"""
    apr = get_object_or_404(APRRequest, pk=apr_id)
    # Only items not yet fully received
    items = apr.items.all().select_related('product')
    for item in items:
        item.balance = item.quantity_requested - item.quantity_received
        
    return render(request, 'supplies/includes/apr_manifest_entries.html', {
        'items': items,
        'apr': apr
    })

@user_passes_test(lambda u: u.is_staff)
def batch_list(request):
    base_template = "supplies/admin_base.html"
    if request.headers.get('HX-Request') or request.META.get('HTTP_HX_REQUEST'):
        base_template = "supplies/includes/admin_partial.html"
        
    batches = StockBatch.objects.all().order_by('-date_received')
    return render(request, 'supplies/batch_list.html', {
        'batches': batches,
        'base_template': base_template
    })

# --- PROCUREMENT (APR) MODULE ---

@user_passes_test(lambda u: u.is_staff)
def apr_list(request):
    base_template = "supplies/admin_base.html"
    if request.headers.get('HX-Request'):
        base_template = "supplies/includes/admin_partial.html"
        
    aprs = APRRequest.objects.annotate(item_count=Count('items')).order_by('-date_prepared')
    return render(request, 'supplies/apr_list.html', {'aprs': aprs, 'base_template': base_template})

@scope_required('can_manage_procurement')
def add_apr(request):
    base_template = "supplies/admin_base.html"
    if request.headers.get('HX-Request') and not request.GET.get('full_page'):
        base_template = "supplies/includes/admin_partial.html"
        
    if request.method == 'POST':
        form = APRRequestForm(request.POST)
        if form.is_valid():
            apr = form.save(commit=False)
            apr.prepared_by = request.user
            apr.save()
            return redirect('apr_detail', pk=apr.id) 
    else:
        form = APRRequestForm()
    return render(request, 'supplies/apr_form.html', {
        'form': form, 
        'title': 'Initiate Procurement Request',
        'base_template': base_template
    })

@user_passes_test(lambda u: u.is_staff)
def apr_detail(request, pk):
    base_template = "supplies/admin_base.html"
    if request.headers.get('HX-Request'):
        base_template = "supplies/includes/admin_partial.html"
        
    apr = get_object_or_404(APRRequest, pk=pk)
    items = apr.items.all().select_related('product')
    products = Product.objects.all().order_by('name')
    
    context = {
        'apr': apr,
        'items': items,
        'products': products,
        'base_template': base_template,
    }
    return render(request, 'supplies/apr_detail.html', context)

@user_passes_test(lambda u: u.is_staff)
def add_apr_item(request, apr_id):
    if request.method == 'POST':
        apr = get_object_or_404(APRRequest, pk=apr_id)
        product_id = request.POST.get('product')
        quantity = int(request.POST.get('quantity', 0))
        unit_price = float(request.POST.get('unit_price', 0))
        
        APRItem.objects.create(
            apr=apr,
            product_id=product_id,
            quantity_requested=quantity,
            unit_price=unit_price
        )
        
        # Recalculate Total
        apr.total_amount = sum(item.total_amount for item in apr.items.all())
        apr.save()
        
    return redirect('apr_detail', pk=apr_id)

@user_passes_test(lambda u: u.is_staff)
def delete_apr_item(request, item_id):
    item = get_object_or_404(APRItem, pk=item_id)
    apr_id = item.apr.id
    item.delete()
    
    # Recalculate Total
    apr = APRRequest.objects.get(pk=apr_id)
    apr.total_amount = sum(i.total_amount for i in apr.items.all())
    apr.save()
    
    return redirect('apr_detail', pk=apr_id)

@user_passes_test(lambda u: u.is_staff)
def apr_print(request, pk):
    apr = get_object_or_404(APRRequest, pk=pk)
    items = apr.items.all().select_related('product')
    
    # Fill up to 15 rows for 'standard form' look if needed, 
    # but for now we just pass the items.
    
    context = {
        'apr': apr,
        'items': items,
        'today': timezone.now().date(),
    }
    return render(request, 'supplies/apr_print.html', context)

@user_passes_test(lambda u: u.is_staff)
def settlement_list(request):
    base_template = "supplies/admin_base.html"
    if request.headers.get('HX-Request') or request.META.get('HTTP_HX_REQUEST'):
        base_template = "supplies/includes/admin_partial.html"
        
    settlements = Settlement.objects.all().order_by('-created_at')
    
    # Financial Analytics
    total_settled = settlements.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    total_incoming = settlements.filter(settlement_type='INCOMING').aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    total_outgoing = settlements.filter(settlement_type='OUTGOING').aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    
    type_filter = request.GET.get('type')
    if type_filter:
        settlements = settlements.filter(settlement_type=type_filter)
        
    context = {
        'settlements': settlements,
        'selected_type': type_filter,
        'total_settled': total_settled,
        'total_incoming': total_incoming,
        'total_outgoing': total_outgoing,
        'base_template': base_template,
    }
    return render(request, 'supplies/settlements.html', context)

@user_passes_test(lambda u: u.is_staff)
def add_settlement(request):
    order_id = request.GET.get('order_id')
    initial_data = {}
    if order_id: initial_data['order_id'] = order_id
    
    if request.method == 'POST':
        form = SettlementForm(request.POST, request.FILES)
        if form.is_valid():
            settlement = form.save(commit=False)
            settlement.processed_by = request.user
            settlement.save()
            return redirect('settlement_list')
    else:
        form = SettlementForm(initial=initial_data)
        
    return render(request, 'supplies/settlement_form.html', {'form': form})

# ==========================================
# 5. CONFIGURATION HUB (SUPPLIERS, CATEGORIES, UNITS)
# ==========================================

@user_passes_test(lambda u: u.is_staff)
def supplier_list(request):
    base_template = "supplies/admin_base.html"
    if request.headers.get('HX-Request') or request.META.get('HTTP_HX_REQUEST'):
        base_template = "supplies/includes/admin_partial.html"
        
    suppliers = Supplier.objects.annotate(product_count=Count('product')).order_by('name')
    return render(request, 'supplies/supplier_list.html', {'suppliers': suppliers, 'base_template': base_template})

@scope_required('can_manage_system')
def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'supplies/supplier_form.html', {'form': form, 'title': 'Add New Supplier'})

@scope_required('can_manage_system')
def edit_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'supplies/supplier_form.html', {'form': form, 'title': 'Edit Supplier'})

@user_passes_test(lambda u: u.is_staff)
def delete_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    supplier.delete()
    return redirect('supplier_list')

@user_passes_test(lambda u: u.is_staff)
def category_list(request):
    base_template = "supplies/admin_base.html"
    if request.headers.get('HX-Request') or request.META.get('HTTP_HX_REQUEST'):
        base_template = "supplies/includes/admin_partial.html"
        
    categories = Category.objects.annotate(product_count=Count('product')).order_by('name')
    return render(request, 'supplies/category_list.html', {'categories': categories, 'base_template': base_template})

@scope_required('can_manage_system')
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'supplies/category_form.html', {'form': form, 'title': 'Add New Category'})

@scope_required('can_manage_system')
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'supplies/category_form.html', {'form': form, 'title': 'Edit Category'})

@user_passes_test(lambda u: u.is_staff)
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect('category_list')

@user_passes_test(lambda u: u.is_staff)
def unit_list(request):
    base_template = "supplies/admin_base.html"
    if request.headers.get('HX-Request') or request.META.get('HTTP_HX_REQUEST'):
        base_template = "supplies/includes/admin_partial.html"
        
    units = Department.objects.annotate(staff_count=Count('profiles')).order_by('name')
    
    search_query = request.GET.get('search', '')
    if search_query:
        units = units.filter(name__icontains=search_query)
        
    return render(request, 'supplies/unit_list.html', {'units': units, 'base_template': base_template, 'search_query': search_query})

@scope_required('can_manage_system')
def add_unit(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('unit_list')
    else:
        form = DepartmentForm()
    return render(request, 'supplies/unit_form.html', {'form': form, 'title': 'Add New System Office'})

# ==========================================
# 5. DATA HUB (BULK IMPORT/EXPORT)
# ==========================================

@user_passes_test(lambda u: u.is_staff)
def data_hub(request):
    base_template = "supplies/admin_base.html"
    if request.headers.get('HX-Request') or request.META.get('HTTP_HX_REQUEST'):
        base_template = "supplies/includes/admin_partial.html"
    return render(request, 'supplies/data_hub.html', {'base_template': base_template})

@user_passes_test(lambda u: u.is_staff)
def download_template(request, type):
    response = HttpResponse(content_type='text/csv')
    
    if type == 'incoming':
        response['Content-Disposition'] = 'attachment; filename="suplay_incoming_template.csv"'
        writer = csv.writer(response)
        writer.writerow(['date_received', 'item_code', 'quantity', 'unit_cost', 'supplier_name', 'batch_number'])
        writer.writerow(['2026-01-15', 'STK-001', '100', '150.50', 'Global Supplies Inc', 'B2026-01'])
    else:
        response['Content-Disposition'] = 'attachment; filename="suplay_outgoing_template.csv"'
        writer = csv.writer(response)
        writer.writerow(['date_requested', 'employee_name', 'department_name', 'item_code', 'quantity', 'unit_cost', 'status'])
        writer.writerow(['2026-01-20', 'Juan Dela Cruz', 'Accounting Office', 'STK-001', '5', '165.00', 'delivered'])
        
    return response

@user_passes_test(lambda u: u.is_staff)
def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        import_type = request.POST.get('import_type')
        
        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        success_count = 0
        error_count = 0
        
        for row in reader:
            try:
                if import_type == 'incoming':
                    product = Product.objects.get(item_code=row['item_code'])
                    StockBatch.objects.create(
                        product=product,
                        supplier_name=row['supplier_name'],
                        batch_number=row['batch_number'],
                        quantity_initial=int(row['quantity']),
                        quantity_remaining=int(row['quantity']),
                        cost_per_item=float(row['unit_cost']),
                        date_received=row['date_received']
                    )
                    # Update master stock
                    product.stock += int(row['quantity'])
                    product.save()
                
                elif import_type == 'outgoing':
                    product = Product.objects.get(item_code=row['item_code'])
                    dept, _ = Department.objects.get_or_create(name=row['department_name'])
                    
                    order = Order.objects.create(
                        employee_name=row['employee_name'],
                        department=dept,
                        total_amount=float(row['unit_cost']) * int(row['quantity']),
                        status=row['status']
                    )
                    order.created_at = row['date_requested']
                    order.save()
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=int(row['quantity']),
                        price=float(row['unit_cost'])
                    )
                    # Deduct stock if delivered
                    if row['status'] == 'delivered':
                        product.stock -= int(row['quantity'])
                        product.save()
                
                success_count += 1
            except Exception as e:
                error_count += 1
                
        return JsonResponse({
            'status': 'success',
            'message': f'Import Complete: {success_count} records added, {error_count} failed.'
        })
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})
@user_passes_test(lambda u: u.is_staff)
def delete_unit(request, pk):
    unit = get_object_or_404(Department, pk=pk)
    unit.delete()
    return redirect('unit_list')

@scope_required('can_manage_system')
def edit_unit(request, pk):
    unit = get_object_or_404(Department, pk=pk)
    # Get personnel linked to this unit
    personnel = UserProfile.objects.filter(department=unit).select_related('user')
    # Get users NOT linked to any department or linked to THIS department
    available_users = User.objects.exclude(profile__department__isnull=False).exclude(is_staff=True)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            # Handle user assignment if HX-Post or normal post
            user_id = request.POST.get('assign_user')
            if user_id:
                user_to_assign = User.objects.get(pk=user_id)
                profile = user_to_assign.profile
                profile.department = unit
                profile.role = 'dept_staff' # Default to Unit Admin Staff role
                profile.save()
            
            return redirect('unit_list')
    else:
        form = DepartmentForm(instance=unit)
        
    context = {
        'form': form, 
        'unit': unit,
        'personnel': personnel,
        'available_users': available_users,
        'title': f'Manage {unit.name}'
    }
    return render(request, 'supplies/unit_form.html', context)

@scope_required('can_manage_system')
def unlink_user(request, profile_id):
    profile = get_object_or_404(UserProfile, pk=profile_id)
    unit_id = profile.department.id
    profile.department = None
    profile.save()
    return redirect('edit_unit', pk=unit_id)

@scope_required('can_manage_procurement')
def broadcast_list(request):
    """List all global announcements in the Broadcast Hub"""
    base_template = "supplies/admin_base.html"
    if request.headers.get('HX-Request') or request.META.get('HTTP_HX_REQUEST'):
        base_template = "supplies/includes/admin_partial.html"

    news_items = News.objects.all().order_by('-date_posted')
        
    return render(request, 'supplies/broadcast_list.html', {
        'news_items': news_items,
        'base_template': base_template
    })

@scope_required('can_manage_procurement')
def add_broadcast(request):
    """Create a new global announcement"""
    base_template = "supplies/admin_base.html"
    if request.headers.get('HX-Request') and not request.GET.get('full_page'):
        base_template = "supplies/includes/admin_partial.html"
        
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            return redirect('broadcast_list')
    else:
        form = NewsForm()
        
    return render(request, 'supplies/broadcast_form.html', {
        'form': form,
        'base_template': base_template,
        'title': 'New Broadcast'
    })

@scope_required('can_manage_procurement')
def edit_broadcast(request, pk):
    """Modify an existing global announcement"""
    news = get_object_or_404(News, pk=pk)
    base_template = "supplies/admin_base.html"
    if request.headers.get('HX-Request') and not request.GET.get('full_page'):
        base_template = "supplies/includes/admin_partial.html"
        
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            form.save()
            return redirect('broadcast_list')
    else:
        form = NewsForm(instance=news)
        
    return render(request, 'supplies/broadcast_form.html', {
        'form': form,
        'base_template': base_template,
        'title': 'Edit Broadcast'
    })

@scope_required('can_manage_procurement')
def delete_broadcast(request, pk):
    """Remove a global announcement"""
    if request.method == 'POST':
        News.objects.get(pk=pk).delete()
    return redirect('broadcast_list')
