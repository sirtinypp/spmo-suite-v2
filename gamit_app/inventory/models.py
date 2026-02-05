from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
import datetime

# 1. USER PROFILE
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    office = models.CharField(max_length=100, verbose_name="Assigned Office Access")
    def __str__(self): return f"{self.user.username} - {self.office}"

# 2. MAIN ASSET MODEL
class Asset(models.Model):
    STATUS_CHOICES = [
        ('SERVICEABLE', 'Serviceable'), ('UNSERVICEABLE', 'Unserviceable'),
        ('DISPOSED', 'Disposed'), ('UNDER_REPAIR', 'Under Repair'),
        ('PENDING', 'Pending Approval'),
    ]
    CLASS_CHOICES = [
        ('ICT EQUIPMENT', 'ICT Equipment'), ('VEHICLE', 'Vehicle'),
        ('AIRCONDITIONING', 'Airconditioning'), ('OFFICE EQUIPMENT', 'Office Equipment'),
        ('TECH_SCIENTIFIC', 'Technical and Scientific Equipment'),
        ('FURNITURE', 'Furniture and Fixtures'), ('OTHER', 'Other'),
    ]
    NATURE_CHOICES = [
        ('OFFICE', 'Office'), ('LABORATORY', 'Laboratory'), ('SCHOOL', 'School'),
        ('ACCOMODATION', 'Accomodation'), ('OTHER', 'Other'),
    ]

    item_id = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name="Item ID")
    property_number = models.CharField(max_length=50, unique=True, verbose_name="Property Number")
    name = models.CharField(max_length=255, verbose_name="Description (Short)")
    description = models.TextField(blank=True, null=True, verbose_name="Description (Full)")
    date_acquired = models.DateField(verbose_name="Date Acquired")
    acquisition_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Acquisition Cost")
    assigned_office = models.CharField(max_length=255, verbose_name="Office/Unit")
    asset_class = models.CharField(max_length=50, choices=CLASS_CHOICES, default='OTHER', verbose_name="Class/Type")
    asset_nature = models.CharField(max_length=50, choices=NATURE_CHOICES, default='OFFICE', verbose_name="Nature")
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
    STATUS_CHOICES = [('PENDING', 'Pending Approval'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('RETURNED', 'Returned')]
    transaction_id = models.CharField(max_length=20, unique=True, editable=False)
    requestor = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
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