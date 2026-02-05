from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.mail import EmailMessage
from django.conf import settings
from .models import BookingRequest, AirlineCredit
from .forms import BookingRequestForm, BookingUploadForm, AdminBookingForm
import json


# 1. Landing Page
@login_required
def index(request):
    return render(request, "travel/index.html")


# 2. Book Flight
@login_required
def book_flight(request):
    if request.method == "POST":
        form = BookingRequestForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.status = "DRAFT"
            booking.created_by = request.user
            booking.save()
            return redirect("print_requisition", pk=booking.pk)
    else:
        initial_data = {"email": request.user.email}
        form = BookingRequestForm(initial=initial_data)

    return render(request, "travel/form.html", {"form": form})


# 3. Print Slip
@login_required
def print_requisition(request, pk):
    booking = get_object_or_404(BookingRequest, pk=pk)
    return render(request, "travel/requisition_slip.html", {"booking": booking})


# 4. Upload Docs
@login_required
def upload_documents(request, pk):
    booking = get_object_or_404(BookingRequest, pk=pk)
    if request.method == "POST":
        form = BookingUploadForm(request.POST, request.FILES, instance=booking)
        if form.is_valid():
            final_booking = form.save(commit=False)
            final_booking.status = "PENDING"
            final_booking.save()
            messages.success(request, "Success! Booking submitted for review.")
            return redirect("gfa_dashboard")
    else:
        form = BookingUploadForm(instance=booking)
    return render(request, "travel/upload.html", {"form": form, "booking": booking})


# 5. DASHBOARD CONTROLLER (With Filtering)
# 5. DASHBOARD CONTROLLER (With Formatting & Colors)
@login_required
def admin_dashboard(request):
    user = request.user

    # 1. Routing
    if user.is_superuser:
        transactions = BookingRequest.objects.all().order_by("-created_at")
        dashboard_title = "Executive Dashboard (System Wide)"
        template_name = "travel/dashboard.html"
    elif hasattr(user, "userprofile") and user.userprofile.office and user.is_staff:
        user_office = user.userprofile.office
        transactions = BookingRequest.objects.filter(unit_office=user_office).order_by(
            "-created_at"
        )
        dashboard_title = f"{user.userprofile.get_office_display()} Dashboard"
        template_name = "travel/dashboard.html"
    else:
        transactions = BookingRequest.objects.filter(created_by=user).order_by(
            "-created_at"
        )
        dashboard_title = "My Travel Profile"
        template_name = "travel/user_transactions.html"

    # 2. Search & Filter
    search_query = request.GET.get("q")
    if search_query:
        transactions = transactions.filter(
            Q(full_name__icontains=search_query)
            | Q(destination_details__icontains=search_query)
            | Q(id__icontains=search_query)
            | Q(booking_reference_no__icontains=search_query)
        )

    status_filter = request.GET.get("status")
    if status_filter:
        transactions = transactions.filter(status=status_filter)
    date_filter = request.GET.get("date")
    if date_filter:
        transactions = transactions.filter(departure_date=date_filter)

    # 3. Statistics
    total_reqs = transactions.count()
    pending_reqs = transactions.filter(status="PENDING").count()
    booked_txns = transactions.filter(status="BOOKED")
    total_booked_count = booked_txns.count()
    total_spent = booked_txns.aggregate(Sum("total_amount"))["total_amount__sum"] or 0

    # 4. Airline Balances & Formatting
    pal_display = {"val": "0", "color": "text-slate-400"}
    ceb_display = {"val": "0", "color": "text-slate-400"}

    dest_labels, dest_counts, office_labels, office_counts = [], [], [], []

    if template_name == "travel/dashboard.html":

        # HELPER FUNCTION
        def format_credit(amount):
            # Color Logic
            if amount <= 300000:
                color = "text-red-600"  # Critical
            elif amount <= 500000:
                color = "text-orange-500"  # Warning
            else:
                color = "text-emerald-700"  # Healthy

            # Text Formatting
            if amount >= 1_000_000:
                val = f"{amount/1_000_000:.1f}M"
            elif amount >= 1_000:
                val = f"{amount/1_000:.0f}K"
            else:
                val = f"{amount:.0f}"

            return {"val": val, "color": color}

        try:
            pal_credit = AirlineCredit.objects.get(airline="PAL")
            pal_display = format_credit(pal_credit.current_balance)
        except AirlineCredit.DoesNotExist:
            pass

        try:
            ceb_credit = AirlineCredit.objects.get(airline="CEB")
            ceb_display = format_credit(ceb_credit.current_balance)
        except AirlineCredit.DoesNotExist:
            pass

        # Charts
        dest_data = transactions.values("destination_details").annotate(
            count=Count("id")
        )
        dest_labels = json.dumps([d["destination_details"] for d in dest_data])
        dest_counts = json.dumps([d["count"] for d in dest_data])

        office_data = transactions.values("unit_office").annotate(count=Count("id"))
        office_labels = json.dumps([d["unit_office"] for d in office_data])
        office_counts = json.dumps([d["count"] for d in office_data])

    context = {
        "transactions": transactions,
        "total_reqs": total_reqs,
        "pending_reqs": pending_reqs,
        "total_booked_count": total_booked_count,
        "total_spent": total_spent,
        "pal_display": pal_display,
        "ceb_display": ceb_display,
        "dest_labels": dest_labels,
        "dest_counts": dest_counts,
        "office_labels": office_labels,
        "office_counts": office_counts,
        "dashboard_title": dashboard_title,
        "search_query": search_query,
        "current_status": status_filter,
        "current_date": date_filter,
    }
    return render(request, template_name, context)


# 6. Update Status
@login_required
def update_status(request, pk):
    if not request.user.is_staff:
        return redirect("index")

    if request.method == "POST":
        booking = get_object_or_404(BookingRequest, pk=pk)
        action = request.POST.get("action")
        if action == "approve":
            booking.status = "APPROVED"
        elif action == "return":
            booking.status = "RETURNED"
            booking.remarks = request.POST.get("remarks")
        booking.save()
    return redirect("gfa_dashboard")


# 7. Admin Attach Ticket
# Add these imports at top if missing
from django.db import transaction
from django.core.mail import EmailMessage
from django.conf import settings
from .models import AirlineCredit

# ... (keep other views)


@login_required
@transaction.atomic  # Locks DB to prevent partial saves
def admin_attach_ticket(request, pk):
    if not request.user.is_staff:
        return redirect("index")

    booking = get_object_or_404(BookingRequest, pk=pk)

    if request.method == "POST":
        form = AdminBookingForm(request.POST, request.FILES, instance=booking)
        if form.is_valid():
            final = form.save(commit=False)

            # --- SAFETY CHECK: PREVENT DOUBLE DEDUCTION ---
            # If ticket is ALREADY booked, just update details (edit mode)
            if booking.status == "BOOKED":
                final.save()
                messages.info(
                    request,
                    "Ticket updated successfully. No balance deducted (previously booked).",
                )
                return redirect("booking_summary", pk=booking.pk)

            # --- DEDUCTION LOGIC (New Booking Only) ---
            cost = final.total_amount
            airline_code = final.airline

            if cost and cost > 0 and airline_code:
                try:
                    # 1. Lock the wallet row (Prevent race conditions)
                    credit = AirlineCredit.objects.select_for_update().get(
                        airline=airline_code
                    )

                    # 2. Check Balance
                    if credit.current_balance >= cost:

                        # 3. Deduct
                        credit.current_balance -= cost
                        credit.save()

                        # 4. Save Status
                        final.status = "BOOKED"
                        final.ticket_issued_at = timezone.now()
                        final.save()

                        # 5. Send Email
                        subject = f"Flight Confirmed: {final.origin} - {final.destination_details}"
                        recipient_list = [final.email]
                        sender_email = getattr(
                            settings, "DEFAULT_FROM_EMAIL", "admin@example.com"
                        )
                        email = EmailMessage(
                            subject,
                            final.admin_instructions,
                            sender_email,
                            recipient_list,
                        )

                        if "doc_flight_ticket" in request.FILES:
                            f = request.FILES["doc_flight_ticket"]
                            email.attach(f.name, f.read(), f.content_type)

                        try:
                            email.send(fail_silently=False)
                            messages.success(
                                request,
                                f"Success! ₱{cost:,.2f} deducted from {credit.get_airline_display()}. Remaining: ₱{credit.current_balance:,.2f}",
                            )
                        except:
                            messages.warning(
                                request, "Ticket booked and deducted, but email failed."
                            )

                        return redirect("booking_summary", pk=booking.pk)

                    else:
                        messages.error(
                            request,
                            f"TRANSACTION FAILED: Insufficient funds in {credit.get_airline_display()}. Available: ₱{credit.current_balance:,.2f}",
                        )
                        return render(
                            request,
                            "travel/admin_attach.html",
                            {"form": form, "booking": booking},
                        )

                except AirlineCredit.DoesNotExist:
                    messages.error(
                        request,
                        f"System Error: No Credit Wallet found for {airline_code}.",
                    )
                    return render(
                        request,
                        "travel/admin_attach.html",
                        {"form": form, "booking": booking},
                    )

            # Fallback (If cost is 0, just save)
            final.status = "BOOKED"
            final.save()
            messages.warning(request, "Ticket issued with ZERO cost.")
            return redirect("booking_summary", pk=booking.pk)

    else:
        # Pre-fill standard message
        dep_time = booking.departure_time.strftime("%I:%M %p")
        standard_msg = (
            f"Dear {booking.full_name},\n\n"
            f"Good day! Your flight to {booking.destination_details} has been successfully booked.\n\n"
            f"FLIGHT DETAILS:\nRoute: {booking.origin} -> {booking.destination_details}\nDate: {booking.departure_date} | Time: {dep_time}\nAirline: {booking.get_airline_display()}\n\n"
            f"IMPORTANT REMINDERS:\n1. ARRIVAL: Please be at the airport 2 hours before flight.\n"
            f"2. BAGGAGE: {booking.get_baggage_type_display()}.\n3. CHECK-IN: Present the attached Electronic Ticket and your valid ID.\n\n"
            f"Safe travels,\nUP System Supply & Property Management Office"
        )
        form = AdminBookingForm(
            instance=booking, initial={"admin_instructions": standard_msg}
        )

    return render(
        request, "travel/admin_attach.html", {"form": form, "booking": booking}
    )


# 8. Summary
@login_required
def booking_summary(request, pk):
    booking = get_object_or_404(BookingRequest, pk=pk)
    return render(request, "travel/booking_summary.html", {"booking": booking})
