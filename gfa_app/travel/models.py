from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- CONSTANTS ---
MOTHER_UNIT_CHOICES = [
    ("OP", "Office of the President (OP)"),
    ("OVPAA", "Office of the Vice President for Academic Affairs (OVPAA)"),
    ("OVPA", "Office of the Vice President for Administration (OVPA)"),
    ("OVPA_QMS", "Office of the Vice President for Administration (QMS)"),
    ("OVPD", "Office of the Vice President for Development (OVPD)"),
    ("OVPLA", "Office of the Vice President for Legal Affairs (OVPLA)"),
    ("OVPPF", "Office of the Vice President for Planning and Finance (OVPPF)"),
    ("OVPPA", "Office of the Vice President for Public Affairs (OVPPA)"),
    ("OVPRI", "Office of the Vice President for Research and Innovation (OVPRI)"),
    ("OTHER", "Other"),
]

OFFICE_CHOICES = [
    ("SAO", "System Accounting Office"),
    ("SBO", "System Budget Office"),
    ("SCO", "System Cash Office"),
    ("CIDS", "Center for Integrative Development Studies (CIDS)"),
    ("CWGS", "Center for Women and Gender Studies (CWGS)"),
    ("CIFAL", "CIFAL"),
    ("COA", "System COA"),
    ("EXEC_HOUSE", "Executive House"),
    ("SHRDO", "System Human Resource Development Office (SHRDO)"),
    ("ITDC", "Information Technology Development Center (ITDC)"),
    ("MPRO", "Media and Public Relation (MPRO)"),
    ("OAd", "Office of Admissions (OAd)"),
    ("OAR", "Office of Alumni Relation (OAR)"),
    ("ODPI", "Office of Design and Planning Initiatives (ODPI)"),
    ("OIL", "Office of International Linkages (OIL)"),
    ("OSR", "Office of Sectoral Regents (OSR)"),
    ("OSFA", "Office of Student Financial Assistance (OSFA)"),
    ("OSU", "Office of the Secretary of the University (OSU)"),
    ("PPSO", "Padayon Public Service Office"),
    ("PERPI", "Philippine Energy Research and Policy Institute (PERPI)"),
    ("PGC", "Philippine Genome Center (PGC)"),
    ("PMO", "Project Management Office (PMO)"),
    ("SPMO", "System Supply and Property Management Office (SPMO)"),
    ("TTBDO", "Technology Transfer and Business Development Office (TTBDO)"),
    ("TVUP", "TVUP"),
    ("UPS", "Ugnayan ng Pahinungod -System"),
    ("UPBGC", "UP Bonifacio Global City (UPBGC)"),
    ("UP_ISC", "UP Intelligent System Center (UP-ISC)"),
    ("UPKRC", "UP Korea Research Center (UPKRC)"),
    ("UP_PRESS", "UP Press"),
    ("UP_PROC", "UP Procurement Unit"),
    ("UPRI", "UP Resilience Institute (UPRI)"),
    ("UPRI_PROJ", "UP Resilience Institute Projects"),
    ("UP_SRP", "UP Strategic Relations Program"),
    ("DPO", "UP System Data Protection Office"),
    ("UPS_OSDS", "UPS OSDS"),
    ("FMO", "Facilities Management Office"),
    ("UP_DT", "UP Digital Transformation"),
    ("OTHER", "Other"),
]

TRIP_TYPE_CHOICES = [
    ("ONE_WAY", "One-Way"),
    ("ROUND_TRIP", "Round-Trip"),
    ("MULTI_CITY", "Multi-City"),
]

AIRLINE_CHOICES = [
    ("PAL", "Philippine Airlines"),
    ("CEB", "Cebu Pacific"),
]

CLASS_CHOICES = [
    ("ECONOMY", "Economy"),
    ("BUSINESS", "Business Class"),
    ("PREMIUM", "Premium / First Class"),
]

BAGGAGE_CHOICES = [
    ("HAND_CARRY", "Hand-carry only"),
    ("CHECK_IN", "Additional check-in baggage"),
]

STATUS_CHOICES = [
    ("DRAFT", "Draft / Printing"),
    ("PENDING", "Pending Review"),
    ("APPROVED", "Approved (Processing)"),
    ("BOOKED", "Ticket Issued & Confirmed"),
    ("SETTLED", "Transaction Settled"),  # Added for future button
    ("RETURNED", "Returned"),
    ("CANCELLED", "Cancelled"),  # Added for future button
]


# --- 1. AIRLINE CREDIT MODEL ---
class AirlineCredit(models.Model):
    airline = models.CharField(max_length=3, choices=AIRLINE_CHOICES, unique=True)
    total_credit_limit = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, verbose_name="Total Allocation"
    )
    current_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, verbose_name="Remaining Balance"
    )
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_airline_display()} - ₱{self.current_balance}"

    class Meta:
        verbose_name = "Airline Credit Balance"
        verbose_name_plural = "Airline Credit Balances"


# --- 2. USER PROFILE ---
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    office = models.CharField(
        max_length=100,
        choices=OFFICE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Assigned Office",
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_office_display() or 'No Office'}"


# --- 3. BOOKING REQUEST MODEL ---
class BookingRequest(models.Model):
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="bookings"
    )

    # Traveler Info
    email = models.EmailField(verbose_name="Email Address")
    full_name = models.CharField(
        max_length=200, verbose_name="Official Name of Traveler"
    )
    employee_id = models.CharField(max_length=50, verbose_name="Employee ID")
    unit_office = models.CharField(
        max_length=100, choices=OFFICE_CHOICES, verbose_name="Unit Office"
    )
    mother_unit = models.CharField(
        max_length=100, choices=MOTHER_UNIT_CHOICES, verbose_name="Mother Unit"
    )
    birthday = models.DateField(verbose_name="Birthday")
    designation = models.CharField(max_length=100, verbose_name="Designation")
    up_mail = models.EmailField(verbose_name="UP Mail")
    contact_number = models.CharField(
        max_length=50, verbose_name="Contact Phone Number"
    )
    admin_officer = models.CharField(
        max_length=200, verbose_name="Admin Officer (Requesting Staff)"
    )

    # Travel Details
    purpose = models.TextField(verbose_name="Purpose of Travel")
    trip_type = models.CharField(
        max_length=20, choices=TRIP_TYPE_CHOICES, default="ROUND_TRIP"
    )
    origin = models.CharField(
        max_length=255, verbose_name="Origin (Departure From)", default="Manila"
    )
    destination_details = models.CharField(
        max_length=255, verbose_name="Destination (Arrival At)"
    )
    departure_date = models.DateField()
    departure_time = models.TimeField(verbose_name="Specific Time (Departure)")
    return_date = models.DateField(blank=True, null=True)
    return_time = models.TimeField(
        blank=True, null=True, verbose_name="Specific Time (Return)"
    )
    is_official = models.BooleanField(
        default=False, verbose_name="Is this Travel Official and Approved?"
    )

    # Preferences
    airline = models.CharField(max_length=20, choices=AIRLINE_CHOICES)
    seat_class = models.CharField(
        max_length=20, choices=CLASS_CHOICES, default="ECONOMY"
    )
    avail_insurance = models.BooleanField(
        default=False, verbose_name="Avail Travel Insurance?"
    )
    baggage_type = models.CharField(
        max_length=20, choices=BAGGAGE_CHOICES, default="HAND_CARRY"
    )
    special_requests = models.TextField(blank=True, null=True)

    # Approvals & Declarations
    supervisor_name = models.CharField(
        max_length=200, verbose_name="Immediate Supervisor's Name"
    )
    supervisor_email = models.EmailField(verbose_name="Supervisor's Email")
    approval_date = models.DateField(verbose_name="Date of Approval")
    remarks = models.TextField(blank=True, null=True)
    agreed_to_policy = models.BooleanField(
        default=False, verbose_name="I hereby certify that information is true"
    )

    # Documents
    doc_signed_slip = models.FileField(
        upload_to="docs/ris/",
        blank=True,
        null=True,
        verbose_name="Signed Requisition Slip (RIS)",
    )
    doc_travel_order = models.FileField(
        upload_to="docs/to/",
        blank=True,
        null=True,
        verbose_name="Approved Travel Order",
    )
    doc_gov_id = models.FileField(
        upload_to="docs/ids/",
        blank=True,
        null=True,
        verbose_name="Government Issued ID",
    )
    doc_itinerary = models.FileField(
        upload_to="docs/itin/",
        blank=True,
        null=True,
        verbose_name="Itinerary / Invitation Letter",
    )
    doc_previous_gfa = models.FileField(
        upload_to="docs/prev/",
        blank=True,
        null=True,
        verbose_name="Previous GFA (If Rebooking)",
    )

    # ADMIN BOOKING DETAILS
    booking_reference_no = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Airline Booking Ref / PNR"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Total Ticket Cost (PHP)",
    )
    doc_flight_ticket = models.FileField(
        upload_to="docs/tickets/",
        blank=True,
        null=True,
        verbose_name="Official Airline Ticket",
    )
    doc_voucher = models.FileField(
        upload_to="docs/vouchers/",
        blank=True,
        null=True,
        verbose_name="Hotel/Other Voucher",
    )
    admin_instructions = models.TextField(
        blank=True, null=True, help_text="Instructions for the traveler"
    )
    ticket_issued_at = models.DateTimeField(null=True, blank=True)

    # System Fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.destination_details}"


# --- SIGNALS ---


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
    if hasattr(instance, "userprofile"):
        instance.userprofile.save()


# NOTE: The 'post_delete' signal for refunding balance has been REMOVED as requested.
# Refund logic will be handled manually via a future "Settled/Refund" button logic.
