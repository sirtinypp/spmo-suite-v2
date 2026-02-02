# suplay_app/supplies/views.py

@login_required
def home(request):
    # 1. Base Queryset
    products = Product.objects.all().order_by('category__name', 'name')

    # 2. Filter by Category
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    # 3. Filter by Supplier
    supplier_id = request.GET.get('supplier')
    if supplier_id:
        products = products.filter(supplier_id=supplier_id)

    # 4. Filter by Stock Status
    stock_status = request.GET.get('stock')
    if stock_status == 'in_stock':
        products = products.filter(stock__gt=0)
    elif stock_status == 'out_of_stock':
        products = products.filter(stock=0)
    
    # 5. Context Data
    categories = Category.objects.all().order_by('name')
    suppliers = Supplier.objects.all().order_by('name')
    
    return render(request, 'supplies/home.html', {
        'products': products,
        'categories': categories,
        'suppliers': suppliers,
        'selected_category': int(category_id) if category_id else None,
        'selected_supplier': int(supplier_id) if supplier_id else None,
        'selected_stock': stock_status,
        'search_query': None
    })
