from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q, Count
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from io import BytesIO
from xhtml2pdf import pisa

from ..models import Product, Category, Order, OrderItem, AnnualProcurementPlan, Supplier, StockBatch, News, Department

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
    
    # --- CALCULATE MONTHLY PERSONAL STOCK (MOVED) ---
    # Convert to list AFTER filters are applied
    products = list(products)
    
    if request.user.is_authenticated and user_dept:
        now = timezone.now()
        month_str = now.strftime('%b').lower()
        current_cart = request.session.get('cart', {})
        current_year = now.year
        
        for p in products:
            try:
                plan = AnnualProcurementPlan.objects.get(
                    department=user_dept, 
                    product=p, 
                    year=current_year
                )
                limit = getattr(plan, month_str, 0)
            except AnnualProcurementPlan.DoesNotExist:
                limit = 0
            
            # Re-fetch consumed (Optimization: extract this to helper function?)
            # For now, inline is fine.
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
    
    # Newly Added (Last 30 days)
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    product_ids = [p.id for p in products]
    newly_added = Product.objects.filter(created_at__gte=thirty_days_ago, id__in=product_ids).order_by('-created_at')[:5]
    
    # Latest News
    news_items = News.objects.filter(is_active=True).order_by('-date_posted')[:5]

    context = {
        'products': products,
        'categories': categories,
        'suppliers': suppliers,
        'newly_added': newly_added,
        'news_items': news_items,
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
            
            # Filter search results to only allocated products
            products = products.filter(id__in=list(allocated_product_ids))
        else:
            # No department = no products
            products = Product.objects.none()
        
        products = products.order_by('category__name', 'name')
        valid_category_ids = products.values_list('category_id', flat=True).distinct()
        categories = Category.objects.filter(id__in=valid_category_ids).order_by('name')

        # --- CALCULATE MONTHLY PERSONAL STOCK (SEARCH) ---
        products = list(products)
        if user_dept:
            now = timezone.now()
            month_str = now.strftime('%b').lower()
            current_cart = request.session.get('cart', {})
            current_year = now.year

            for p in products:
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
        else:
            # If no dept, personal_stock not relevant/used, or 0
            pass
    
    return render(request, 'supplies/home.html', {
        'products': products, 
        'categories': categories, 
        'search_query': query
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
        last_item = last_order.items.first()
        if last_item:
            target_category = last_item.product.category
            suggested_products = Product.objects.filter(category=target_category).exclude(id=last_item.product.id).order_by('?')[:4]

    # Strategy B: Fallback (If no history or not enough suggestions)
    if not suggested_products or len(suggested_products) < 4:
        additional_needed = 4 - len(suggested_products)
        ids_to_exclude = [p.id for p in suggested_products]
        fallback_items = Product.objects.exclude(id__in=ids_to_exclude).order_by('?')[:additional_needed]
        # Combine them
        import itertools
        suggested_products = list(itertools.chain(suggested_products, fallback_items))

    return render(request, 'supplies/profile.html', {
        'orders': my_orders,
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

    context = {
        'cart_items': cart_items,
        'total': total,
        'user': request.user,
        'date': timezone.now(),
        'order': order,
        'issued_by_user': issued_by_user,
    }

    # --- BROWSER PRINT STRATEGY ---
    # Return standard HTML. The template contains @media print CSS for A4 formatting.
    return render(request, 'supplies/requisition_slip.html', context)
