from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    def __str__(self): return self.name
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    is_ps_dbm = models.BooleanField(default=False, verbose_name="Is Procurement Service (DBM)?")
    def __str__(self): return self.name
    class Meta: ordering = ['name']

class Product(models.Model):
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100, blank=True, null=True)
    item_code = models.CharField(max_length=50, blank=True, null=True, help_text="Stock No / Item Code")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)
    unit = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., pc, box, ream")
    reorder_point = models.IntegerField(default=0, help_text="Alert when stock drops below this number")
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name
    class Meta: ordering = ['name']

class DeliveryRecord(models.Model):
    apr = models.ForeignKey('APRRequest', on_delete=models.CASCADE, related_name='deliveries')
    dr_number = models.CharField(max_length=100, verbose_name="Delivery Receipt No.")
    si_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Sales Invoice No.")
    
    # Document Scans
    dr_scan = models.FileField(upload_to='deliveries/dr/', blank=True, null=True)
    si_scan = models.FileField(upload_to='deliveries/si/', blank=True, null=True)
    signed_apr_scan = models.FileField(upload_to='deliveries/apr/', blank=True, null=True)
    
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_received = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self): return f"DR {self.dr_number} for APR {self.apr.apr_no}"

class StockBatch(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='batches')
    supplier_name = models.CharField(max_length=100, blank=True)
    batch_number = models.CharField(max_length=50, blank=True)
    quantity_initial = models.IntegerField()
    quantity_remaining = models.IntegerField()
    cost_per_item = models.DecimalField(max_digits=10, decimal_places=2)
    date_received = models.DateField(default=timezone.now)
    
    # Link to the Delivery Event (Audit Trail)
    delivery_record = models.ForeignKey(DeliveryRecord, on_delete=models.SET_NULL, null=True, blank=True, related_name='batches')
    
    # Legacy link (Keep for compatibility)
    apr_reference = models.ForeignKey('APRRequest', on_delete=models.SET_NULL, null=True, blank=True, related_name='received_batches')
    
    class Meta: ordering = ['date_received', 'id']
    def __str__(self): return f"{self.product.name} - Batch {self.batch_number}"

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    class Meta: ordering = ['name']

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Admin Validation (Aaron)'),
        ('for_approval', 'For Chief Approval (Isagani)'),
        ('approved', 'Ready for Pickup/Delivery'),
        ('delivered_pending_settlement', 'Delivered (Awaiting DV Upload)'),
        ('completed', 'Completed & Settled'),
        ('returned', 'Returned to Sender'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    employee_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    remarks = models.TextField(blank=True, null=True)
    
    # Settlement Fields (Institutional Hardening)
    dv_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="Disbursement Voucher No.")
    dv_file = models.FileField(upload_to='order_settlements/', blank=True, null=True)
    dv_uploaded_at = models.DateTimeField(blank=True, null=True)
    dv_verified_at = models.DateTimeField(blank=True, null=True)
    dv_verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='verified_settlements')

    # Workflow Logic
    admin_validated = models.BooleanField(default=False)
    chief_approved = models.BooleanField(default=False)
    
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True) # Request Time
    approved_at = models.DateTimeField(null=True, blank=True) # Approval Time
    completed_at = models.DateTimeField(null=True, blank=True) # Pickup/Delivery Time
    
    is_emergency = models.BooleanField(default=False)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    
    document1 = models.FileField(upload_to='order_documents/', blank=True, null=True)
    document2 = models.FileField(upload_to='order_documents/', blank=True, null=True)
    document3 = models.FileField(upload_to='order_documents/', blank=True, null=True)
    
    def __str__(self): return f"Order #{self.id} - {self.employee_name}"

class EmergencyRequest(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Drafting'),
        ('pending_ao', 'Pending Admin Officer Validation'),
        ('pending_supervisor', 'Pending Store Supervisor Review'),
        ('pending_chief', 'Pending Chief Final Approval'),
        ('approved', 'Approved - Form Access Granted'),
        ('rejected', 'Rejected / Needs Revision'),
        ('completed', 'Order Finalized'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emergency_requests')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    
    justification_letter = models.FileField(upload_to='emergency/justifications/')
    supplemental_app = models.FileField(upload_to='emergency/app_amendments/')
    
    remarks = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_ao')
    
    # Track the final order once approved
    linked_order = models.OneToOneField(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='emergency_meta')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"EMG-REQ #{self.id} - {self.department.name} ({self.status})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self): return f"{self.quantity}x {self.product.name}"

    @property
    def subtotal(self):
        return self.quantity * self.price

# ==========================================
# 2. PROCUREMENT MODULE (APR)
# ==========================================

class APRRequest(models.Model):
    DELIVERY_MODE_CHOICES = [
        ('PICKUP_FAST', 'Pick-up (Fast Lane)'),
        ('PICKUP_SCHEDULE', 'Pick-up (Schedule)'),
        ('DELIVERY', 'Delivery (door-to-door)'),
    ]
    FUND_ACTION_CHOICES = [
        ('REDUCE', 'Reduce Quantity'),
        ('BILL', 'Bill Us'),
        ('CHARGE_DEPOSIT', 'Charge to Unutilized Deposit'),
    ]
    STATUS_CHOICES = [
        ('DRAFT', 'Draft/Preparing'),
        ('VERIFICATION_PENDING', 'Pending Supervisor Verification'),
        ('VERIFIED', 'Verified & Released to Store'),
        ('PARTIAL', 'Partially Received'),
        ('CLOSED', 'Closed/Fully Received'),
        ('CANCELLED', 'Cancelled'),
    ]

    apr_no = models.CharField(max_length=50, unique=True, verbose_name="PS APR No.")
    control_no = models.CharField(max_length=50, blank=True, null=True, verbose_name="Agency Control No.")
    date_prepared = models.DateField(default=timezone.now)
    
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, limit_choices_to={'is_ps_dbm': True})
    
    mode_of_delivery = models.CharField(max_length=20, choices=DELIVERY_MODE_CHOICES, default='PICKUP_FAST')
    insufficient_fund_action = models.CharField(max_length=20, choices=FUND_ACTION_CHOICES, default='REDUCE')
    
    # Approvals
    prepared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='prepared_aprs')
    is_validated = models.BooleanField(default=False)
    is_chief_approved = models.BooleanField(default=False)
    is_head_approved = models.BooleanField(default=False)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='VERIFICATION_PENDING')
    has_unregistered_items = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='verified_aprs')
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Financial Snapshot
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    check_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="Check No. (If Paid)")
    
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"APR {self.apr_no} - {self.date_prepared}"

class APRItem(models.Model):
    apr = models.ForeignKey(APRRequest, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity_requested = models.PositiveIntegerField()
    quantity_received = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    remarks = models.TextField(blank=True, null=True)
    
    def __str__(self): return f"{self.quantity_requested}x {self.product.name if self.product else 'Unregistered'}"
    
    @property
    def total_amount(self): return self.quantity_requested * self.unit_price

    @property
    def quantity_received_neg(self):
        return -self.quantity_received

class ProcurementDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('INVOICE', 'Sales Invoice'),
        ('RECEIPT', 'Official Receipt (OR)'),
        ('DR', 'Delivery Receipt'),
        ('APR', 'Scanned APR Form'),
        ('INSPECTION', 'Inspection & Acceptance Report (IAR)'),
        ('OTHER', 'Other Supporting Doc'),
    ]
    
    apr = models.ForeignKey(APRRequest, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='procurement_docs/')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='OTHER')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self): return f"{self.get_document_type_display()} - {self.apr.apr_no}"

# ==========================================
# 3. SETTLEMENT MODULE
# ==========================================

class Settlement(models.Model):
    TYPE_CHOICES = [
        ('OUTGOING', 'Customer / Dept Order'),
        ('INCOMING', 'Supplier / APR Procurement'),
    ]
    
    settlement_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    order_id = models.PositiveIntegerField(help_text="The ID of the linked Order or APRRequest")
    
    is_settled = models.BooleanField(default=False)
    date_settled = models.DateField(blank=True, null=True)
    reference_no = models.CharField(max_length=150, help_text="DV No., Check No., or OR No.")
    
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2)
    attachment = models.FileField(upload_to='settlements/', blank=True, null=True)
    
    remarks = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"Settlement {self.settlement_type} - {self.reference_no}"

# ==========================================
# 4. ACCOUNTABILITY & CONFIG
# ==========================================

class AnnualProcurementPlan(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='plans', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    year = models.IntegerField(default=2025)
    date_requested = models.DateField(null=True, blank=True)

    # --- MONTHLY ALLOCATIONS ---
    jan = models.PositiveIntegerField(default=0, verbose_name="Jan")
    feb = models.PositiveIntegerField(default=0, verbose_name="Feb")
    mar = models.PositiveIntegerField(default=0, verbose_name="Mar")
    apr = models.PositiveIntegerField(default=0, verbose_name="Apr")
    may = models.PositiveIntegerField(default=0, verbose_name="May")
    jun = models.PositiveIntegerField(default=0, verbose_name="Jun")
    jul = models.PositiveIntegerField(default=0, verbose_name="Jul")
    aug = models.PositiveIntegerField(default=0, verbose_name="Aug")
    sep = models.PositiveIntegerField(default=0, verbose_name="Sep")
    oct = models.PositiveIntegerField(default=0, verbose_name="Oct")
    nov = models.PositiveIntegerField(default=0, verbose_name="Nov")
    dec = models.PositiveIntegerField(default=0, verbose_name="Dec")

    quantity_consumed = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('department', 'product', 'year') 
        verbose_name = "APP Allocation"
        ordering = ['department__name', 'product__name']

    @property
    def quantity_approved(self):
        return (self.jan + self.feb + self.mar + self.apr + self.may + self.jun + 
                self.jul + self.aug + self.sep + self.oct + self.nov + self.dec)

    def remaining_balance(self):
        return self.quantity_approved - self.quantity_consumed

    def __str__(self):
        return f"{self.department} | {self.product.name} | {self.year}"

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('dept_ao', 'Department Admin Officer'),
        ('unit_head', 'Head of Unit / Office'),
        ('store_ao', 'Store Admin Officer (Egay)'),
        ('store_sup', 'Store Supervisor (Aaron)'),
        ('spmo_chief', 'SSPMO Chief (Isagani)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='profiles')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='dept_ao')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()} - {self.department}"

    @property
    def is_dept_ao(self): return self.role == 'dept_ao'
    @property
    def is_unit_head(self): return self.role == 'unit_head'
    @property
    def is_store_ao(self): return self.role == 'store_ao' or self.user.is_superuser
    @property
    def is_store_supervisor(self): return self.role == 'store_sup' or self.user.is_superuser
    @property
    def is_supply_officer(self): return self.role in ['store_ao', 'store_sup', 'spmo_chief'] or self.user.is_superuser
    @property
    def is_chief(self): return self.role == 'spmo_chief' or self.user.is_superuser

    # Permission Scopes
    @property
    def can_manage_assets(self): return self.is_supply_officer
    @property
    def can_manage_procurement(self): return self.is_supply_officer
    @property
    def can_manage_fulfillment(self): return self.is_supply_officer
    @property
    def can_manage_finances(self): return self.is_supply_officer
    @property
    def can_manage_system(self): return self.is_supply_officer

class News(models.Model):
    URGENCY_CHOICES = [
        ('URGENT', 'Critical Alert / Pulse'),
        ('INFO', 'General News / Info'),
        ('SUCCESS', 'Success / Update'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES, default='INFO')
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    date_posted = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name_plural = "News"
        ordering = ['-date_posted']

    def __str__(self): return self.title

    @property
    def short_content(self):
        words = self.content.split()
        return " ".join(words[:20]) + "..." if len(words) > 20 else self.content