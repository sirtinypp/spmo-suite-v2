from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.mail import EmailMessage
from django.conf import settings
from .models import (
    BookingRequest, UserProfile, AirlineCredit, Department, Province, City, 
    Airport, TravelTrip, PassengerRecord, NewsPost, VisitorCount, CreditLog, Settlement
)
from .forms import BookingRequestForm, BookingUploadForm, AdminBookingForm, TripForm, PassengerFormSet
import json

# 1. Landing Page
def index(request):
    if request.user.is_authenticated:
        return redirect('gfa_dashboard')
        
    from .models import NewsPost, VisitorCount, BookingRequest
    
    # KPIs for Landing Page
    total_bookings = BookingRequest.objects.count()
    tickets_issued = BookingRequest.objects.filter(status='BOOKED').count()
    
    # News Feed
    news_posts = NewsPost.objects.filter(is_published=True)[:5]
    
    # Visitor Counter (Simple Increment)
    visitor_stat, created = VisitorCount.objects.get_or_create(id=1)
    visitor_stat.total_hits += 1
    visitor_stat.save()
    
    context = {
        'total_bookings': total_bookings,
        'tickets_issued': tickets_issued,
        'news_posts': news_posts,
        'visitor_count': visitor_stat.total_hits,
    }
    return render(request, 'travel/index.html', context)

# 2. Book Flight (NEW - Phase 9 TravelTrip + Passengers)
@login_required
def book_flight(request):
    from .forms import TripForm, PassengerFormSet
    if request.method == 'POST':
        form = TripForm(request.POST)
        formset = PassengerFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            trip = form.save(commit=False)
            trip.status = 'DRAFT'
            trip.created_by = request.user
            trip.save()
            formset.instance = trip
            formset.save()
            return redirect('gfa_dashboard')
    else:
        form = TripForm()
        formset = PassengerFormSet()
    
    return render(request, 'travel/form.html', {'form': form, 'formset': formset})

# 2b. Airport Search API (JSON)
def airport_search(request):
    from django.http import JsonResponse
    from .models import Airport
    q = request.GET.get('q', '').strip()
    if len(q) < 1:
        return JsonResponse([], safe=False)
    results = Airport.objects.filter(
        Q(iata_code__icontains=q) | Q(city_name__icontains=q) | Q(name__icontains=q)
    )[:10]
    data = [{'id': a.id, 'iata': a.iata_code, 'city': a.city_name, 'name': a.name, 'intl': a.is_international} for a in results]
    return JsonResponse(data, safe=False)

# 3. Print Slip
@login_required
def print_requisition(request, pk):
    booking = get_object_or_404(BookingRequest, pk=pk)
    return render(request, 'travel/requisition_slip.html', {'booking': booking})

# 4. Upload Docs
@login_required
def upload_documents(request, pk):
    booking = get_object_or_404(BookingRequest, pk=pk)
    if request.method == 'POST':
        form = BookingUploadForm(request.POST, request.FILES, instance=booking)
        if form.is_valid():
            final_booking = form.save(commit=False)
            final_booking.status = 'FOR_ADMIN' # Route to Ruby
            final_booking.save()
            messages.success(request, 'Success! Booking submitted for SPMO Admin Review.')
            return redirect('gfa_dashboard')
    else:
        form = BookingUploadForm(instance=booking)
    return render(request, 'travel/upload.html', {'form': form, 'booking': booking})

# 5. DASHBOARD CONTROLLER
@login_required
def admin_dashboard(request):
    user = request.user
    
    # 1. Routing
    if user.is_superuser:
        all_transactions = BookingRequest.objects.all().order_by('-created_at')
        dashboard_title = "Executive Dashboard"
        template_name = 'travel/dashboard.html'
    elif hasattr(user, 'userprofile') and user.userprofile.office and user.is_staff:
        user_office = user.userprofile.office
        all_transactions = BookingRequest.objects.filter(unit_office=user_office).order_by('-created_at')
        dashboard_title = f"{user_office.name} Dashboard"
        template_name = 'travel/dashboard.html'
    else:
        all_transactions = BookingRequest.objects.filter(created_by=user).order_by('-created_at')
        dashboard_title = "My Travel Profile"
        template_name = 'travel/user_transactions.html'

    # 2. Statistics
    total_reqs = all_transactions.count()
    pending_reqs = all_transactions.filter(status='PENDING').count()
    # Multi-Role Pending Stats (Phase 11)
    pending_admin = all_transactions.filter(status='FOR_ADMIN').count()
    pending_supervisor = all_transactions.filter(status='FOR_SUPERVISOR').count()
    pending_chief = all_transactions.filter(status='FOR_CHIEF').count()
    approved_reqs = all_transactions.filter(status='APPROVED').count()
    booked_txns = all_transactions.filter(status='BOOKED')
    total_booked_count = booked_txns.count()
    total_spent = booked_txns.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    cancelled_count = all_transactions.filter(status='CANCELLED').count()
    settled_count = all_transactions.filter(status='SETTLED').count()
    draft_count = all_transactions.filter(status='DRAFT').count()

    # 3. Top 5 Recent Transactions
    recent_transactions = all_transactions[:5]

    # 4. Airline Balances & Formatting
    pal_display = {'val': '0', 'color': 'text-slate-400', 'raw': 0, 'limit': 0}
    ceb_display = {'val': '0', 'color': 'text-slate-400', 'raw': 0, 'limit': 0}
    dest_labels, dest_counts, office_labels, office_counts = '[]', '[]', '[]', '[]'
    monthly_labels, monthly_counts = '[]', '[]'
    status_labels, status_counts, status_colors = '[]', '[]', '[]'
    airline_labels, airline_counts = '[]', '[]'

    if template_name == 'travel/dashboard.html':
        def format_credit(credit_obj):
            amount = float(credit_obj.current_balance)
            limit = float(credit_obj.total_credit_limit)
            if amount <= 300000:
                color = 'text-red-600'
            elif amount <= 500000:
                color = 'text-orange-500'
            else:
                color = 'text-emerald-700'
            if amount >= 1_000_000:
                val = f"{amount/1_000_000:.1f}M"
            elif amount >= 1_000:
                val = f"{amount/1_000:.0f}K"
            else:
                val = f"{amount:.0f}"
            return {'val': val, 'color': color, 'raw': amount, 'limit': limit}

        try:
            pal_display = format_credit(AirlineCredit.objects.get(airline='PAL'))
        except AirlineCredit.DoesNotExist:
            pass
        try:
            ceb_display = format_credit(AirlineCredit.objects.get(airline='CEB'))
        except AirlineCredit.DoesNotExist:
            pass

        # Chart: Top Destinations (Top 8)
        dest_data = all_transactions.values('destination_details').annotate(count=Count('id')).order_by('-count')[:8]
        dest_labels = json.dumps([d['destination_details'][:25] for d in dest_data])
        dest_counts = json.dumps([d['count'] for d in dest_data])

        # Chart: Requests by Office (Top 6) - use department name
        from .models import Department
        office_data = all_transactions.values('unit_office').annotate(count=Count('id')).order_by('-count')[:6]
        office_id_to_name = {d.id: d.code for d in Department.objects.all()}
        office_labels = json.dumps([office_id_to_name.get(d['unit_office'], 'Other') for d in office_data])
        office_counts = json.dumps([d['count'] for d in office_data])

        # Chart: Monthly Trend (last 6 months)
        from django.db.models.functions import TruncMonth
        monthly_data = all_transactions.annotate(month=TruncMonth('departure_date')).values('month').annotate(count=Count('id')).order_by('month')
        monthly_data = list(monthly_data)[-6:]
        monthly_labels = json.dumps([d['month'].strftime('%b %Y') if d['month'] else 'N/A' for d in monthly_data])
        monthly_counts = json.dumps([d['count'] for d in monthly_data])

        # Chart: Status Breakdown
        status_map = {'DRAFT': ('#94a3b8', 'Draft'), 'PENDING': ('#eab308', 'Pending'), 'APPROVED': ('#3b82f6', 'Approved'),
                      'BOOKED': ('#059669', 'Booked'), 'SETTLED': ('#7c3aed', 'Settled'), 'CANCELLED': ('#dc2626', 'Cancelled')}
        # Added .order_by() to prevent ordering fields from breaking the GROUP BY
        s_data = all_transactions.values('status').annotate(count=Count('id')).order_by()
        status_labels = json.dumps([status_map.get(d['status'], ('#64748b', d['status']))[1] for d in s_data])
        status_counts = json.dumps([d['count'] for d in s_data])
        status_colors = json.dumps([status_map.get(d['status'], ('#64748b', ''))[0] for d in s_data])

        # Chart: Airline Split
        a_data = all_transactions.values('airline').annotate(count=Count('id'))
        airline_map = {'PAL': 'Philippine Airlines', 'CEB': 'Cebu Pacific'}
        airline_labels = json.dumps([airline_map.get(d['airline'], d['airline']) for d in a_data])
        airline_counts = json.dumps([d['count'] for d in a_data])

    context = {
        'recent_transactions': recent_transactions,
        'total_reqs': total_reqs, 'pending_reqs': pending_reqs, 'approved_reqs': approved_reqs,
        'total_booked_count': total_booked_count, 'total_spent': total_spent,
        'cancelled_count': cancelled_count, 'settled_count': settled_count, 'draft_count': draft_count,
        'pending_admin': pending_admin,
        'pending_supervisor': pending_supervisor,
        'pending_chief': pending_chief,
        'pal_display': pal_display, 'ceb_display': ceb_display,
        'dest_labels': dest_labels, 'dest_counts': dest_counts,
        'office_labels': office_labels, 'office_counts': office_counts,
        'monthly_labels': monthly_labels, 'monthly_counts': monthly_counts,
        'status_labels': status_labels, 'status_counts': status_counts, 'status_colors': status_colors,
        'airline_labels': airline_labels, 'airline_counts': airline_counts,
        'dashboard_title': dashboard_title,
    }
    return render(request, template_name, context)

# 6. Update Status
@login_required
def update_status(request, pk):
    if not request.user.is_staff:
        return redirect('index')
    
    if request.method == 'POST':
        booking = get_object_or_404(BookingRequest, pk=pk)
        action = request.POST.get('action')
        if action == 'approve':
            booking.status = 'APPROVED'
        elif action == 'return':
            booking.status = 'RETURNED'
            booking.remarks = request.POST.get('remarks')
        booking.save()
    return redirect('gfa_dashboard')

# 7. Admin Attach Ticket
# Add these imports at top if missing
from django.db import transaction
from django.core.mail import EmailMessage
from django.conf import settings
from .models import AirlineCredit

# ... (keep other views)

@login_required
@transaction.atomic # Locks DB to prevent partial saves
def admin_attach_ticket(request, pk):
    if not request.user.is_staff:
        return redirect('index')

    booking = get_object_or_404(BookingRequest, pk=pk)
    
    if request.method == 'POST':
        form = AdminBookingForm(request.POST, request.FILES, instance=booking)
        if form.is_valid():
            final = form.save(commit=False)
            
            # --- SAFETY CHECK: PREVENT DOUBLE DEDUCTION ---
            # If ticket is ALREADY booked, just update details (edit mode)
            if booking.status == 'BOOKED':
                final.save()
                messages.info(request, "Ticket updated successfully. No balance deducted (previously booked).")
                return redirect('booking_summary', pk=booking.pk)

            # --- DEDUCTION LOGIC (New Booking Only) ---
            cost = final.total_amount
            airline_code = final.airline
            
            if cost and cost > 0 and airline_code:
                try:
                    # 1. Lock the wallet row (Prevent race conditions)
                    credit = AirlineCredit.objects.select_for_update().get(airline=airline_code)
                    
                    # 2. Check Balance
                    if credit.current_balance >= cost:
                        
                        # 3. Deduct
                        credit.current_balance -= cost
                        credit.save()
                        
                        # 4. Save Status
                        final.status = 'BOOKED'
                        final.ticket_issued_at = timezone.now()
                        final.save()
                        
                        # --- PHASE 10: CREDIT LOG ---
                        CreditLog.objects.create(
                            trip=None, # For legacy BookingRequest
                            airline=airline_code,
                            amount=cost,
                            transaction_type='DEDUCTION',
                            balance_after=credit.current_balance,
                            remarks=f"Ticket issued for {final.full_name} (Ref: {final.booking_reference_no})",
                            processed_by=request.user
                        )
                        
                        # 5. Send Email
                        subject = f"Flight Confirmed: {final.origin} - {final.destination_details}"
                        recipient_list = [final.email]
                        sender_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'admin@example.com')
                        email = EmailMessage(subject, final.admin_instructions, sender_email, recipient_list)
                        
                        if 'doc_flight_ticket' in request.FILES:
                            f = request.FILES['doc_flight_ticket']
                            email.attach(f.name, f.read(), f.content_type)
                        
                        try:
                            email.send(fail_silently=False)
                            messages.success(request, f'Success! ₱{cost:,.2f} deducted from {credit.get_airline_display()}. Remaining: ₱{credit.current_balance:,.2f}')
                        except:
                            messages.warning(request, 'Ticket booked and deducted, but email failed.')

                        return redirect('booking_summary', pk=booking.pk)
                    
                    else:
                        messages.error(request, f'TRANSACTION FAILED: Insufficient funds in {credit.get_airline_display()}. Available: ₱{credit.current_balance:,.2f}')
                        return render(request, 'travel/admin_attach.html', {'form': form, 'booking': booking})

                except AirlineCredit.DoesNotExist:
                    messages.error(request, f'System Error: No Credit Wallet found for {airline_code}.')
                    return render(request, 'travel/admin_attach.html', {'form': form, 'booking': booking})
            
            # Fallback (If cost is 0, just save)
            final.status = 'BOOKED'
            final.save()
            messages.warning(request, "Ticket issued with ZERO cost.")
            return redirect('booking_summary', pk=booking.pk)

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
        form = AdminBookingForm(instance=booking, initial={'admin_instructions': standard_msg})
    
    return render(request, 'travel/admin_attach.html', {'form': form, 'booking': booking})

# 8. Summary
@login_required
def booking_summary(request, pk):
    from .models import TravelTrip, BookingRequest
    trip = TravelTrip.objects.filter(pk=pk).first()
    booking = trip if trip else get_object_or_404(BookingRequest, pk=pk)
    return render(request, 'travel/booking_summary.html', {'booking': booking, 'is_trip': bool(trip)})

# 10. TRANSACTION LIST (Robustness Phase 1)
@login_required
def transaction_list(request):
    from django.db.models import Q
    from django.core.paginator import Paginator
    from .models import STATUS_CHOICES, AIRLINE_CHOICES
    
    user = request.user
    
    # Base Queryset based on permissions
    if user.is_superuser:
        transactions = BookingRequest.objects.all()
    elif hasattr(user, 'userprofile') and user.userprofile.office and user.is_staff:
        transactions = BookingRequest.objects.filter(unit_office=user.userprofile.office)
    else:
        transactions = BookingRequest.objects.filter(created_by=user)
        
    # Search
    q = request.GET.get('q', '')
    if q:
        transactions = transactions.filter(
            Q(full_name__icontains=q) | 
            Q(destination_details__icontains=q) |
            Q(booking_reference_no__icontains=q) |
            Q(id__icontains=q)
        )
        
    # Advanced Filters
    status_f = request.GET.get('status')
    airline_f = request.GET.get('airline')
    date_f = request.GET.get('date')
    
    if status_f: transactions = transactions.filter(status=status_f)
    if airline_f: transactions = transactions.filter(airline=airline_f)
    if date_f: transactions = transactions.filter(departure_date=date_f)
    
    # Ordering
    transactions = transactions.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'q': q,
        'current_status': status_f,
        'current_airline': airline_f,
        'current_date': date_f,
        'AIRLINE_CHOICES': AIRLINE_CHOICES,
        'STATUS_CHOICES': STATUS_CHOICES,
    }
    return render(request, 'travel/transaction_list.html', context)

# --- PHASE 10: FINANCIAL VIEWS ---

@login_required
def credit_log_list(request):
    if not request.user.is_staff: return redirect('index')
    
    from .models import CreditLog
    logs = CreditLog.objects.all().order_by('-timestamp')
    
    # Filter by Airline
    airline = request.GET.get('airline')
    if airline: logs = logs.filter(airline=airline)
    
    # Filter by Type
    ttype = request.GET.get('type')
    if ttype: logs = logs.filter(transaction_type=ttype)
    
    return render(request, 'travel/financial/credit_log.html', {
        'logs': logs,
        'current_airline': airline,
        'current_type': ttype
    })

@login_required
def settlement_list(request):
    if not request.user.is_staff: return redirect('index')
    from .models import Settlement
    settlements = Settlement.objects.all().order_by('-settlement_date')
    return render(request, 'travel/booking_summary.html', {'booking': booking})

# 10. TRANSACTION LIST (Robustness Phase 1)
@login_required
def transaction_list(request):
    from django.db.models import Q
    from django.core.paginator import Paginator
    from .models import STATUS_CHOICES, AIRLINE_CHOICES
    
    user = request.user
    
    # Base Queryset based on permissions
    if user.is_superuser:
        transactions = BookingRequest.objects.all()
    elif hasattr(user, 'userprofile') and user.userprofile.office and user.is_staff:
        transactions = BookingRequest.objects.filter(unit_office=user.userprofile.office)
    else:
        transactions = BookingRequest.objects.filter(created_by=user)
        
    # Search
    q = request.GET.get('q', '')
    if q:
        transactions = transactions.filter(
            Q(full_name__icontains=q) | 
            Q(destination_details__icontains=q) |
            Q(booking_reference_no__icontains=q) |
            Q(id__icontains=q)
        )
        
    # Advanced Filters
    status_f = request.GET.get('status')
    airline_f = request.GET.get('airline')
    date_f = request.GET.get('date')
    
    if status_f: transactions = transactions.filter(status=status_f)
    if airline_f: transactions = transactions.filter(airline=airline_f)
    if date_f: transactions = transactions.filter(departure_date=date_f)
    
    # Ordering
    transactions = transactions.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'q': q,
        'current_status': status_f,
        'current_airline': airline_f,
        'current_date': date_f,
        'AIRLINE_CHOICES': AIRLINE_CHOICES,
        'STATUS_CHOICES': STATUS_CHOICES,
    }
    return render(request, 'travel/transaction_list.html', context)

# --- PHASE 10: FINANCIAL VIEWS ---

@login_required
def credit_log_list(request):
    if not request.user.is_staff: return redirect('index')
    
    from .models import CreditLog
    logs = CreditLog.objects.all().order_by('-timestamp')
    
    # Filter by Airline
    airline = request.GET.get('airline')
    if airline: logs = logs.filter(airline=airline)
    
    # Filter by Type
    ttype = request.GET.get('type')
    if ttype: logs = logs.filter(transaction_type=ttype)
    
    return render(request, 'travel/financial/credit_log.html', {
        'logs': logs,
        'current_airline': airline,
        'current_type': ttype
    })

@login_required
def settlement_list(request):
    if not request.user.is_staff: return redirect('index')
    from .models import Settlement
    settlements = Settlement.objects.all().order_by('-settlement_date')
    return render(request, 'travel/financial/settlement_list.html', {'settlements': settlements})

@login_required
@transaction.atomic
def settlement_create(request):
    if not request.user.is_staff: return redirect('index')
    
    from .forms import SettlementForm
    from .models import Settlement, AirlineCredit, CreditLog, TravelTrip, BookingRequest
    
    pnr = request.GET.get('pnr', '').strip()
    trip = None
    legacy = None
    error = None
    
    # 1. SEARCH LOGIC
    if pnr:
        found_id = None
        # Support GFA-000123 format or raw numeric ID
        if pnr.upper().startswith('GFA-'):
            try: found_id = int(pnr[4:])
            except ValueError: pass
        elif pnr.isdigit():
            found_id = int(pnr)
            
        if found_id:
            trip = TravelTrip.objects.filter(id=found_id).first()
            if not trip:
                legacy = BookingRequest.objects.filter(id=found_id).first()
        
        # If not found by ID, try searching by PNR field
        if not trip and not legacy:
            trip = TravelTrip.objects.filter(booking_reference_no=pnr).first()
            if not trip:
                legacy = BookingRequest.objects.filter(booking_reference_no=pnr).first()
            
        if not trip and not legacy:
            error = f"No booking found with Reference No: {pnr}"
        else:
            obj = trip or legacy
            if obj.status == 'SETTLED':
                error = f"Transaction {pnr} is already SETTLED."
            elif obj.status != 'BOOKED':
                error = f"Transaction {pnr} is in {obj.status} status. It must be BOOKED to settle."

    # 2. PROCESS LOGIC (POST)
    if request.method == 'POST' and (trip or legacy):
        form = SettlementForm(request.POST, request.FILES)
        if form.is_valid():
            target = trip or legacy
            
            # Save Settlement
            settlement = form.save(commit=False)
            settlement.processed_by = request.user
            settlement.airline = target.airline
            
            if trip: settlement.trip = trip
            else: settlement.legacy_booking = legacy
            
            settlement.save()
            
            # Update Transaction Status
            target.status = 'SETTLED'
            target.save()
            
            # Update Airline Credit (Replenishment)
            credit = AirlineCredit.objects.select_for_update().get(airline=target.airline)
            credit.current_balance += settlement.amount
            credit.save()
            
            # Log the Top-up (+)
            CreditLog.objects.create(
                airline=target.airline,
                amount=settlement.amount,
                transaction_type='TOP_UP',
                balance_after=credit.current_balance,
                remarks=f"Settlement for PNR: {pnr} | Ref: {settlement.reference_no}",
                processed_by=request.user,
                trip=trip,
                settlement=settlement # New link for traceability
            )
            
            messages.success(request, f'Settlement successful! {pnr} marked as SETTLED. ₱{settlement.amount:,.2f} added to {credit.get_airline_display()}.')
            return redirect('settlement_list')
    else:
        # Prepopulate amount if trip found
        initial_data = {}
        if trip: initial_data['amount'] = trip.total_amount
        elif legacy: initial_data['amount'] = legacy.total_amount
        form = SettlementForm(initial=initial_data)
        
    return render(request, 'travel/financial/settlement_form.html', {
        'form': form,
        'trip': trip,
        'legacy': legacy,
        'pnr': pnr,
        'error': error
    })

# 12. APPROVAL WORKFLOW (Phase 11)
@login_required
@transaction.atomic
def process_approval(request, pk):
    from .models import TravelTrip
    trip = get_object_or_404(TravelTrip, pk=pk)
    
    # Define Fixed Roles (Usernames)
    ROLE_MAPPING = {
        'FOR_ADMIN': 'rubyadmin',
        'FOR_SUPERVISOR': 'ajbasa',
        'FOR_CHIEF': 'chiefbagus',
    }
    
    if request.method == 'POST':
        action = request.POST.get('action') # 'approve' or 'return'
        comment = request.POST.get('comment', '')
        
        # Identity Check
        required_user = ROLE_MAPPING.get(trip.status)
        if required_user and request.user.username != required_user and not request.user.is_superuser:
            messages.error(request, 'You are not authorized to process this approval stage.')
            return redirect('booking_summary', pk=pk)

        if action == 'approve':
            if trip.status == 'FOR_ADMIN':
                trip.admin_verified = True
                trip.admin_verified_at = timezone.now()
                trip.admin_verified_by = request.user
                trip.status = 'FOR_SUPERVISOR'
                msg = 'Verified by SPMO Admin (Ruby). Forwarded to Supervisor.'
            elif trip.status == 'FOR_SUPERVISOR':
                trip.supervisor_verified = True
                trip.supervisor_verified_at = timezone.now()
                trip.supervisor_verified_by = request.user
                trip.status = 'FOR_CHIEF'
                msg = 'Verified by Supervisor (Aaron). Forwarded to Chief.'
            elif trip.status == 'FOR_CHIEF':
                trip.chief_approved = True
                trip.chief_approved_at = timezone.now()
                trip.chief_approved_by = request.user
                trip.status = 'APPROVED'
                msg = 'Final Approval by Chief Bagus. Ready for Processing.'
            else:
                msg = 'Approved.'
            
            trip.save()
            messages.success(request, msg)
            
        elif action == 'return':
            trip.status = 'RETURNED'
            trip.remarks = f'Returned by {request.user.get_full_name()}: {comment}'
            trip.save()
            messages.warning(request, f'Request returned to sender with comment: {comment}')
            
    return redirect('booking_summary', pk=pk)

