from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats
from .models import Category, Product, Order, OrderItem, StockBatch, Supplier, UserProfile, AnnualProcurementPlan, Department, News
from django.db.models import Max

# --- 1. PRODUCT RESOURCE (For Master List Upload) ---
class ProductResource(resources.ModelResource):
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, field='name')
    )
    supplier = fields.Field(
        column_name='supplier',
        attribute='supplier',
        widget=ForeignKeyWidget(Supplier, field='name')
    )

    class Meta:
        model = Product
        # This maps the CSV headers to the Database fields
        fields = ('id', 'name', 'item_code', 'brand', 'description', 'price', 'category', 'supplier', 'unit', 'reorder_point', 'stock')
        import_id_fields = ('item_code',)

    def before_import_row(self, row, **kwargs):
        """
        1. Allow 'stock' to be left blank (defaults to 0).
        2. SMART MAP: Map 'Item Code', 'Brand', etc. from various CSV header styles.
        """
        # Stock Default
        if 'stock' not in row or row['stock'] in (None, ''):
            row['stock'] = 0

        # Smart Map: Item Code
        if 'item_code' not in row:
            for key in ['Item Code', 'ItemCode', 'ITEM CODE', 'Item Code PSDB']:
                if key in row:
                    row['item_code'] = row[key]
                    break
        
        # Smart Map: Brand
        if 'brand' not in row:
            for key in ['Brand', 'BRAND']:
                if key in row:
                    row['brand'] = row[key]
                    break
        
        # Smart Map: Unit
        if 'unit' not in row:
            for key in ['Unit', 'UoM', 'UOM', 'Unit of Measure']:
                if key in row:
                    row['unit'] = row[key]
                    break

    def before_import(self, dataset, **kwargs):
        """
        Auto-create Categories and Suppliers if they don't exist.
        """
        # 1. Auto-Create Categories
        if 'category' in dataset.headers:
            categories = set(dataset['category'])
            for cat_name in categories:
                if cat_name and str(cat_name).strip():
                    Category.objects.get_or_create(name=str(cat_name).strip())

        # 2. Auto-Create Suppliers
        if 'supplier' in dataset.headers:
            suppliers = set(dataset['supplier'])
            for sup_name in suppliers:
                if sup_name and str(sup_name).strip():
                    Supplier.objects.get_or_create(name=str(sup_name).strip())

# --- 2. STOCK BATCH RESOURCE (For Replenishment via Item Code) ---
class StockBatchResource(resources.ModelResource):
    # This tells Django: "Look at the 'item_code' column in the CSV, 
    # search for a Product with that item_code, and link it."
    product = fields.Field(
        column_name='item_code',
        attribute='product',
        widget=ForeignKeyWidget(Product, field='item_code')
    )

    class Meta:
        model = StockBatch
        # These are the headers your CSV MUST have
        fields = ('id', 'product', 'supplier_name', 'batch_number', 'quantity_initial', 'quantity_remaining', 'cost_per_item', 'date_received')

    def before_import_row(self, row, **kwargs):
        """
        1. Parse numbers (remove commas in cost/quantity).
        2. Set quantity_remaining = quantity_initial automatically.
        """
        # Clean Cost
        if 'cost_per_item' in row:
            try:
                # Remove commas, strip spaces
                val = str(row['cost_per_item']).replace(',', '').strip()
                row['cost_per_item'] = val
            except:
                pass

        # Clean Quantity & Set Remaining
        if 'quantity_initial' in row:
            try:
                val = str(row['quantity_initial']).replace(',', '').strip()
                row['quantity_initial'] = val
                # Auto-set remaining
                row['quantity_remaining'] = val
            except:
                pass
    
    def after_save_instance(self, instance, *args, **kwargs):
        """
        After the batch is uploaded, automatically update the Main Product's 
        stock level and price.
        """
        # Safely get dry_run from kwargs (usually passed as kwarg in newer versions)
        # If passed as positional, it's hard to guess index, but usually we only care if it's explicitly True.
        # Let's check both just in case, assuming typical positions.
        # Unpack: (instance, using_transactions, dry_run) is common for old versions.
        
        dry_run = kwargs.get('dry_run', False)
        
        # Fallback for positional dry_run (index 1 if signature is instance, using_transactions, dry_run)
        if len(args) > 1 and isinstance(args[1], bool):
             dry_run = args[1]

        if not dry_run:
            try:
                # 1. Get the product linked to this batch
                product_to_update = instance.product
                
                # 2. Add the new quantity (Handle None case)
                current_stock = product_to_update.stock or 0
                product_to_update.stock = current_stock + instance.quantity_initial
                
                # 3. Update the price
                product_to_update.price = instance.cost_per_item
                
                # 4. Save Product changes
                product_to_update.save()
            except Exception as e:
                print(f"Error updating product stock: {e}")

# --- ADMIN REGISTRATIONS ---

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    list_display = ('name', 'description')

# --- CUSTOM FILTERS ---
class StockStatusFilter(admin.SimpleListFilter):
    title = 'Stock Status'
    parameter_name = 'stock_status'

    def lookups(self, request, model_admin):
        return (
            ('in_stock', 'In Stock'),
            ('out_of_stock', 'Out of Stock'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'in_stock':
            return queryset.filter(stock__gt=0)
        if self.value() == 'out_of_stock':
            return queryset.filter(stock=0)

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    # Shows Item Code, Name, and Brand in the list
    list_display = ('item_code', 'name', 'brand', 'category', 'supplier', 'price', 'stock')
    search_fields = ('name', 'item_code', 'brand') 
    list_filter = ('category', 'brand', 'supplier', StockStatusFilter)

@admin.register(StockBatch)
class StockBatchAdmin(ImportExportModelAdmin):
    resource_class = StockBatchResource
    # Shows Batch info in the list
    list_display = ('get_item_code', 'get_product_name', 'batch_number', 'quantity_remaining', 'date_received')
    list_filter = ('date_received',)
    
    # Helper to show product info in the Batch list
    def get_item_code(self, obj):
        return obj.product.item_code
    get_item_code.short_description = 'Item Code'

    def get_product_name(self, obj):
        return obj.product.name
    get_product_name.short_description = 'Product Name'

# --- 3. ORDER RESOURCE (Transactions Export) ---
class OrderResource(resources.ModelResource):
    department = fields.Field(
        column_name='department',
        attribute='department',
        widget=ForeignKeyWidget(Department, field='name')
    )
    class Meta:
        model = Order
        fields = ('id', 'created_at', 'employee_name', 'department', 'total_amount', 'status', 'remarks', 'approved_at', 'completed_at')
        export_order = ('id', 'created_at', 'employee_name', 'department', 'total_amount', 'status')

@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    resource_class = OrderResource
    list_display = ('id', 'created_at', 'employee_name', 'department', 'total_amount', 'status')
    list_filter = ('status', 'department', 'created_at')
    search_fields = ('id', 'employee_name', 'department__name')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

# --- 4. APP RESOURCE (Smart Importer with Auto-Detect) ---
class FlatAPPResource(resources.ModelResource):
    """
    Smart Resource for importing APP files.
    - DETECTS: Raw (Flat) vs Processed (Matrix)
    - NORMALIZES: Office names using DEPARTMENT_MAPPING
    - AGGREGATES: Multiple monthly rows into single Matrix rows
    """
    department = fields.Field(
        attribute='department', 
        column_name='Office',
        widget=ForeignKeyWidget(Department, field='name')
    )
    product = fields.Field(
        attribute='product', 
        column_name='Item Code', 
        widget=ForeignKeyWidget(Product, field='item_code')
    )
    
    class Meta:
        model = AnnualProcurementPlan
        # We always target the Matrix format of the Model
        fields = ('id', 'department', 'product', 'year', 'date_requested', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec')
        import_id_fields = ('department', 'product', 'year')
        skip_unchanged = True
        report_skipped = True

    def before_import(self, dataset, **kwargs):
        """
        SMART AUTO-DETECT LOGIC
        """
        # --- 0. DEPARTMENT MAPPING DICTIONARY ---
        DEPARTMENT_MAPPING = {
            "Accounting Office": "System Accounting Office (SAO)",
            "Cash Office": "System Cash Office (SCO)",
            "Supply and Property Management Office (SPMO)": "System Supply and Property Management Office (SSPMO)",
            "Human Resource Development Office (HRDO)": "System Human Resource Development Office (SHRDO)",
            "Information Technology Development Center (ITDC)": "UP Information Technology Development Center (UP ITDC)",
            "CIFAL": "UP CIFAL Philippines",
            "COA-SYSTEM": "Commission on Audit (COA-System)",
            "Center for Integrative Development Studies (CIDS)": "UP Center for Integrative and Development Studies (UP CIDS)",
            "Center for Women and Gender Studies (CWGS)": "UP Center for Women’ and Gender Studies (UP CWGS)",
            "Digital transformation": "Office of the Vice President for Digital Transformation (OVPDX)",
            "Executive House": "Office of the President (OP)",
            "Media and Public Relation (MPRO)": "UP Media and Public Relations Office (UP MPRO)",
            "Office of Admissions": "Office of Admissions (OADMS)",
            "Office of Alumni Relation (OAR)": "Office of Alumni Relations (OAR)",
            "Office of Design and Planning Initiatives (ODPI)": "Office of Design and Planning Initiative (ODPI)",
            "Office of the Vice President for Planning and Finance (OVPPF)": "Office of the Vice President for Planning & Finance (OVPPF)",
            "TVUP": "Television network operated by the University of the Philippines (TVUP)",
            "UP Bonifacio Global City (UPBGC)": "UP Bonifacio Global City Campus (UP-BGC)",
            "UP Intelligent System Center": "UP Intelligent Systems Center (ISC)",
            "UP Korea Research Center (UPKRC)": "UP Korea Research Center (UP KRC)",
            "UP Procurement Unit": "System Procurement Office (SPO)",
            "Ugnayan ng Pahinungod": "UP Ugnayan ng Pahinungod Office"
        }

        # --- 1. DETECT FORMAT ---
        headers = [h.strip() for h in dataset.headers] if dataset.headers else []
        
        # CASE A: Raw Source (Flat Format)
        # Check for key columns: "Office" AND "Month"
        if "Office" in headers and "Month" in headers:
            print(">> DETECTED: RAW FLAT FORMAT. Transformation Routine Engaged.")
            
            aggregated_data = {} # Key: (Normalized_Office, Item_Code) -> Data Dict
            
            month_map = {
                'jan': 'jan', 'feb': 'feb', 'mar': 'mar', 'apr': 'apr', 'may': 'may', 'jun': 'jun',
                'jul': 'jul', 'aug': 'aug', 'sep': 'sep', 'oct': 'oct', 'nov': 'nov', 'dec': 'dec',
                'january': 'jan', 'february': 'feb', 'march': 'mar', 'april': 'apr', 'june': 'jun', 
                'july': 'jul', 'august': 'aug', 'september': 'sep', 'october': 'oct', 'november': 'nov', 'december': 'dec'
            }

            for row in dataset:
                row_dict = dict(zip(dataset.headers, row))
                
                # A. Normalize Office
                raw_office = row_dict.get('Office', '').strip()
                office_name = DEPARTMENT_MAPPING.get(raw_office, raw_office) # Map or keep original
                
                # B. Get Item Code
                item_code = row_dict.get('Item Code PSDB', row_dict.get('Item Code', '')).strip()

                if not office_name or not item_code:
                    continue # Skip empty rows

                # C. Initialize Key
                unique_key = (office_name, item_code)
                
                # Smart Year Detection:
                # 1. Try to find 'Year' in the row
                # 2. Defaults to Current Year if missing
                try:
                     row_year = int(str(row_dict.get('Year', row_dict.get('year', timezone.now().year))).strip())
                except:
                     row_year = timezone.now().year

                if unique_key not in aggregated_data:
                    aggregated_data[unique_key] = {
                        'Office': office_name,
                        'Item Code': item_code,
                        'year': row_year,
                        'Date Requested': row_dict.get('Date Requested', None),
                        'jan':0, 'feb':0, 'mar':0, 'apr':0, 'may':0, 'jun':0,
                        'jul':0, 'aug':0, 'sep':0, 'oct':0, 'nov':0, 'dec':0
                    }
                else:
                    # Update Date if later
                    new_date = row_dict.get('Date Requested', '')
                    current_date = aggregated_data[unique_key]['Date Requested']
                    if new_date and (not current_date or new_date > current_date):
                        aggregated_data[unique_key]['Date Requested'] = new_date

                # D. Parse Month & Quantity
                month_str = row_dict.get('Month', '').strip().lower()
                target_field = month_map.get(month_str[:3], None) # Try 3-letter prefix
                
                try:
                    qty = int(float(str(row_dict.get('QTY', row_dict.get('Quantity', 0))).replace(',', '')))
                except ValueError:
                    qty = 0

                if target_field:
                    aggregated_data[unique_key][target_field] += qty

            # --- E.1. Pre-Check for Missing Products & Auto-Create ---
            # Get all unique item codes from the import
            import_codes = set(d['Item Code'] for d in aggregated_data.values() if d['Item Code'])
            
            # Find which ones exist in DB
            existing_codes = set(Product.objects.filter(item_code__in=import_codes).values_list('item_code', flat=True))
            missing_codes = import_codes - existing_codes
            
            if missing_codes:
                print(f">> Auto-Creating {len(missing_codes)} missing products...")
                default_category, _ = Category.objects.get_or_create(name="Uncategorized")
                
                new_products = []
                for code in missing_codes:
                    new_products.append(Product(
                        item_code=code,
                        name=f"[AUTO-CREATED] Item {code}",
                        description="Auto-created during APP Import. Please update details.",
                        price=1.00, # Dummy price
                        category=default_category,
                        stock=0
                    ))
                Product.objects.bulk_create(new_products)

            # E.2. Rebuild Dataset as Matrix
            new_data = []
            for data in aggregated_data.values():
                # Auto-Create Normalized Department if missing
                if data['Office']:
                    Department.objects.get_or_create(name=data['Office'])
                
                new_row = [
                    data['Office'],
                    data['Item Code'],
                    data['year'],
                    data['Date Requested'],
                    data['jan'], data['feb'], data['mar'], data['apr'], data['may'], data['jun'],
                    data['jul'], data['aug'], data['sep'], data['oct'], data['nov'], data['dec']
                ]
                new_data.append(new_row)

            # F. Replace Dataset Content
            dataset.wipe()
            dataset.headers = ['Office', 'Item Code', 'year', 'date_requested', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
            for row in new_data:
                dataset.append(row)

        # CASE B: Processed (Matrix Format)
        # Check for "department" OR "Office" but NO "Month"
        elif "jan" in headers or "Jan" in headers:
             print(">> DETECTED: MATRIX FORMAT. Proceeding with Direct Mapping.")
             # Only normalization might be needed if user uploaded matrix with raw office names
             # Optional: Check if we want to normalize 'Office' column here too?
             # For now, assuming Matrix upload follows strict headers OR we just let standard logic handle it.
             # If "Office" is in headers and we mapped it to 'department', standard import uses lookup.
             # If headers match standard fields, we are good.
             pass
        
        else:
            print(">> WARNING: Unknown Format. Attempting Auto-Import.")

@admin.register(AnnualProcurementPlan)
class APPAdmin(ImportExportModelAdmin):
    resource_class = FlatAPPResource
    list_display = ('department', 'get_category', 'product', 'year', 'quantity_approved', 'quantity_consumed', 'remaining_balance')
    list_filter = ('department', 'year', 'product__category')
    search_fields = ('product__name', 'department__name') # Foreign key search syntax
    ordering = ('department__name', 'product__category__name') 

    def get_category(self, obj):
        return obj.product.category.name if obj.product.category else '-'
    get_category.short_description = 'Category'
    get_category.admin_order_field = 'product__category__name'

    # --- CUSTOM ACTION: Export as Flat CSV ---
    def export_as_flat_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="APP_Allocation_Flat.csv"'
        writer = csv.writer(response)

        # 2. Write Headers (User's Exact Schema)
        headers = ['Office', 'Date Requested', 'Month', 'Item Code', 'Item Name', 'Category', 'Quantity']
        writer.writerow(headers)

        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        for obj in queryset:
            category = obj.product.category.name if obj.product.category else ''
            item_name = obj.product.name
            office = obj.department.name # FK
            item_code = obj.product.item_code
            date_req = obj.date_requested.strftime('%Y-%m-%d') if obj.date_requested else ''

            for i, month_field in enumerate(months):
                qty = getattr(obj, month_field, 0)
                if qty > 0:
                    writer.writerow([
                        office,
                        date_req,
                        month_labels[i],
                        item_code,
                        item_name,
                        category,
                        qty
                    ])
        
        return response
    
    export_as_flat_csv.short_description = "Export Selected as Flat CSV"

    actions = ['export_as_flat_csv']
    
    def get_import_formats(self):
        return [base_formats.CSV, base_formats.XLSX]

    def get_export_formats(self):
        return [base_formats.CSV, base_formats.XLSX]

# --- 5. USER PROFILE EXTENSION (INLINE) ---
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile (Role & Department)'
    fk_name = 'user'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role', 'get_department')
    list_select_related = ('profile', 'profile__department')

    def get_role(self, instance):
        return instance.profile.get_role_display()
    get_role.short_description = 'Role'

    def get_department(self, instance):
        return instance.profile.department
    get_department.short_description = 'Department'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_posted', 'is_active')
    list_filter = ('is_active', 'date_posted')
    search_fields = ('title', 'content')