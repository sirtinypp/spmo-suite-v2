from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum
from django.utils import timezone
from ..models import Product, Category, Order, OrderItem, StockBatch, AnnualProcurementPlan
from ..forms import ProductForm, StockBatchForm

# ==========================================
#             ADMIN VIEWS (STOCK & APP LOGIC)
# ==========================================

@user_passes_test(lambda u: u.is_superuser)
def transaction_list(request):
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
        'count_returned': count_returned
    }
    return render(request, 'supplies/transactions.html', context)

# --- UPDATE STATUS (Includes Stock & APP Deduction) ---
@user_passes_test(lambda u: u.is_superuser)
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
            
            product.stock -= item.quantity
            if product.stock < 0: product.stock = 0
            product.save()

            # B. Consume APP Allocation
            # Find the correct APP entry for this department
            try:
                app_entry = AnnualProcurementPlan.objects.get(
                    department=order.department, # Uses dept from Order info
                    product=product,
                    year=timezone.now().year
                )
                app_entry.quantity_consumed += item.quantity
                app_entry.save()
            except AnnualProcurementPlan.DoesNotExist:
                pass # If no APP exists, skip (or handle as error if strict)

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
                # Prevent negative consumption
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
@user_passes_test(lambda u: u.is_superuser)
def return_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=order_id)
        old_status = order.status
        
        # If returning an order that was approved/delivered, we must restock everything
        if old_status in ['approved', 'delivered']:
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

        order.status = 'returned'
        order.remarks = request.POST.get('remarks', '')
        order.save()
    return redirect('transaction_list')

# --- DELIVERY DASHBOARD ---
@user_passes_test(lambda u: u.is_superuser)
def delivery_dashboard(request):
    orders = Order.objects.filter(status='approved').order_by('approved_at')
    departments = Order.objects.values_list('department', flat=True).distinct().order_by('department')

    dept_filter = request.GET.get('department')
    if dept_filter: orders = orders.filter(department=dept_filter)
    date_from = request.GET.get('date_from')
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
    }
    return render(request, 'supplies/delivery.html', context)

@user_passes_test(lambda u: u.is_superuser)
def mark_delivered(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    order.status = 'delivered'
    order.completed_at = timezone.now()
    order.save()
    return redirect('delivery_dashboard')

# --- INVENTORY & BATCH MANAGEMENT ---
@user_passes_test(lambda u: u.is_superuser)
def inventory_list(request):
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
        'low_stock_count': low_stock_count
    }
    return render(request, 'supplies/inventory.html', context)

@user_passes_test(lambda u: u.is_superuser)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')
    else:
        form = ProductForm()
    return render(request, 'supplies/product_form.html', {'form': form, 'title': 'Add New Product'})

@user_passes_test(lambda u: u.is_superuser)
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

@user_passes_test(lambda u: u.is_superuser)
def delete_product(request, pk):
    if request.method == 'POST':
        Product.objects.get(pk=pk).delete()
    return redirect('inventory_list')

@user_passes_test(lambda u: u.is_superuser)
def receive_delivery(request):
    if request.method == 'POST':
        form = StockBatchForm(request.POST)
        if form.is_valid():
            batch = form.save(commit=False)
            batch.quantity_remaining = batch.quantity_initial
            batch.save()
            
            product = batch.product
            product.stock += batch.quantity_initial
            product.save()
            
            return redirect('batch_list')
    else:
        form = StockBatchForm()
    return render(request, 'supplies/receive_delivery.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def batch_list(request):
    batches = StockBatch.objects.all().order_by('-date_received')
    return render(request, 'supplies/batch_list.html', {'batches': batches})
