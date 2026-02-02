from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db.models import Sum, Q
from django.utils import timezone
from django.template.loader import get_template
from django.http import HttpResponse, JsonResponse
from io import BytesIO
from xhtml2pdf import pisa
# IMPORTANT: Added AnnualProcurementPlan to imports
from .models import Product, Category, Order, OrderItem, StockBatch, AnnualProcurementPlan, Supplier
from .forms import ProductForm, StockBatchForm

# ==========================================
#             CLIENT SIDE VIEWS
# ==========================================

# --- HOME PAGE ---
@login_required
def home(request):
    # 1. Base Queryset (Optimization: Select Related)
    products = Product.objects.select_related('category', 'supplier').all().order_by('category__name', 'name')

    # --- APP ALLOCATION LOGIC ---
    user_department = None
    if hasattr(request.user, 'profile'):
        user_department = request.user.profile.department

    if user_department:
        # User belongs to a department: STRICT FILTERING
        # 1. Get List of Product IDs allocated to this department
        allocated_product_ids = AnnualProcurementPlan.objects.filter(
            department=user_department,
            year=2025 # Default Year
        ).values_list('product_id', flat=True)

        # 2. Filter Main Queryset
        products = products.filter(id__in=allocated_product_ids)

        # 3. Annotate EACH product with 'personal_stock'
        # This is inefficient for large datasets but simple for now. 
        # Ideally, we used SubQueries, but Python loop is safer for complex property logic.
        # We will iterate in the template or attach it here.
        # Let's attach a dictionary for fast lookup
        allocations = AnnualProcurementPlan.objects.filter(
            department=user_department, 
            year=2025
        ).select_related('product')
        
        allocation_map = {a.product_id: a.remaining_balance() for a in allocations}

        # We can't easily annotate a Python property onto a QS without raw SQL or looping.
        # Since pagination isn't huge, we can attach attributes in a wrapper or just pass the map?
        # Better: Filter first, then when rendering, use a Template Filter or helper.
        # Let's attach it to the object in a list (converts QuerySet to List)
        products_list = []
        for p in products:
            p.personal_stock = allocation_map.get(p.id, 0)
            products_list.append(p)
        products = products_list # Override queryset with list
    else:
        # Fallback: Just show global stock (default behavior)
        pass

    # 2. Filter by Category (If passed) - Works on List or Queryset
    category_id = request.GET.get('category')
    if category_id:
        if isinstance(products, list):
            products = [p for p in products if p.category_id == int(category_id)]
        else:
            products = products.filter(category_id=category_id)

    # 3. Filter by Supplier
    supplier_id = request.GET.get('supplier')
    if supplier_id:
        if isinstance(products, list):
            products = [p for p in products if p.supplier_id == int(supplier_id)]
        else:
            products = products.filter(supplier_id=supplier_id)

    # 4. Filter by Stock Status
    stock_status = request.GET.get('stock')
    if stock_status == 'in':
        if isinstance(products, list):
            products = [p for p in products if (getattr(p, 'personal_stock', p.stock) > 0)]
        else:
            products = products.filter(stock__gt=0)
    elif stock_status == 'out':
        if isinstance(products, list):
            products = [p for p in products if (getattr(p, 'personal_stock', p.stock) == 0)]
        else:
            products = products.filter(stock=0)
    
    # 5. Context Data
    categories = Category.objects.all().order_by('name')
    suppliers = Supplier.objects.all().order_by('name')

    # 6. Suggested Items (Random 4 for now) - REMOVED TO PREVENT CRASH FOR NOW
    # suggested_products = Product.objects.all().order_by('?')[:4]
    suggested_products = [] 

    # 7. Hero Banner Data (New & Restocked)
    # HERO should probably be filtered too? Or show generic? 
    # Let's keep Hero generic for now but maybe hide "Add to Cart" if not allocated?
    # For now, leaving Hero generic.
    newly_added = Product.objects.all().order_by('-created_at')[:5]
    restocked_batches = StockBatch.objects.select_related('product').order_by('-date_received')[:5]
    
    return render(request, 'supplies/home.html', {
        'products': products,
        'categories': categories,
        'suppliers': suppliers,
        'suggested_products': suggested_products,
        'newly_added': newly_added,
        'restocked_batches': restocked_batches,
        'selected_category': int(category_id) if category_id else None,
        'selected_supplier': int(supplier_id) if supplier_id else None,
        'selected_stock': stock_status,
        'search_query': None,
        'user_has_department': bool(user_department)
    })

# --- SEARCH ---
@login_required
def search(request):
    query = request.GET.get('q', '')
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(brand__icontains=query) | 
            Q(item_code__icontains=query)
        ).order_by('category__name', 'name')
        
        valid_category_ids = products.values_list('category_id', flat=True).distinct()
        categories = Category.objects.filter(id__in=valid_category_ids).order_by('name')
    else:
        products = Product.objects.all().order_by('category__name', 'name')
        categories = Category.objects.all().order_by('name')
    
    return render(request, 'supplies/home.html', {
        'products': products, 
        'categories': categories, 
        'search_query': query
    })

# --- PRODUCT DETAIL ---
@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'supplies/product_detail.html', {'product': product})

# --- CART ACTIONS (FIXED) ---
@login_required
def add_to_cart(request, pk):
    cart = request.session.get('cart', {})
    product_id = str(pk)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1

    # Check for AJAX header to return JSON errors properly
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or \
              request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

    # --- START APP CHECK (DISABLED FOR TESTING) ---
    # I have temporarily commented this out so you can test the cart immediately.
    # Since your database was flushed, the APP table is empty. If this runs,
    # it will block EVERYTHING. Uncomment this block when you have populated the APP table.
    
    # product = get_object_or_404(Product, pk=pk)
    # user_dept = request.session.get('user_department', 'General') 
    # try:
    #     app_entry = AnnualProcurementPlan.objects.get(
    #         department=user_dept,
    #         product=product,
    #         year=timezone.now().year
    #     )
    #     current_cart_qty = cart.get(product_id, 0)
    #     total_requested = quantity + current_cart_qty
    #     if total_requested > app_entry.remaining_balance():
    #         msg = f"APP Limit Reached! Only {app_entry.remaining_balance()} remaining."
    #         if is_ajax: return JsonResponse({'status': 'error', 'message': msg}, status=400)
    #         return redirect('home')
    # except AnnualProcurementPlan.DoesNotExist:
    #     msg = "This item is not in your Annual Procurement Plan."
    #     if is_ajax: return JsonResponse({'status': 'error', 'message': msg}, status=400)
    #     return redirect('home')
    # --- END APP CHECK ---

    # Add to Cart Logic
    if product_id in cart:
        cart[product_id] += quantity
    else:
        cart[product_id] = quantity
    
    request.session['cart'] = cart
    request.session.modified = True 
    
    # CRITICAL FIX: Calculate total quantity of items (e.g., 5 pens + 2 papers = 7)
    # The previous code used len(cart) which only counted unique products (e.g., 2)
    total_count = sum(cart.values())

    if is_ajax:
        return JsonResponse({
            'status': 'success', 
            'cart_count': total_count,
            'message': 'Item added successfully'
        })

    return redirect('home')

@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(pk=product_id)
            subtotal = product.price * quantity
            cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
            total += subtotal
        except Product.DoesNotExist:
            continue
            
    return render(request, 'supplies/cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def update_cart(request, pk):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        product_id = str(pk)
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity > 0:
                cart[product_id] = quantity
            else:
                cart.pop(product_id, None)
            request.session['cart'] = cart
            request.session.modified = True
        except ValueError:
            pass
    return redirect('view_cart')

@login_required
def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    product_id = str(pk)
    if product_id in cart:
        cart.pop(product_id, None)
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('view_cart')

# ==========================================
#          CHECKOUT & PRINT FLOW
# ==========================================

@login_required
def checkout_init(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if not cart:
            return redirect('home')

        total = 0
        valid_items = {} 
        
        for pid, qty in cart.items():
            try:
                prod = Product.objects.get(pk=pid)
                total += prod.price * qty
                valid_items[pid] = prod 
            except Product.DoesNotExist:
                continue

        if total == 0 and not valid_items:
            request.session['cart'] = {}
            return redirect('view_cart')

        order = Order.objects.create(
            user=request.user,
            employee_name=request.POST.get('name', 'Unknown'),
            department=request.POST.get('department', 'General'),
            total_amount=total,
            status='draft' 
        )

        for pid, prod in valid_items.items():
            quantity = cart[pid]
            OrderItem.objects.create(
                order=order, 
                product=prod, 
                quantity=quantity, 
                price=prod.price
            )
        
        return redirect('checkout_finalize', order_id=order.id)

    return render(request, 'supplies/checkout.html')


@login_required
def checkout_finalize(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)

    if order.status != 'draft':
        return redirect('order_success', order_id=order.id)

    if request.method == 'POST':
        if 'document1' in request.FILES:
            order.document1 = request.FILES['document1']
        
        # JUST UPDATE STATUS - DO NOT DEDUCT STOCK OR APP YET
        # Deduction happens on Admin Approval
        order.status = 'pending'
        order.save()

        # Clear Cart
        request.session['cart'] = {}
        request.session.modified = True
        return redirect('order_success', order_id=order.id)

    return render(request, 'supplies/checkout_finalize.html', {'order': order})


@login_required
def print_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'supplies/print_order.html', {'order': order})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'supplies/order_success.html', {'order': order})

@login_required
def profile(request):
    # 1. Request History (Limit 5)
    my_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # 2. Suggested Items Logic
    suggested_products = []
    
    # Strategy A: Check user's department from last order
    last_order = Order.objects.filter(user=request.user).order_by('-created_at').first()
    
    if last_order:
        # Get orders from same department, exclude user's own last week orders to vary it? 
        # For now, just get top products ordered by this dept
        # Since we don't have complex analytics, we'll just get random items from same categories they ordered
        last_item = last_order.items.first()
        if last_item:
            target_category = last_item.product.category
            suggested_products = Product.objects.filter(category=target_category).exclude(id=last_item.product.id).order_by('?')[:4]

    # Strategy B: Fallback (If no history or not enough suggestions)
    if not suggested_products or len(suggested_products) < 4:
        # Just get 4 random items
        # In a real app, this would be "Most Popular"
        additional_needed = 4 - len(suggested_products)
        ids_to_exclude = [p.id for p in suggested_products]
        fallback_items = Product.objects.exclude(id__in=ids_to_exclude).order_by('?')[:additional_needed]
        # Combine them (if list was empty, it's just fallback)
        import itertools
        suggested_products = list(itertools.chain(suggested_products, fallback_items))

    return render(request, 'supplies/profile.html', {
        'orders': my_orders,
        'suggested_products': suggested_products
    })


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

# --- GENERATE REQUISITION SLIP (PDF) ---
@login_required
def requisition_slip(request, order_id=None):
    cart_items = []
    total = 0
    order = None

    if order_id:
        # Generate from specific Order
        order = get_object_or_404(Order, pk=order_id)
        if order.user != request.user and not request.user.is_superuser:
            # Simple permission check (can refine if needed)
            return redirect('home')

        for item in order.items.all():
            subtotal = item.price * item.quantity
            cart_items.append({'product': item.product, 'quantity': item.quantity, 'subtotal': subtotal})
            total += subtotal
    else:
        # Fallback: Generate from Session Cart (Pre-checkout)
        cart = request.session.get('cart', {})
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(pk=product_id)
                subtotal = product.price * quantity
                cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
                total += subtotal
            except Product.DoesNotExist:
                continue

    context = {
        'cart_items': cart_items,
        'total': total,
        'user': request.user,
        'date': timezone.now(),
        'order': order, 
    }

    template = get_template('supplies/requisition_slip.html')
    html = template.render(context)
    result = BytesIO()
    
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        if order:
            filename = f"requisition_slip_{order.id}.pdf"
        else:
            filename = "requisition_slip.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    return HttpResponse("Error generating PDF", status=400)

# --- APP MODULE VIEWS ---

@login_required
def my_app_status(request):
    # FIX: Use UserProfile instead of Session/Placeholder
    user_dept = None
    if hasattr(request.user, 'profile'):
        user_dept = request.user.profile.department
    
    if not user_dept:
        # Fallback or empty if no profile
        # Perhaps show all if superuser? No, strict mode means empty.
        allocations = AnnualProcurementPlan.objects.none()
    else:
        allocations = AnnualProcurementPlan.objects.filter(
            department=user_dept, 
            year=timezone.now().year
        ).select_related('product', 'product__category').order_by('product__category__name', 'product__name')

    return render(request, 'supplies/app_status.html', {'allocations': allocations})