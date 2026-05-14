from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q, Count, F
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.contrib import messages
from decimal import Decimal
from io import BytesIO
from xhtml2pdf import pisa

from ..models import Product, Category, Order, OrderItem, EmergencyRequest, AnnualProcurementPlan, Supplier, StockBatch, News, Department
from ..forms import OrderDocumentForm

@login_required
def upload_dv(request, order_id):
    """
    Institutional Self-Settlement: Allows Unit AO to upload DV proof.
    Transition: DELIVERED_PENDING_SETTLEMENT -> (Wait for Admin Verification)
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        dv_no = request.POST.get('dv_no')
        dv_file = request.FILES.get('dv_file')
        
        if dv_no and dv_file:
            order.dv_no = dv_no
            order.dv_file = dv_file
            order.dv_uploaded_at = timezone.now()
            # Note: We keep status as delivered_pending_settlement 
            # until verified by Admin.
            order.save()
            messages.success(request, f"Settlement proof for Order #SUP-{order.id:05d} has been uploaded and is now awaiting institutional verification.")
        else:
            messages.error(request, "Please provide both the DV Number and the File Scan.")
            
    return redirect('profile')

# ==========================================
#             CLIENT SIDE VIEWS
# ==========================================

# --- HOME PAGE ---

def check_monthly_allocation(user, product_id, quantity_to_add, current_cart_qty=0):
    """
    Centralized logic to check if a user can add/update item quantity based on monthly allocation.
    Returns: (is_allowed: bool, error_message: str|None, remaining: int)
    """
    try:
        user_dept = user.profile.department
    except:
        return False, "Department not assigned.", 0

    if not user_dept:
        return False, "Department not assigned.", 0

    current_year = timezone.now().year
    now = timezone.now()
    month_str = now.strftime('%b').lower()

    try:
        # 1. Get Allocation
        alloc = AnnualProcurementPlan.objects.get(department=user_dept, product_id=product_id, year=current_year)
        limit = getattr(alloc, month_str, 0)

        # 2. Get Consumed
        monthly_orders = Order.objects.filter(
            department=user_dept,
            created_at__year=current_year,
            created_at__month=now.month
        ).exclude(status='cancelled')

        consumed = OrderItem.objects.filter(
            order__in=monthly_orders,
            product_id=product_id
        ).aggregate(total=Sum('quantity'))['total'] or 0

        # 3. Check Balance
        total_attempted = consumed + current_cart_qty + quantity_to_add
        
        if total_attempted > limit:
            remaining = max(0, limit - (consumed + current_cart_qty))
            msg = (f"Monthly Limit Reached ({month_str.title()})! "
                   f"Allocation: {limit}. "
                   f"Consumed+Cart: {consumed + current_cart_qty}. "
                   f"Remaining: {remaining}.")
            return False, msg, remaining
        
        return True, None, limit - total_attempted

    except AnnualProcurementPlan.DoesNotExist:
        return False, "Restricted: Your department has no allocation record for this item this year.", 0

def home(request):
    """
    APP Allocation Filtered View
    Displays only products allocated to user's department in current year.
    """
    # 1. Get user's department
    user_dept = None
    user_has_department = False
    info_message = None
    
    if hasattr(request.user, 'profile') and request.user.profile.department:
        user_dept = request.user.profile.department
        user_has_department = True
    
    # 2. Filter by APP Allocation
    if request.user.is_superuser:
        # SUPERUSER OVERRIDE: See all products
        products = Product.objects.all().select_related('category', 'supplier').order_by('name')
        allocated_product_ids = Product.objects.values_list('id', flat=True)
        # info_message = "Admin View: Showing all items."
    elif request.user.is_authenticated and user_dept:
        # AUTHENTICATED USER WITH DEPARTMENT: Show allocated products
        current_year = timezone.now().year
        
        # Get products allocated to this department this year
        allocated_product_ids = AnnualProcurementPlan.objects.filter(
            department=user_dept,
            year=current_year
        ).values_list('product_id', flat=True)
        
        # FALLBACK: If no 2026 allocations, check 2025
        if not allocated_product_ids:
            previous_year = current_year - 1
            allocated_product_ids = AnnualProcurementPlan.objects.filter(
                department=user_dept,
                year=previous_year
            ).values_list('product_id', flat=True)
            if allocated_product_ids:
                info_message = f"Note: Showing allocations from {previous_year} (No {current_year} records found)."
        
        if not allocated_product_ids:
            # If authenticated but no allocations, show all products
            products = Product.objects.all().select_related('category', 'supplier').order_by('name')
            allocated_product_ids = Product.objects.values_list('id', flat=True)
            info_message = f"No allocations found for {user_dept.name}. Showing all products."
        else:
            # Base queryset - ONLY allocated products
            products = Product.objects.filter(
                id__in=list(allocated_product_ids)
            ).select_related('category', 'supplier').order_by('name')
    else:
        # PUBLIC/UNAUTHENTICATED: Show all products
        products = Product.objects.all().select_related('category', 'supplier').order_by('name')
        allocated_product_ids = Product.objects.values_list('id', flat=True)
    
    # 3. Apply existing filters (category, supplier, stock)
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    supplier_id = request.GET.get('supplier')
    if supplier_id:
        products = products.filter(supplier_id=supplier_id)

    search_query = request.GET.get('q')
    stock_status = request.GET.get('stock')
    ready_to_order = request.GET.get('ready_to_order') == '1'

    # --- ADVANCED ALLOCATION FILTERING ---
    orderable_ids = []
    if request.user.is_authenticated and user_dept:
        now = timezone.now()
        month_str = now.strftime('%b').lower()
        current_year = now.year
        
        # 1. Get all products in the user's APP
        app_items = AnnualProcurementPlan.objects.filter(department=user_dept, year=current_year)
        
        # 2. Filter for those with remaining monthly allocation
        for item in app_items:
            limit = getattr(item, month_str, 0)
            if limit > 0:
                # Check consumption
                monthly_orders = Order.objects.filter(
                    department=user_dept,
                    created_at__year=current_year,
                    created_at__month=now.month
                ).exclude(status='cancelled')
                
                consumed = OrderItem.objects.filter(
                    order__in=monthly_orders,
                    product=item.product
                ).aggregate(total=Sum('quantity'))['total'] or 0
                
                if consumed < limit:
                    orderable_ids.append(item.product_id)
        
        if ready_to_order:
            products = products.filter(id__in=orderable_ids)

    if search_query:
        # If searching: Show everything matching the query (In Stock + Out of Stock)
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(item_code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    else:
        # If NOT searching: Default to showing ONLY In-Stock items
        # Unless user explicitly asks for 'out_of_stock' via filter dropdown (if exists)
        if stock_status == 'out_of_stock':
             products = products.filter(stock=0)
        else:
             # Default behavior (including stock_status == 'in_stock')
             products = products.filter(stock__gt=0)
    
    # --- PAGINATION (DAST Optimization) ---
    paginator = Paginator(products, 12) # 12 items per page
    page = request.GET.get('page')
    try:
        products_paginated = paginator.page(page)
    except PageNotAnInteger:
        products_paginated = paginator.page(1)
    except EmptyPage:
        products_paginated = paginator.page(paginator.num_pages)

    # --- CALCULATE MONTHLY PERSONAL STOCK (Current Page Only) ---
    if request.user.is_authenticated and user_dept:
        now = timezone.now()
        month_str = now.strftime('%b').lower()
        current_cart = request.session.get('cart', {})
        current_year = now.year
        
        for p in products_paginated:
            try:
                plan = AnnualProcurementPlan.objects.get(
                    department=user_dept, 
                    product=p, 
                    year=current_year
                )
                limit = getattr(plan, month_str, 0)
            except AnnualProcurementPlan.DoesNotExist:
                limit = 0
            
            monthly_orders = Order.objects.filter(
                department=user_dept,
                created_at__year=current_year,
                created_at__month=now.month
            ).exclude(status='cancelled')
            
            consumed = OrderItem.objects.filter(
                order__in=monthly_orders,
                product=p
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            in_cart = current_cart.get(str(p.id), 0)
            p.personal_stock = max(0, limit - (consumed + in_cart))
    
    # 4. Context Data
    
    # Calculate counts for Categories (based on ALL allocated products, ignoring current filters)
    # We need to know how many items are available in each category for this user
    # 4. Context Data
    
    # Calculate counts for Categories (based on ALL allocated products, ignoring current filters)
    # We need to know how many items are available in each category for this user
    if user_dept or request.user.is_superuser:
        categories = Category.objects.annotate(
            product_count=Count('product', filter=Q(product__id__in=allocated_product_ids))
        ).filter(product_count__gt=0).order_by('name')
        
        suppliers = Supplier.objects.annotate(
            product_count=Count('product', filter=Q(product__id__in=allocated_product_ids))
        ).filter(product_count__gt=0).order_by('name')
    else:
        categories = Category.objects.annotate(product_count=Count('product')).order_by('name') # Fallback if no dept (should be empty products anyway)
        suppliers = Supplier.objects.all()

    # categories = Category.objects.all() # OLD
    # suppliers = Supplier.objects.all() # OLD
    
    # Newly Added (Last 30 days) - Based on ALL filtered products
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    # Re-query for newly added within the current filtered set
    newly_added = products.filter(created_at__gte=thirty_days_ago).order_by('-created_at')[:5]
    
    # Latest News
    news_items = News.objects.filter(is_active=True).order_by('-urgency', '-date_posted')[:5]
    urgent_news = News.objects.filter(is_active=True, urgency='URGENT').order_by('-date_posted')[:3]

    context = {
        'products': products_paginated,
        'total_count_all': products.count(),
        'categories': categories,
        'suppliers': suppliers,
        'newly_added': newly_added,
        'news_items': news_items,
        'urgent_news': urgent_news,
        'user_has_department': user_has_department,
        'info_message': info_message
    }
    return render(request, 'supplies/home.html', context)

# --- SEARCH ---
def search(request):
    query = request.GET.get('q', '')
    
    # Get user's department for APP filtering
    user_dept = None
    if hasattr(request.user, 'profile') and request.user.profile.department:
        user_dept = request.user.profile.department
    
    if query:
        # Start with search query
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(brand__icontains=query) | 
            Q(item_code__icontains=query)
        )
        
        # Apply APP filtering if user has department
        if user_dept:
            current_year = timezone.now().year
            allocated_product_ids = AnnualProcurementPlan.objects.filter(
                department=user_dept,
                year=current_year
            ).values_list('product_id', flat=True)
            
            # FALLBACK: If no current year, check previous year (matching home view logic)
            if not allocated_product_ids:
                allocated_product_ids = AnnualProcurementPlan.objects.filter(
                    department=user_dept,
                    year=current_year - 1
                ).values_list('product_id', flat=True)

            if allocated_product_ids:
                # Filter search results to only allocated products
                products = products.filter(id__in=list(allocated_product_ids))
        
        products = products.order_by('category__name', 'name')
        total_count_all = products.count()
        
        valid_category_ids = products.values_list('category_id', flat=True).distinct()
        categories = Category.objects.filter(id__in=valid_category_ids).annotate(
            product_count=Count('product', filter=Q(product__id__in=products.values_list('id', flat=True)))
        ).order_by('name')

        # --- PAGINATION (Search Results) ---
        paginator = Paginator(products, 12)
        page = request.GET.get('page')
        try:
            products_paginated = paginator.page(page)
        except PageNotAnInteger:
            products_paginated = paginator.page(1)
        except EmptyPage:
            products_paginated = paginator.page(paginator.num_pages)

        if user_dept:
            now = timezone.now()
            month_str = now.strftime('%b').lower()
            current_cart = request.session.get('cart', {})
            current_year = now.year

            for p in products_paginated:
                try:
                    plan = AnnualProcurementPlan.objects.get(
                        department=user_dept, 
                        product=p, 
                        year=current_year
                    )
                    limit = getattr(plan, month_str, 0)
                except AnnualProcurementPlan.DoesNotExist:
                    limit = 0
                
                monthly_orders = Order.objects.filter(
                    department=user_dept,
                    created_at__year=current_year,
                    created_at__month=now.month
                ).exclude(status='cancelled')
                
                consumed = OrderItem.objects.filter(
                    order__in=monthly_orders,
                    product=p
                ).aggregate(total=Sum('quantity'))['total'] or 0
                
                in_cart = current_cart.get(str(p.id), 0)
                p.personal_stock = max(0, limit - (consumed + in_cart))
        
        # Latest News
        urgent_news = News.objects.filter(is_active=True, urgency='URGENT').order_by('-date_posted')[:3]
    
    return render(request, 'supplies/home.html', {
        'products': products, 
        'categories': categories, 
        'search_query': query,
        'total_count_all': total_count_all,
        'urgent_news': urgent_news,
    })

# --- PRODUCT DETAIL ---
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

    # --- LOGIC REBUILD: Department Allocation Limit Check ---
    # --- LOGIC REBUILD: Department Allocation Limit Check ---
    # Principle: "app allocation links to user/department/stock value limit"
    
    current_cart_qty = cart.get(product_id, 0)
    
    is_allowed, error_msg, remaining = check_monthly_allocation(
        request.user, product_id, quantity, current_cart_qty=current_cart_qty
    )
    
    if not is_allowed:
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
        else:
            return redirect('home')

    # Add to Cart Logic
    if product_id in cart:
        cart[product_id] += quantity
    else:
        cart[product_id] = quantity
    
    request.session['cart'] = cart
    request.session.modified = True 
    
    # CRITICAL FIX: Calculate total quantity of items
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
                # --- SECURITY FIX: Check Limit ---
                is_allowed, _, _ = check_monthly_allocation(
                    request.user, product_id, quantity, current_cart_qty=0
                )
                if is_allowed:
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
                
                # --- SECURITY FIX: Final Gatekeeper ---
                # Ensure even at checkout, limits are respected.
                is_allowed, _, _ = check_monthly_allocation(request.user, pid, qty, current_cart_qty=0)
                if not is_allowed:
                    continue

                total += prod.price * qty
                valid_items[pid] = prod 
            except Product.DoesNotExist:
                continue

        if total == 0 and not valid_items:
            request.session['cart'] = {}
            return redirect('view_cart')

        dept_name = request.POST.get('department', 'General')
        dept_obj = Department.objects.filter(name=dept_name).first()

        order = Order.objects.create(
            user=request.user,
            employee_name=request.POST.get('name', 'Unknown'),
            department=dept_obj,
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

    departments = Department.objects.all().order_by('name')
    return render(request, 'supplies/checkout.html', {'departments': departments})


@login_required
def checkout_finalize(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)

    if order.status != 'draft':
        return redirect('order_success', order_id=order.id)

    if request.method == 'POST':
        form = OrderDocumentForm(request.POST, request.FILES, instance=order)
        if form.is_valid():
            # JUST UPDATE STATUS - DO NOT DEDUCT STOCK OR APP YET
            # Deduction happens on Admin Approval
            order = form.save(commit=False)
            order.status = 'pending'
            order.save()

            # Clear Cart
            request.session['cart'] = {}
            request.session.modified = True
            return redirect('order_success', order_id=order.id)
        else:
            # If form is invalid, re-render with errors
            return render(request, 'supplies/checkout_finalize.html', {'order': order, 'form': form})

    form = OrderDocumentForm(instance=order)
    return render(request, 'supplies/checkout_finalize.html', {'order': order, 'form': form})


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
    # 1. Request History (Full ledger for institutional transparency)
    my_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # 2. Predictive Replenishment Logic
    # Identify top 4 most frequently purchased products by this user across all history
    frequent_items = OrderItem.objects.filter(
        order__user=request.user
    ).values('product').annotate(
        count=Count('product')
    ).order_by('-count')[:4]
    
    suggested_products = []
    if frequent_items:
        product_ids = [item['product'] for item in frequent_items]
        # Maintain order of frequency
        preserved_order = {id: i for i, id in enumerate(product_ids)}
        suggested_products = sorted(
            Product.objects.filter(id__in=product_ids),
            key=lambda x: preserved_order.get(x.id)
        )
    
    # Strategy B: Fallback (If no history or not enough suggestions)
    if len(suggested_products) < 4:
        additional_needed = 4 - len(suggested_products)
        exclude_ids = [p.id for p in suggested_products]
        
        # Pull diverse items from the general catalog
        fallback_items = Product.objects.exclude(id__in=exclude_ids).order_by('?')[:additional_needed]
        suggested_products = list(suggested_products) + list(fallback_items)

    # Fetch emergency requests
    emergency_requests = EmergencyRequest.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'supplies/profile.html', {
        'orders': my_orders,
        'emergency_requests': emergency_requests,
        'suggested_products': suggested_products
    })

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
            # Simple permission check
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

    # Fetch Issued By User (spmo_admin2)
    from django.contrib.auth.models import User
    issued_by_user = User.objects.filter(username='spmo_admin2').first()

    # Fetch Emergency Context if applicable
    emergency_req = None
    if order and order.is_emergency:
        from ..models import EmergencyRequest
        emergency_req = EmergencyRequest.objects.filter(linked_order=order).first()

    context = {
        'cart_items': cart_items,
        'total': total,
        'user': request.user,
        'date': timezone.now(),
        'order': order,
        'emergency_req': emergency_req,
        'issued_by_user': issued_by_user,
    }

    # --- BROWSER PRINT STRATEGY ---
    # Return standard HTML. The template contains @media print CSS for A4 formatting.
    return render(request, 'supplies/requisition_slip.html', context)

@login_required
def emergency_request_submit(request):
    if request.method == 'POST':
        justification = request.FILES.get('justification_letter')
        supplemental = request.FILES.get('supplemental_app')
        remarks = request.POST.get('remarks', '')
        
        if not justification or not supplemental:
            from django.contrib import messages
            messages.error(request, "Both Justification Letter and Supplemental APP are required.")
            return redirect('home')

        from ..models import EmergencyRequest
        emergency_req = EmergencyRequest.objects.create(
            user=request.user,
            department=request.user.profile.department if hasattr(request.user, 'profile') else None,
            justification_letter=justification,
            supplemental_app=supplemental,
            remarks=remarks,
            status='pending_ao'
        )
        
        from django.contrib import messages
        messages.success(request, f"Emergency Request #EMG-{emergency_req.id} submitted successfully. Pending Admin Officer (Aaron) validation.")
        return redirect('profile')
        
    return redirect('home')

@login_required
def emergency_cockpit(request):
    # God-Mode Bypass: Superusers don't strictly need a profile for the cockpit
    if request.user.is_superuser:
        role = 'store_sup' # Treat as Supervisor for UI context
    else:
        try:
            if not request.user.profile.is_supply_officer:
                return redirect('home')
            role = request.user.profile.role
        except UserProfile.DoesNotExist:
            return redirect('home')
    
    if request.user.is_superuser:
        # God-Mode: See all pending validation/approval stages
        active_requests = EmergencyRequest.objects.filter(
            status__in=['pending_ao', 'pending_supervisor', 'pending_chief']
        )
    elif role == 'store_ao':
        active_requests = EmergencyRequest.objects.filter(status='pending_ao')
    elif role == 'store_sup':
        active_requests = EmergencyRequest.objects.filter(status='pending_supervisor')
    elif role == 'spmo_chief':
        active_requests = EmergencyRequest.objects.filter(status='pending_chief')
    else:
        active_requests = EmergencyRequest.objects.none()
        
    all_requests = EmergencyRequest.objects.all().order_by('-created_at')
    
    return render(request, 'supplies/emergency_cockpit.html', {
        'active_requests': active_requests,
        'all_requests': all_requests
    })

@login_required
def emergency_request_action(request, pk, action):
    # God-Mode Bypass
    if request.user.is_superuser:
        role = 'store_sup'
    else:
        try:
            if not request.user.profile.is_supply_officer:
                return redirect('home')
            role = request.user.profile.role
        except UserProfile.DoesNotExist:
            return redirect('home')
        
    emg_req = get_object_or_404(EmergencyRequest, pk=pk)
    
    if action == 'approve':
        if role == 'store_ao' and emg_req.status == 'pending_ao':
            emg_req.status = 'pending_supervisor'
        elif role == 'store_sup' and emg_req.status == 'pending_supervisor':
            emg_req.status = 'pending_chief'
        elif role == 'spmo_chief' and emg_req.status == 'pending_chief':
            emg_req.status = 'approved'
        if request.user.is_superuser:
            # God-Mode: Universal Advance
            if emg_req.status == 'pending_ao':
                emg_req.status = 'pending_supervisor'
                messages.success(request, f"God-Mode: Request #EMG-{emg_req.id} advanced to Supervisor Review.")
            elif emg_req.status == 'pending_supervisor':
                emg_req.status = 'pending_chief'
                messages.success(request, f"God-Mode: Request #EMG-{emg_req.id} advanced to Chief Approval.")
            elif emg_req.status == 'pending_chief':
                emg_req.status = 'approved'
                messages.success(request, f"God-Mode: Request #EMG-{emg_req.id} FULLY APPROVED.")
        else:
            # Standard Role-Based Logic
            if role == 'store_ao' and emg_req.status == 'pending_ao':
                emg_req.status = 'pending_supervisor'
                messages.success(request, f"Request #EMG-{emg_req.id} validated by AO. Now pending Supervisor review.")
            elif role == 'store_sup' and emg_req.status == 'pending_supervisor':
                emg_req.status = 'pending_chief'
                messages.success(request, f"Request #EMG-{emg_req.id} reviewed by Supervisor. Now pending Chief approval.")
            elif role == 'spmo_chief' and emg_req.status == 'pending_chief':
                emg_req.status = 'approved'
                messages.success(request, f"Request #EMG-{emg_req.id} fully approved. Department can now access the form.")
        
        emg_req.save()
    elif action == 'reject':
        emg_req.status = 'rejected'
        emg_req.remarks = request.POST.get('remarks', 'Rejected by ' + request.user.username)
        emg_req.save()
        messages.warning(request, f"Request #EMG-{emg_req.id} has been rejected.")
        
    return redirect('emergency_cockpit')

# ==========================================
# FIFO PRICING ENGINE
# ==========================================

def get_fifo_price(product, quantity):
    """
    Calculates the total cost for a quantity of product using FIFO logic.
    Does NOT deduct stock, only calculates quote.
    """
    batches = StockBatch.objects.filter(product=product, quantity_remaining__gt=0).order_by('date_received', 'id')
    total_cost = Decimal('0.00')
    remaining_to_calculate = int(quantity)
    
    for batch in batches:
        if remaining_to_calculate <= 0:
            break
            
        take_from_this_batch = min(batch.quantity_remaining, remaining_to_calculate)
        total_cost += take_from_this_batch * batch.cost_per_item
        remaining_to_calculate -= take_from_this_batch
        
    # If we couldn't fulfill the quantity from current batches, use the product's default price for the rest
    if remaining_to_calculate > 0:
        total_cost += remaining_to_calculate * product.price
        
    return total_cost

@login_required
def get_fifo_quote(request):
    """AJAX endpoint for real-time pricing"""
    product_id = request.GET.get('product_id')
    quantity = request.GET.get('quantity', 0)
    
    if not product_id or not quantity:
        return JsonResponse({'error': 'Invalid parameters'}, status=400)
        
    product = get_object_or_404(Product, pk=product_id)
    total_price = get_fifo_price(product, quantity)
    
    return JsonResponse({
        'total_price': float(total_price),
        'unit_price_avg': float(total_price / int(quantity)) if int(quantity) > 0 else 0
    })

# ==========================================
# EMERGENCY ORDER FLOW
# ==========================================

@login_required
def emergency_order_form(request, req_id):
    # Ensure user has an APPROVED request
    emg_req = get_object_or_404(EmergencyRequest, pk=req_id, user=request.user, status='approved')
    products = Product.objects.all().order_by('name')
    
    return render(request, 'supplies/emergency_form.html', {
        'emg_req': emg_req,
        'products': products
    })

@login_required
@transaction.atomic
def emergency_order_finalize(request, req_id):
    if request.method != 'POST':
        return redirect('home')
        
    emg_req = get_object_or_404(EmergencyRequest, pk=req_id, user=request.user, status='approved')
    
    product_ids = request.POST.getlist('product_ids[]')
    quantities = request.POST.getlist('quantities[]')
    
    if not product_ids or not quantities or len(product_ids) != len(quantities):
        messages.error(request, "Requisition data is incomplete or corrupted.")
        return redirect('emergency_order_form', req_id=req_id)
        
    # Phase 1: Verification & Calculation
    total_order_amount = Decimal('0.00')
    items_to_create = []
    
    for i in range(len(product_ids)):
        p_id = product_ids[i]
        qty = int(quantities[i])
        
        if qty <= 0: continue
        
        product = get_object_or_404(Product, pk=p_id)
        item_total_cost = get_fifo_price(product, qty)
        
        total_order_amount += item_total_cost
        items_to_create.append({
            'product': product,
            'quantity': qty,
            'price': item_total_cost / qty
        })

    if not items_to_create:
        messages.error(request, "No valid items selected.")
        return redirect('emergency_order_form', req_id=req_id)
        
    # Phase 2: Creation
    order = Order.objects.create(
        user=request.user,
        employee_name=request.user.get_full_name() or request.user.username,
        department=request.user.profile.department,
        total_amount=total_order_amount,
        remarks=f"EMERGENCY REQUISITION (Ref: EMG-REQ #{emg_req.id})",
        is_emergency=True,
        status='pending'
    )
    
    for item in items_to_create:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            quantity=item['quantity'],
            price=item['price']
        )
    
    # Phase 3: Transition
    emg_req.status = 'completed'
    emg_req.linked_order = order
    emg_req.save()
    
    messages.success(request, f"Emergency Requisition #{order.id} established. Pending final admin validation.")
    return redirect('profile')

@login_required
def get_fifo_quote_bulk(request):
    """AJAX endpoint for multi-item real-time pricing"""
    import json
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
    except:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
    grand_total = Decimal('0.00')
    results = []
    
    for item in items:
        p_id = item.get('product_id')
        qty = int(item.get('quantity', 0))
        
        if p_id and qty > 0:
            product = Product.objects.get(pk=p_id)
            cost = get_fifo_price(product, qty)
            grand_total += cost
            results.append({
                'product_id': p_id,
                'total_cost': float(cost),
                'unit_avg': float(cost / qty)
            })
            
    return JsonResponse({
        'grand_total': float(grand_total),
        'items': results
    })
