from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
import datetime

# 0. DEPARTMENT MODEL (New)
class Department(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Department / Office Name")
    
    def __str__(self): return self.name

    class Meta:
        ordering = ['name']

# 1. USER PROFILE
class UserProfile(models.Model):
    ROLE_CHOICES = [
        # Legacy (kept for backward compat)
        ('ADMIN_OFFICER', 'Admin Officer (Legacy)'),
        ('HEAD_OF_UNIT', 'Head of Unit'),
        ('USER', 'User (Staff)'),
        # Office-specific admin roles
        ('SPMO_ADMIN', 'Admin Officer — SPMO'),
        ('ACCT_ADMIN', 'Admin Officer — Accounting'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    office = models.CharField(max_length=100, blank=True, null=True, verbose_name="Assigned Office Access (Legacy)") # Kept for safety
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Department")
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='USER', verbose_name="User Role")
    
    def __str__(self): return f"{self.user.username} - {self.role}"

# 1.1 USER SIGNATURE (New for Workflow)
class UserSignature(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='signature')
    signature_image = models.ImageField(upload_to='signatures/', verbose_name="Digital Signature")
    position_title = models.CharField(max_length=150, verbose_name="Official Position Title")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return f"Signature: {self.user.username}"

# 2. MAIN ASSET MODEL
class Asset(models.Model):
    STATUS_CHOICES = [
        ('SERVICEABLE', 'Serviceable'), ('UNSERVICEABLE', 'Unserviceable'),
        ('DISPOSED', 'Disposed'), ('UNDER_REPAIR', 'Under Repair'),
        ('PENDING', 'Pending Approval'),
    ]
    # ... choices ...
    # 2. PPE CLASS CHOICES (Standardized to CSV)
    CLASS_CHOICES = [
        ('FURNITURE', 'Furniture and Fixtures'),
        ('ICT EQUIPMENT', 'ICT Equipment'),
        ('MACHINERY', 'Machinery'),
        ('MOTOR_VEHICLE', 'Motor Vehicle'),
        ('OFFICE EQUIPMENT', 'Office Equipment'),
        ('TECH_SCIENTIFIC', 'Technical and Scientific Equipment'),
    ]
    
    # 3. ASSET TYPE CHOICES (Detailed from CSV)
    NATURE_CHOICES = [
        ('AUDIO', 'Audio'),
        ('AV_BROADCAST', 'Audio/Video & Broadcast'),
        ('CAMERAS', 'Cameras'),
        ('CARS', 'Cars'),
        ('COMM_AUDIO', 'Communication and Audio Devices'),
        ('COMP_PERI_SERV', 'Computer Peripherals and Servers'),
        ('COPIER_PRINT', 'Copier and Printing Devices'),
        ('DESK_WORKSTATION', 'Desks & Workstations'),
        ('DESKTOP_AIO', 'Desktops and All-in-one PCs'),
        ('DRONES_NAV', 'Drones & Navigation'),
        ('FITNESS', 'Fitness Equipment'),
        ('FOOD_EQUIP', 'Food Equipment'),
        ('HVAC', 'HVAC Systems'),
        ('IMAGING_PHOTO', 'Imaging & Photography'),
        ('LAPTOPS', 'Laptops'),
        ('MEASURE_TEST', 'Measurement & Testing'),
        ('MEDICAL', 'Medical Equipment'),
        ('MOBILE', 'Mobile Phones'),
        ('MONITOR_DISPLAY', 'Monitor and Display Devices'),
        ('NETWORK_SEC', 'Network and Security Devices'),
        ('OTHER_FURNITURE', 'Other Furnitures and Fixtures'),
        ('POWER_ELEC', 'Power & Electrical'),
        ('SCIENTIFIC_LAB', 'Scientific & Laboratory Instruments'),
        ('SEATING', 'Seating Units'),
        ('SEWING_IND', 'Sewing/Industrial Machines'),
        ('SPECIAL_FIX', 'Specialized Fixtures'),
        ('SPORTS_DISPLAY', 'Sports & Display Systems'),
        ('SPORTS_EQUIP', 'Sports Equipment'),
        ('STORAGE_PRES', 'Storage & Preservation'),
        ('TABLETS', 'Tablets'),
        ('TRICYCLE', 'Tricycle'),
        ('WATER_SYSTEMS', 'Water Systems'),
        ('OTHER', 'Other'),
    ]

    item_id = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name="Item ID")
    property_number = models.CharField(max_length=50, unique=True, verbose_name="Property Number")
    name = models.CharField(max_length=255, verbose_name="Description (Short)")
    description = models.TextField(blank=True, null=True, verbose_name="Description (Full)")
    date_acquired = models.DateField(verbose_name="Date Acquired")
    acquisition_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Acquisition Cost")
    
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Department")
    
    asset_class = models.CharField(max_length=50, choices=CLASS_CHOICES, default='OTHER', verbose_name="PPE Category")
    asset_nature = models.CharField(max_length=50, choices=NATURE_CHOICES, default='OTHER', verbose_name="Asset Type")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SERVICEABLE', verbose_name="Status")
    
    accountable_surname = models.CharField(max_length=50, blank=True, null=True)
    accountable_firstname = models.CharField(max_length=50, blank=True, null=True)
    accountable_middle_initial = models.CharField(max_length=50, blank=True, null=True)
    cu = models.CharField(max_length=50, blank=True, null=True)
    image_serial = models.ImageField(upload_to='assets/serials/', blank=True, null=True)
    image_condition = models.ImageField(upload_to='assets/condition/', blank=True, null=True)
    attachment = models.FileField(upload_to='assets/docs/', blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # ==============================================
    # FINANCE & VALUATION FIELDS (Tab 2)
    # ==============================================
    DEPRECIATION_METHOD_CHOICES = [
        ('STRAIGHT_LINE', 'Straight-Line'),
        ('DECLINING_BALANCE', 'Declining Balance'),
        ('SUM_OF_YEARS', 'Sum-of-Years Digits'),
    ]
    fair_market_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Fair Market Value")
    salvage_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Salvage/Residual Value")
    useful_life_years = models.PositiveIntegerField(blank=True, null=True, verbose_name="Useful Life (Years)")
    depreciation_method = models.CharField(max_length=30, choices=DEPRECIATION_METHOD_CHOICES, default='STRAIGHT_LINE', verbose_name="Depreciation Method")
    accumulated_depreciation = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Accumulated Depreciation")
    depreciation_start_date = models.DateField(blank=True, null=True, verbose_name="Depreciation Start Date")

    # ==============================================
    # LIFECYCLE FIELDS (Tab 3)
    # ==============================================
    warranty_expiry = models.DateField(blank=True, null=True, verbose_name="Warranty Expiry Date")
    insurance_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Insurance Value")
    disposal_date = models.DateField(blank=True, null=True, verbose_name="Disposal Date")
    DISPOSAL_METHOD_CHOICES = [
        ('AUCTION', 'Public Auction'), ('CONDEMNATION', 'Condemnation'),
        ('DONATION', 'Donation'), ('BARTER', 'Barter'),
        ('TRANSFER', 'Transfer to Other Agency'),
    ]
    disposal_method = models.CharField(max_length=30, choices=DISPOSAL_METHOD_CHOICES, blank=True, null=True, verbose_name="Disposal Method")
    disposal_proceeds = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Disposal Proceeds")

    # ==============================================
    # GOVERNMENT / COA FIELDS (Tab 4)
    # ==============================================
    PROPERTY_CLASSIFICATION_CHOICES = [
        ('PPE', 'Property, Plant & Equipment'),
        ('SEMI_EXPENDABLE', 'Semi-Expendable'),
        ('EXPENDABLE', 'Expendable'),
    ]
    FUND_SOURCE_CHOICES = [
        ('GAA', 'General Appropriations Act'),
        ('INCOME', 'Income'),
        ('TRUST', 'Trust Fund'),
        ('EXTERNAL', 'Externally Funded'),
    ]
    uacs_object_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="UACS Object Code")
    fund_source = models.CharField(max_length=20, choices=FUND_SOURCE_CHOICES, blank=True, null=True, verbose_name="Fund Source")
    property_classification = models.CharField(max_length=20, choices=PROPERTY_CLASSIFICATION_CHOICES, blank=True, null=True, verbose_name="Property Classification")
    appraisal_date = models.DateField(blank=True, null=True, verbose_name="Last Appraisal Date")
    appraised_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Appraised Value")

    # ==============================================
    # COMPUTED PROPERTIES
    # ==============================================
    @property
    def book_value(self):
        """Acquisition Cost - Accumulated Depreciation"""
        if self.acquisition_cost and self.accumulated_depreciation:
            return self.acquisition_cost - self.accumulated_depreciation
        return self.acquisition_cost

    @property
    def annual_depreciation(self):
        """(Acquisition Cost - Salvage Value) / Useful Life"""
        if self.acquisition_cost and self.salvage_value and self.useful_life_years:
            return (self.acquisition_cost - self.salvage_value) / self.useful_life_years
        return None

    @property
    def is_fully_depreciated(self):
        if self.acquisition_cost and self.accumulated_depreciation and self.salvage_value:
            return self.accumulated_depreciation >= (self.acquisition_cost - self.salvage_value)
        return False

    def save(self, *args, **kwargs):
        if not self.item_id:
            year = datetime.date.today().year
            rand = get_random_string(6).upper()
            self.item_id = f"AST-{year}-{rand}"
        super().save(*args, **kwargs)

    def __str__(self): return f"{self.property_number} - {self.name}"

# 3. INSPECTION REQUEST MODEL
class InspectionRequest(models.Model):
    STATUS_CHOICES = [('Pending Inspection', 'Pending'), ('Approved', 'Approved'), ('Returned', 'Returned'), ('Rejected', 'Rejected')]
    transaction_id = models.CharField(max_length=20, unique=True, editable=False)
    requestor = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    notes = models.TextField()
    status = models.CharField(max_length=50, default='Pending Inspection', choices=STATUS_CHOICES)
    document_1 = models.FileField(upload_to='inspection_docs/', blank=True, null=True)
    document_2 = models.FileField(upload_to='inspection_docs/', blank=True, null=True)
    admin_remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            today = datetime.date.today().strftime('%Y')
            rand = get_random_string(4).upper()
            self.transaction_id = f"REQ-{today}-{rand}"
        super().save(*args, **kwargs)

    def __str__(self): return f"{self.transaction_id} - {self.asset.name}"

# 4. BATCH ASSET UPLOAD
class AssetBatch(models.Model):
    # Old Status Choices (kept for migration safety if needed, but overwritten below)
    # STATUS_CHOICES = [('PENDING', 'Pending Approval'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('RETURNED', 'Returned')]
    
    # NEW STRICT WORKFLOW STATES
    WORKFLOW_STATUS = [
        ('ANTICIPATORY', 'Anticipatory Procurement'),
        ('AWAITING_DELIVERY', 'Awaiting Delivery'),
        ('DELIVERY_VALIDATION', 'Delivery Validation'),
        ('FOR_INSPECTION', 'For Inspection'),
        ('FOR_SUPERVISOR_APPROVAL', 'For Supervisor Approval'),
        ('FOR_CHIEF_PRE_APPROVAL', 'For Chief Pre-Approval'),
        ('FOR_AO_SIGNATURE', 'For AO Signature'),
        ('FOR_CHIEF_FINAL_SIGNATURE', 'For Chief Final Signature'),
        ('PAR_RELEASED', 'PAR Released (Final)'),
        ('REJECTED', 'Rejected'),
    ]

    transaction_id = models.CharField(max_length=20, unique=True, editable=False)
    requestor = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=WORKFLOW_STATUS, default='ANTICIPATORY')
    
    # --- HEADER DETAILS ---
    requesting_unit = models.CharField(max_length=150, blank=True, null=True, verbose_name="Requesting Unit")
    supplier_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Supplier Name")
    po_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Purchase Order No.")
    sales_invoice_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Sales Invoice No.")
    acceptance_report_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Acceptance Report No.")
    
    # --- NEW FIELDS FOR PAR ONLY ---
    fund_cluster = models.CharField(max_length=100, blank=True, null=True, verbose_name="Fund Cluster")
    ups_dv_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="UPS DV Number")
    
    remarks = models.TextField(blank=True, null=True)
    admin_remarks = models.TextField(blank=True, null=True)
    
    # --- IMMUTABLE PAR STORAGE ---
    par_file = models.FileField(upload_to='pars/final/', blank=True, null=True, verbose_name="Finalized PAR PDF")
    par_hash = models.CharField(max_length=64, blank=True, null=True, verbose_name="SHA256 Hash")
    
    # --- 5 DOCUMENT SLOTS ---
    doc_1_name = models.CharField(max_length=100, blank=True, null=True)
    doc_1_file = models.FileField(upload_to='batch_docs/', blank=True, null=True)
    doc_2_name = models.CharField(max_length=100, blank=True, null=True)
    doc_2_file = models.FileField(upload_to='batch_docs/', blank=True, null=True)
    doc_3_name = models.CharField(max_length=100, blank=True, null=True)
    doc_3_file = models.FileField(upload_to='batch_docs/', blank=True, null=True)
    doc_4_name = models.CharField(max_length=100, blank=True, null=True)
    doc_4_file = models.FileField(upload_to='batch_docs/', blank=True, null=True)
    doc_5_name = models.CharField(max_length=100, blank=True, null=True)
    doc_5_file = models.FileField(upload_to='batch_docs/', blank=True, null=True)

    is_posted = models.BooleanField(default=False, editable=False)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            year = datetime.date.today().year
            rand = get_random_string(4).upper()
            self.transaction_id = f"BATCH-{year}-{rand}"
        super().save(*args, **kwargs)
    
    def __str__(self): return self.transaction_id

# 4.1 APPROVAL LOG (New for Audit Trail)
class ApprovalLog(models.Model):
    batch = models.ForeignKey(AssetBatch, related_name='approval_logs', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    role = models.CharField(max_length=50, verbose_name="Role at time of approval")
    action = models.CharField(max_length=100) # e.g. "Approved Inspection", "Signed PAR"
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Snapshot of signature used (path to a copy, not the user's live profile to prevent mutation)
    signature_snapshot = models.ImageField(upload_to='signatures/snapshots/', null=True, blank=True)

    def __str__(self): return f"{self.batch.transaction_id} - {self.action} by {self.user}"

# 5. BATCH ITEM DETAILS
class BatchItem(models.Model):
    batch = models.ForeignKey(AssetBatch, related_name='items', on_delete=models.CASCADE)
    unit = models.CharField(max_length=50, blank=True, null=True, verbose_name="Unit")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Qty")
    description = models.CharField(max_length=255, verbose_name="Description/Particulars")
    
    image = models.ImageField(upload_to='batch_items/', blank=True, null=True, verbose_name="Asset Image")

    nature_of_expense = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nature of Expense")
    reference_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Reference No.")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Amount")

    def __str__(self):
        return f"{self.description} ({self.quantity})"

    @property
    def total_price(self):
        return self.amount * self.quantity

# 6. ASSET TRANSFER REQUEST
class AssetTransferRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved & Transferred'),
        ('REJECTED', 'Rejected'),
        ('RETURNED', 'Returned'),
    ]

    transaction_id = models.CharField(max_length=20, unique=True, editable=False)
    requestor = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # The Asset being transferred
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name="Target Asset")
    
    # Snapshot of Current Officer (Auto-filled)
    current_officer = models.CharField(max_length=150, verbose_name="Current Accountable Officer")
    
    # New Officer Details
    new_officer_firstname = models.CharField(max_length=100, verbose_name="New Officer First Name")
    new_officer_surname = models.CharField(max_length=100, verbose_name="New Officer Surname")
    
    remarks = models.TextField(verbose_name="Reason for Transfer")
    admin_remarks = models.TextField(blank=True, null=True)

    # 2 Required Documents
    document_1 = models.FileField(upload_to='transfer_docs/', verbose_name="Transfer Form (ITR)")
    document_2 = models.FileField(upload_to='transfer_docs/', verbose_name="ID / Authorization")

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            year = datetime.date.today().strftime('%Y')
            rand = get_random_string(4).upper()
            self.transaction_id = f"TRF-{year}-{rand}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_id} - {self.asset.property_number}"

# ==========================================
# 7. SERVICE & MAINTENANCE LOG (NEW)
# ==========================================
class ServiceLog(models.Model):
    SERVICE_TYPES = [
        ('REPAIR', 'Repair'),
        ('MAINTENANCE', 'Preventive Maintenance'),
        ('UPGRADE', 'Upgrade'),
        ('INSPECTION', 'Inspection'),
        ('OTHER', 'Other'),
    ]

    asset = models.ForeignKey(Asset, related_name='service_logs', on_delete=models.CASCADE)
    service_date = models.DateField(default=datetime.date.today, verbose_name="Date of Service")
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES, default='MAINTENANCE')
    
    description = models.TextField(verbose_name="Work Done / Details")
    service_provider = models.CharField(max_length=150, verbose_name="Service Provider / Technician")
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Cost of Service")
    
    next_service_date = models.DateField(blank=True, null=True, verbose_name="Next Scheduled Date")
    service_document = models.FileField(upload_to='service_docs/', blank=True, null=True, verbose_name="Service Report/Receipt")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service_type} - {self.asset.property_number} ({self.service_date})"

# ==========================================
# 8. ASSET CHANGE LOG (Audit Trail)
# ==========================================
class AssetChangeLog(models.Model):
    TAB_CHOICES = [
        ('PROPERTY', 'Property Details'),
        ('FINANCE', 'Finance & Valuation'),
        ('LIFECYCLE', 'Lifecycle'),
        ('GOVERNMENT', 'Government / COA'),
    ]
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='change_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tab = models.CharField(max_length=30, choices=TAB_CHOICES)
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} changed {self.field_name} on {self.asset.property_number}"

# ==========================================
# 9. ASSET NOTIFICATION
# ==========================================
class AssetNotification(models.Model):
    RECIPIENT_ROLE_CHOICES = [
        ('SPMO_ADMIN', 'SPMO Officers'),
        ('ACCT_ADMIN', 'Accounting Officers'),
    ]
    recipient_role = models.CharField(max_length=30, choices=RECIPIENT_ROLE_CHOICES)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=500)
    triggered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.recipient_role}] {self.message}"