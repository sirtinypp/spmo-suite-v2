from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

# --- CONSTANTS ---
TRIP_TYPE_CHOICES = [
    ('ONE_WAY', 'One-Way'),
    ('ROUND_TRIP', 'Round-Trip'),
    ('MULTI_CITY', 'Multi-City'),
]

AIRLINE_CHOICES = [
    ('PAL', 'Philippine Airlines'),
    ('CEB', 'Cebu Pacific'),
]

CLASS_CHOICES = [
    ('ECONOMY', 'Economy'),
    ('BUSINESS', 'Business Class'),
    ('PREMIUM', 'Premium / First Class'),
]

BAGGAGE_CHOICES = [
    ('HAND_CARRY', 'Hand-carry only'),
    ('CHECK_IN', 'Additional check-in baggage'),
]

STATUS_CHOICES = [
    ('DRAFT', 'Draft / Printing'),
    ('PENDING', 'Pending Unit AO'),
    ('FOR_ADMIN', 'For SPMO Admin Review (Ruby)'),
    ('FOR_SUPERVISOR', 'For Supervisor Verification (Aaron)'),
    ('FOR_CHIEF', 'For Chief Approval (Isagani)'),
    ('APPROVED', 'Approved (Processing)'),
    ('BOOKED', 'Ticket Issued & Confirmed'),
    ('SETTLED', 'Transaction Settled'),
    ('RETURNED', 'Returned'),
    ('CANCELLED', 'Cancelled'),
]

# --- 1. PROVINCE & CITY MODELS ---
class Province(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class City(models.Model):
    name = models.CharField(max_length=255)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='cities')
    zipcode = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.name}, {self.province.name}"

    class Meta:
        verbose_name_plural = "Cities"
        ordering = ['name']
        unique_together = ('name', 'province')

class Airport(models.Model):
    iata_code = models.CharField(max_length=3, unique=True, verbose_name="IATA Code")
    name = models.CharField(max_length=255, verbose_name="Airport Name")
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='airports')
    city_name = models.CharField(max_length=255, verbose_name="City/Area Name")
    is_international = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.city_name} ({self.iata_code})"

    class Meta:
        ordering = ['city_name']

# --- 2. DEPARTMENT DATABASE MODEL ---
class Department(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Department Name")
    code = models.CharField(max_length=50, unique=True, verbose_name="Office Code")
    is_mother_unit = models.BooleanField(default=False, help_text="Checked if this is a primary Mother Unit")

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        ordering = ['name']

# --- 2. AIRLINE CREDIT MODEL ---
class AirlineCredit(models.Model):
    airline = models.CharField(max_length=3, choices=AIRLINE_CHOICES, unique=True)
    total_credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Total Allocation")
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Remaining Balance")
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_airline_display()} - ₱{self.current_balance}"

    class Meta:
        verbose_name = "Airline Credit Balance"
        verbose_name_plural = "Airline Credit Balances"

# --- 3. USER PROFILE ---
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    office = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Assigned Office")

    def __str__(self):
        return f"{self.user.username} - {self.office.name if self.office else 'No Office'}"

# --- 4. BOOKING REQUEST MODEL ---
class BookingRequest(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='bookings')
    
    # Traveler Info
    email = models.EmailField(verbose_name="Email Address")
    full_name = models.CharField(max_length=200, verbose_name="Official Name of Traveler")
    employee_id = models.CharField(max_length=50, verbose_name="Employee ID")
    
    # Relational Fields
    unit_office = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='office_bookings', verbose_name="Unit Office")
    mother_unit = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='mother_unit_bookings', verbose_name="Mother Unit")

    birthday = models.DateField(verbose_name="Birthday")
    designation = models.CharField(max_length=100, verbose_name="Designation")
    up_mail = models.EmailField(verbose_name="UP Mail")
    contact_number = models.CharField(max_length=50, verbose_name="Contact Phone Number")
    admin_officer = models.CharField(max_length=200, verbose_name="Admin Officer (Requesting Staff)")

    # Travel Details
    purpose = models.TextField(verbose_name="Purpose of Travel")
    trip_type = models.CharField(max_length=20, choices=TRIP_TYPE_CHOICES, default='ROUND_TRIP')
    origin = models.CharField(max_length=255, verbose_name="Origin (Departure From)", default="Manila")
    destination_details = models.CharField(max_length=255, verbose_name="Destination (Arrival At)")
    departure_date = models.DateField()
    departure_time = models.TimeField(verbose_name="Specific Time (Departure)")
    return_date = models.DateField(blank=True, null=True)
    return_time = models.TimeField(blank=True, null=True, verbose_name="Specific Time (Return)")
    is_official = models.BooleanField(default=False, verbose_name="Is this Travel Official and Approved?")

    # Preferences
    airline = models.CharField(max_length=20, choices=AIRLINE_CHOICES)
    seat_class = models.CharField(max_length=20, choices=CLASS_CHOICES, default='ECONOMY')
    avail_insurance = models.BooleanField(default=False, verbose_name="Avail Travel Insurance?")
    baggage_type = models.CharField(max_length=20, choices=BAGGAGE_CHOICES, default='HAND_CARRY')
    special_requests = models.TextField(blank=True, null=True)

    # Approvals & Declarations
    supervisor_name = models.CharField(max_length=200, verbose_name="Immediate Supervisor's Name")
    supervisor_email = models.EmailField(verbose_name="Supervisor's Email")
    approval_date = models.DateField(verbose_name="Date of Approval")
    remarks = models.TextField(blank=True, null=True)
    agreed_to_policy = models.BooleanField(default=False, verbose_name="I hereby certify that information is true")

    # Documents
    doc_signed_slip = models.FileField(upload_to='docs/ris/', blank=True, null=True, verbose_name="Signed Requisition Slip (RIS)")
    doc_travel_order = models.FileField(upload_to='docs/to/', blank=True, null=True, verbose_name="Approved Travel Order")
    doc_gov_id = models.FileField(upload_to='docs/ids/', blank=True, null=True, verbose_name="Government Issued ID")
    doc_itinerary = models.FileField(upload_to='docs/itin/', blank=True, null=True, verbose_name="Itinerary / Invitation Letter")
    doc_previous_gfa = models.FileField(upload_to='docs/prev/', blank=True, null=True, verbose_name="Previous GFA (If Rebooking)")

    # ADMIN BOOKING DETAILS
    booking_reference_no = models.CharField(max_length=50, blank=True, null=True, verbose_name="Airline Booking Ref / PNR")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Total Ticket Cost (PHP)")
    doc_flight_ticket = models.FileField(upload_to='docs/tickets/', blank=True, null=True, verbose_name="Official Airline Ticket")
    doc_voucher = models.FileField(upload_to='docs/vouchers/', blank=True, null=True, verbose_name="Hotel/Other Voucher")
    admin_instructions = models.TextField(blank=True, null=True, help_text="Instructions for the traveler")
    ticket_issued_at = models.DateTimeField(null=True, blank=True)

    # System Fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.destination_details}"

# --- 4B. TRAVEL TRIP MODEL (Parent) ---
class TravelTrip(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='trips')

    # Office / Requester
    unit_office = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='office_trips', verbose_name="Unit Office")
    mother_unit = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='mother_unit_trips', verbose_name="Mother Unit")
    admin_officer = models.CharField(max_length=200, verbose_name="Admin Officer (Requesting Staff)")

    # Trip Details
    purpose = models.TextField(verbose_name="Purpose of Travel")
    trip_type = models.CharField(max_length=20, choices=TRIP_TYPE_CHOICES, default='ROUND_TRIP')
    origin = models.ForeignKey('Airport', on_delete=models.SET_NULL, null=True, related_name='departures', verbose_name="Origin Airport")
    destination = models.ForeignKey('Airport', on_delete=models.SET_NULL, null=True, related_name='arrivals', verbose_name="Destination Airport")
    departure_date = models.DateField()
    departure_time = models.TimeField(verbose_name="Preferred Departure Time")
    return_date = models.DateField(blank=True, null=True)
    return_time = models.TimeField(blank=True, null=True, verbose_name="Preferred Return Time")
    is_official = models.BooleanField(default=False, verbose_name="Official & Approved Travel?")

    # Preferences
    airline = models.CharField(max_length=20, choices=AIRLINE_CHOICES)
    seat_class = models.CharField(max_length=20, choices=CLASS_CHOICES, default='ECONOMY')
    baggage_type = models.CharField(max_length=20, choices=BAGGAGE_CHOICES, default='HAND_CARRY')
    special_requests = models.TextField(blank=True, null=True)

    # Approvals
    supervisor_name = models.CharField(max_length=200, verbose_name="Immediate Supervisor")
    supervisor_email = models.EmailField(verbose_name="Supervisor Email")
    approval_date = models.DateField(verbose_name="Date of Approval")
    remarks = models.TextField(blank=True, null=True)

    # Documents (shared per trip)
    doc_signed_slip = models.FileField(upload_to='trips/ris/', blank=True, null=True, verbose_name="Signed RIS")
    doc_travel_order = models.FileField(upload_to='trips/to/', blank=True, null=True, verbose_name="Approved Travel Order")
    doc_itinerary = models.FileField(upload_to='trips/itin/', blank=True, null=True, verbose_name="Itinerary / Invitation")
    doc_previous_gfa = models.FileField(upload_to='trips/prev/', blank=True, null=True, verbose_name="Previous GFA (Rebooking)")

    # Admin / Ticketing
    booking_reference_no = models.CharField(max_length=50, blank=True, null=True, verbose_name="PNR / Booking Ref")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Total Cost (PHP)")
    admin_instructions = models.TextField(blank=True, null=True)
    ticket_issued_at = models.DateTimeField(null=True, blank=True)

    # Approval Workflow (Phase 11)
    admin_verified = models.BooleanField(default=False)
    admin_verified_at = models.DateTimeField(null=True, blank=True)
    admin_verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_approvals')

    supervisor_verified = models.BooleanField(default=False)
    supervisor_verified_at = models.DateTimeField(null=True, blank=True)
    supervisor_verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='supervisor_approvals')

    chief_approved = models.BooleanField(default=False)
    chief_approved_at = models.DateTimeField(null=True, blank=True)
    chief_approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='chief_approvals')

    # System
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    created_at = models.DateTimeField(auto_now_add=True)

    # Legacy link (nullable, used during migration)
    legacy_booking = models.OneToOneField(BookingRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='trip')

    def __str__(self):
        origin_code = self.origin.iata_code if self.origin else '???'
        dest_code = self.destination.iata_code if self.destination else '???'
        return f"TRIP-{self.id:06d} {origin_code}→{dest_code}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Travel Trip"

# --- 4C. PASSENGER RECORD MODEL (Child) ---
class PassengerRecord(models.Model):
    trip = models.ForeignKey(TravelTrip, on_delete=models.CASCADE, related_name='passengers')

    # Personal Info
    full_name = models.CharField(max_length=200, verbose_name="Full Name")
    email = models.EmailField(verbose_name="Email Address")
    employee_id = models.CharField(max_length=50, verbose_name="Employee ID")
    birthday = models.DateField(verbose_name="Birthday")
    designation = models.CharField(max_length=100, verbose_name="Designation")
    up_mail = models.EmailField(verbose_name="UP Mail")
    contact_number = models.CharField(max_length=50, verbose_name="Contact Number")

    # Documents (per passenger)
    doc_gov_id = models.FileField(upload_to='passengers/ids/', blank=True, null=True, verbose_name="Government ID")
    doc_flight_ticket = models.FileField(upload_to='passengers/tickets/', blank=True, null=True, verbose_name="E-Ticket")
    doc_voucher = models.FileField(upload_to='passengers/vouchers/', blank=True, null=True, verbose_name="Voucher")

    # Insurance
    avail_insurance = models.BooleanField(default=False, verbose_name="Travel Insurance?")

    def __str__(self):
        return f"{self.full_name} (Trip #{self.trip_id})"

    class Meta:
        ordering = ['full_name']
        verbose_name = "Passenger Record"

class NewsPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_at']
        verbose_name = "News Post"

class VisitorCount(models.Model):
    total_hits = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Total Hits: {self.total_hits}"

# =====================================================
# PHASE 10: Financial Audit & Settlement
# =====================================================

class CreditLog(models.Model):
    TRANSACTION_TYPES = [
        ('DEDUCTION', 'Deduction (Flight Booking)'),
        ('REFUND', 'Refund (Cancellation)'),
        ('TOP_UP', 'Top-up (Settlement)'),
        ('ADJUSTMENT', 'Manual Adjustment'),
    ]
    
    trip = models.ForeignKey(TravelTrip, on_delete=models.SET_NULL, null=True, blank=True, related_name='credit_logs')
    airline = models.CharField(max_length=10, choices=AIRLINE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2, help_text="Snapshot of the balance after this transaction")
    remarks = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Audit Trail Links
    trip = models.ForeignKey(TravelTrip, on_delete=models.SET_NULL, null=True, blank=True, related_name='credit_logs')
    settlement = models.ForeignKey('Settlement', on_delete=models.SET_NULL, null=True, blank=True, related_name='credit_logs')

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Credit Audit Log"

    def __str__(self):
        return f"{self.transaction_type} | {self.airline} | {self.amount}"


class Settlement(models.Model):
    airline = models.CharField(max_length=10, choices=AIRLINE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference_no = models.CharField(max_length=100, help_text="Check No, DV No, or OR No")
    settlement_date = models.DateField()
    attachment = models.FileField(upload_to='settlements/', blank=True, null=True, help_text="Proof of payment")
    remarks = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Linked Transaction (Search-based Settlement Refinement)
    trip = models.ForeignKey(TravelTrip, on_delete=models.SET_NULL, null=True, blank=True, related_name='settlement_record')
    legacy_booking = models.ForeignKey(BookingRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='settlement_record')

    class Meta:
        ordering = ['-settlement_date', '-created_at']

    def __str__(self):
        return f"Settlement: {self.airline} | {self.amount} | {self.reference_no}"

# --- SIGNALS ---

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()