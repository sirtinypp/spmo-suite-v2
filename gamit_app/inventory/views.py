import json
from collections import Counter
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from django.urls import reverse

# Updated Imports
from .models import Asset, UserProfile, InspectionRequest, AssetBatch, AssetTransferRequest, ServiceLog

from .forms import (
    AssetTransactionForm, InspectionRequestForm, AssetBatchForm, 
    AssetTransferRequestForm, AdminBatchProcessForm, BatchItemFormSet,
    ServiceLogForm 
)

@login_required
def dashboard(request):
    # 1. INITIAL QUERYSET
    assets = Asset.objects.all()
    if not request.user.is_staff:
        try:
            user_office = request.user.userprofile.office
            assets = assets.filter(assigned_office__iexact=user_office)
        except (UserProfile.DoesNotExist, AttributeError):
            assets = Asset.objects.none()

    # 2. SLICERS / FILTERS
    selected_class = request.GET.get('asset_class', '')
    selected_nature = request.GET.get('asset_nature', '')
    selected_status = request.GET.get('status', '')

    if selected_class:
        assets = assets.filter(asset_class=selected_class)
    if selected_nature:
        assets = assets.filter(asset_nature=selected_nature)
    if selected_status:
        assets = assets.filter(status=selected_status)

    # 3. KPI METRICS
    total_count = assets.count()
    
    total_val_agg = assets.aggregate(sum=Sum('acquisition_cost'))
    total_value = total_val_agg['sum'] if total_val_agg['sum'] is not None else 0
    
    highest_asset = assets.order_by('-acquisition_cost').first()
    highest_val = highest_asset.acquisition_cost if highest_asset else 0
    highest_name = highest_asset.name if highest_asset else "N/A"

    # NEW METRIC 1: Asset Status Breakdown
    active_count = assets.filter(status='ACTIVE').count()
    active_percentage = (active_count / total_count * 100) if total_count > 0 else 0
    inactive_count = assets.filter(status__in=['INACTIVE', 'DISPOSED']).count()
    repair_count = assets.filter(status__in=['UNDER REPAIR', 'UNDER_REPAIR']).count()
    
    # NEW METRIC 2: Depreciation Alert (assets >5 years old)
    from datetime import date, timedelta
    five_years_ago = date.today() - timedelta(days=5*365)
    aging_assets_count = assets.filter(date_acquired__lt=five_years_ago).count()
    
    # NEW METRIC 3: Maintenance Cost (last 12 months)
    one_year_ago = timezone.now() - timedelta(days=365)
    maintenance_logs = ServiceLog.objects.filter(
        asset__in=assets,
        service_date__gte=one_year_ago
    )
    maintenance_cost = maintenance_logs.aggregate(sum=Sum('cost'))['sum'] or 0
    maintenance_count = maintenance_logs.count()
    
    # NEW METRIC 4: Office Utilization (top office by asset count)
    office_breakdown = assets.values('assigned_office').annotate(count=Count('id')).order_by('-count')
    top_office = office_breakdown[0] if office_breakdown else None
    top_office_name = top_office['assigned_office'] if top_office else "N/A"
    top_office_count = top_office['count'] if top_office else 0
    top_office_percentage = (top_office_count / total_count * 100) if total_count > 0 else 0
    
    # NEW METRIC 5: Recent Acquisitions (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_acquisitions = assets.filter(created_at__gte=thirty_days_ago)
    recent_count = recent_acquisitions.count()
    recent_value = recent_acquisitions.aggregate(sum=Sum('acquisition_cost'))['sum'] or 0

    def format_money(val):
        if val >= 1000000: return f"{val/1000000:.1f}M"
        return f"{val:,.2f}"

    # 4. DATA BREAKDOWNS (REMOVED - replaced with cards)
    # class_breakdown and nature_breakdown removed per user request

    # 5. SMART INSIGHTS
    if active_count > 0:
        if aging_assets_count > 20:
            insight_text = f"{aging_assets_count} assets are over 5 years old and may need replacement planning."
        elif repair_count > 5:
            insight_text = f"{repair_count} assets are currently under repair. Monitor maintenance costs."
        elif recent_count > 0:
            insight_text = f"{recent_count} new assets added in the last 30 days, totaling ₱{format_money(recent_value)}."
        else:
            insight_text = f"{active_percentage:.0f}% of your inventory is active. Top office: {top_office_name} with {top_office_count} assets."
    else:
        insight_text = "No inventory data available to generate insights."

    # 6. CONTEXT
    all_classes = [c[0] for c in Asset.CLASS_CHOICES]
    all_natures = [n[0] for n in Asset.NATURE_CHOICES]
    all_statuses = [s[0] for s in Asset.STATUS_CHOICES]

    recent_assets = assets.order_by('-created_at')[:5]

    context = {
        # Existing metrics (keep 3)
        'total_count': total_count,
        'total_value': format_money(total_value),
        'highest_val': format_money(highest_val),
        'highest_name': highest_name,
        
        # New Metric 1: Asset Status
        'active_count': active_count,
        'active_percentage': active_percentage,
        'inactive_count': inactive_count,
        'repair_count': repair_count,
        
        # New Metric 2: Depreciation Alert
        'aging_assets_count': aging_assets_count,
        
        # New Metric 3: Maintenance Cost
        'maintenance_cost': format_money(maintenance_cost),
        'maintenance_count': maintenance_count,
        
        # New Metric 4: Office Utilization
        'top_office_name': top_office_name,
        'top_office_count': top_office_count,
        'top_office_percentage': top_office_percentage,
        
        # New Metric 5: Recent Acquisitions
        'recent_acquisitions_count': recent_count,
        'recent_acquisitions_value': format_money(recent_value),
        
        # Keep existing
        'recent_assets': recent_assets,
        'insight_text': insight_text,
        'selected_class': selected_class,
        'selected_nature': selected_nature,
        'selected_status': selected_status,
        'all_classes': all_classes,
        'all_natures': all_natures,
        'all_statuses': all_statuses,
    }
    return render(request, 'inventory/dashboard.html', context)


# 2. ASSET LIST
@login_required
def asset_list(request):
    assets = Asset.objects.all()
    
    # 1. Permission Filter
    if not request.user.is_staff:
        try:
            user_office = request.user.userprofile.office
            if user_office:
                assets = assets.filter(assigned_office__iexact=user_office)
            else:
                assets = Asset.objects.none()
        except (UserProfile.DoesNotExist, AttributeError):
            assets = Asset.objects.none()

    # 2. Slicer Filters (Dropdowns)
    selected_class = request.GET.get('asset_class', '')
    selected_nature = request.GET.get('asset_nature', '')
    selected_status = request.GET.get('status', '') # Status filter
    selected_office = request.GET.get('office', '') # New Office filter

    if selected_class:
        assets = assets.filter(asset_class=selected_class)
    if selected_nature:
        assets = assets.filter(asset_nature=selected_nature)
    if selected_status:
        assets = assets.filter(status=selected_status)
    if selected_office:
        # Case insensitive filter for office
        assets = assets.filter(assigned_office__icontains=selected_office)

    # 3. Search Bar Filter
    search_term = request.GET.get('search', '').strip()
    if search_term:
        search_filter = (
            Q(property_number__icontains=search_term) |
            Q(name__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(accountable_firstname__icontains=search_term) |
            Q(accountable_surname__icontains=search_term) |
            Q(assigned_office__icontains=search_term) 
        )
        assets = assets.filter(search_filter)

    assets = assets.order_by('property_number')

    # 4. Context Data for Dropdowns
    all_classes = [c[0] for c in Asset.CLASS_CHOICES]
    all_natures = [n[0] for n in Asset.NATURE_CHOICES]
    all_statuses = [s[0] for s in Asset.STATUS_CHOICES]
    
    # Get unique offices for the dropdown (efficiently)
    all_offices = Asset.objects.order_by('assigned_office').values_list('assigned_office', flat=True).distinct()
    
    if not request.user.is_staff:
          try:
              user_office = request.user.userprofile.office
              all_offices = [user_office]
          except:
              all_offices = []

    context = {
        'object_list': assets,
        'search_term': search_term,
        
        # Dropdown Options
        'all_classes': all_classes,
        'all_natures': all_natures,
        'all_statuses': all_statuses,
        'all_offices': all_offices,

        # Selected Values (to keep dropdowns selected)
        'selected_class': selected_class,
        'selected_nature': selected_nature,
        'selected_status': selected_status,
        'selected_office': selected_office,
    }
    return render(request, 'inventory/asset_list.html', context)


# 3. ASSET DETAIL
@login_required
def asset_detail(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if not request.user.is_staff:
        try:
            user_office = request.user.userprofile.office
            if asset.assigned_office.lower() != user_office.lower():
                raise Http404("You are not authorized to view this asset.")
        except (UserProfile.DoesNotExist, AttributeError):
            raise Http404("User profile not found.")
    
    # Fetch related service logs
    service_logs = asset.service_logs.all().order_by('-service_date')
    
    # Instantiate an empty form for the modal
    form = ServiceLogForm()

    return render(request, 'inventory/asset_detail.html', {
        'asset': asset,
        'service_logs': service_logs,
        'form': form
    })


# 4. SITEMAP
@login_required
def sitemap(request):
    return render(request, 'inventory/sitemap.html')

# 5. ADD ASSET
@login_required
def add_asset_transaction(request):
    if request.method == 'POST':
        form = AssetTransactionForm(request.POST, request.FILES)
        if form.is_valid():
            asset = form.save(commit=False)
            if not request.user.is_staff:
                try:
                    asset.assigned_office = request.user.userprofile.office
                except (UserProfile.DoesNotExist, AttributeError):
                    messages.error(request, "Error: You do not have an office assigned.")
                    return redirect('dashboard')
            else:
                if not asset.assigned_office: asset.assigned_office = "Main (Admin)"
            asset.save()
            messages.success(request, f"Asset {asset.property_number} successfully recorded!")
            return redirect('asset_list')
    else:
        form = AssetTransactionForm()
    return render(request, 'inventory/transaction_add.html', {'form': form})

# 6. REQUEST INSPECTION
@login_required
def create_inspection_request(request):
    if request.method == 'POST':
        form = InspectionRequestForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            inspection = form.save(commit=False)
            inspection.requestor = request.user
            inspection.save()
            messages.success(request, f"Request {inspection.transaction_id} submitted successfully!")
            return redirect('dashboard')
    else:
        form = InspectionRequestForm(request.user)
    return render(request, 'inventory/transaction_request.html', {'form': form})

# 7. BATCH REQUEST
@login_required
def create_batch_request(request):
    try:
        current_office = request.user.userprofile.office
    except (UserProfile.DoesNotExist, AttributeError):
        current_office = "Unassigned"
    
    current_date_str = timezone.now().strftime('%Y-%m-%d')

    if request.method == 'POST':
        form = AssetBatchForm(request.POST, request.FILES)
        if form.is_valid():
            batch = form.save(commit=False)
            batch.requestor = request.user
            batch.requesting_unit = current_office 
            batch.save()
            messages.success(request, f"Batch {batch.transaction_id} submitted successfully!")
            return redirect('dashboard')
    else:
        form = AssetBatchForm(initial={
            'requesting_unit': current_office,
            'date_created': current_date_str
        })
    return render(request, 'inventory/transaction_batch.html', {'form': form})

# 8. TRANSACTION HISTORY LIST
@login_required
def transaction_history(request):
    if request.user.is_superuser:
        inspections = InspectionRequest.objects.all()
        batches = AssetBatch.objects.all()
        transfers = AssetTransferRequest.objects.all()
    else:
        inspections = InspectionRequest.objects.filter(requestor=request.user)
        batches = AssetBatch.objects.filter(requestor=request.user)
        transfers = AssetTransferRequest.objects.filter(requestor=request.user)

    APPROVED_STATUSES = ['Approved', 'APPROVED']
    RETURNED_STATUSES = ['Returned', 'RETURNED']
    PENDING_STATUSES = ['Pending Inspection', 'PENDING', 'Pending']
    
    total_requests = (
        inspections.count() +
        batches.count() +
        transfers.count()
    )
    
    approved_count = (
        inspections.filter(status__in=APPROVED_STATUSES).count() +
        batches.filter(status__in=APPROVED_STATUSES).count() +
        transfers.filter(status__in=APPROVED_STATUSES).count()
    )
    
    returned_count = (
        inspections.filter(status__in=RETURNED_STATUSES).count() +
        batches.filter(status__in=RETURNED_STATUSES).count() +
        transfers.filter(status__in=RETURNED_STATUSES).count()
    )
    
    pending_count = (
        inspections.filter(status__in=PENDING_STATUSES).count() +
        batches.filter(status__in=PENDING_STATUSES).count() +
        transfers.filter(status__in=PENDING_STATUSES).count()
    )
    
    # Logic for Office Breakdown (Requires Counter)
    inspection_pending_offices = inspections.filter(status__in=PENDING_STATUSES).values_list('requestor__userprofile__office', flat=True)
    batch_pending_offices = batches.filter(status__in=PENDING_STATUSES).values_list('requestor__userprofile__office', flat=True)
    transfer_pending_offices = transfers.filter(status__in=PENDING_STATUSES).values_list('requestor__userprofile__office', flat=True)
    
    all_pending_offices = list(inspection_pending_offices) + list(batch_pending_offices) + list(transfer_pending_offices)
    
    office_counts = Counter(o for o in all_pending_offices if o is not None and o != '')
    
    most_requesting_office = None
    if office_counts:
        office_name, count = office_counts.most_common(1)[0]
        most_requesting_office = {
            'requestor_office': office_name,
            'pending_count': count
        }

    context = {
        'inspections': inspections.order_by('-created_at'),
        'batches': batches.order_by('-created_at'),
        'transfers': transfers.order_by('-created_at'),
        'metrics': {
            'total': total_requests,
            'pending': pending_count,
            'approved': approved_count,
            'returned': returned_count,
            'office_breakdown': most_requesting_office,
        }
    }
    return render(request, 'inventory/transaction_list.html', context)

# 9. UPDATE INSPECTION STATUS
@login_required
def update_request_status(request, pk, action):
    messages.error(request, "Unauthorized action.")
    if not request.user.is_superuser:
        return redirect('transaction_history')
    inspection_req = get_object_or_404(InspectionRequest, pk=pk)
    if request.method == 'POST':
        remarks = request.POST.get('admin_remarks', '')
        if action == 'approve':
            inspection_req.status = 'Approved'
            inspection_req.admin_remarks = remarks
            messages.success(request, f"Request {inspection_req.transaction_id} Approved.")
        elif action == 'return':
            inspection_req.status = 'Returned'
            inspection_req.admin_remarks = remarks
            messages.warning(request, f"Request {inspection_req.transaction_id} Returned.")
        inspection_req.save()
    return redirect('transaction_history')

# 10. UPDATE BATCH STATUS
@login_required
def update_batch_status(request, pk, action):
    if not request.user.is_superuser:
        messages.error(request, "Unauthorized action.")
        return redirect('transaction_history')
    batch = get_object_or_404(AssetBatch, pk=pk)
    if request.method == 'POST':
        remarks = request.POST.get('admin_remarks', '')
        if action == 'approve':
            batch.status = 'APPROVED'
            batch.admin_remarks = remarks
            batch.save()
            messages.success(request, f"Batch {batch.transaction_id} Approved.")
        elif action == 'return':
            batch.status = 'RETURNED'
            batch.admin_remarks = remarks
            batch.save()
            messages.warning(request, f"Batch Returned.")
    return redirect('transaction_history')

# 11. CREATE TRANSFER REQUEST
@login_required
def create_transfer_request(request):
    if request.method == 'POST':
        form = AssetTransferRequestForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.requestor = request.user
            current_asset = transfer.asset
            fname = current_asset.accountable_firstname or ''
            lname = current_asset.accountable_surname or ''
            full_name = f"{fname} {lname}".strip()
            transfer.current_officer = full_name if full_name else "Unassigned"
            transfer.save()
            messages.success(request, f"Transfer Request {transfer.transaction_id} submitted!")
            return redirect('transaction_history')
    else:
        form = AssetTransferRequestForm(request.user)
    return render(request, 'inventory/transaction_transfer.html', {'form': form})

# 12. HELPER: GET ASSET INFO (PROTECTED)
@login_required
def get_asset_info(request, asset_id):
    asset = get_object_or_404(Asset, pk=asset_id)
    fname = asset.accountable_firstname or ''
    lname = asset.accountable_surname or ''
    officer = f"{fname} {lname}".strip()
    return JsonResponse({
        'property_number': asset.property_number,
        'name': asset.name,
        'officer': officer if officer else "Unassigned",
        'status': asset.get_status_display()
    })

# 13. UPDATE TRANSFER STATUS
@login_required
def update_transfer_status(request, pk, action):
    if not request.user.is_superuser:
        return redirect('transaction_history')
    transfer = get_object_or_404(AssetTransferRequest, pk=pk)
    if request.method == 'POST':
        transfer.admin_remarks = request.POST.get('admin_remarks', '')
        if action == 'approve':
            if transfer.status != 'APPROVED':
                asset = transfer.asset
                asset.accountable_firstname = transfer.new_officer_firstname
                asset.accountable_surname = transfer.new_officer_surname
                asset.save()
                transfer.status = 'APPROVED'
                transfer.save()
                messages.success(request, f"Transfer Approved. Asset assigned to {transfer.new_officer_firstname}.")
        elif action == 'return':
            transfer.status = 'RETURNED'
            transfer.save()
            messages.warning(request, "Transfer Request Returned.")
    return redirect('transaction_history')


# 14. ADMIN PROCESS BATCH (Add Items & Update Header)
@login_required
def process_batch_admin(request, pk):
    if not request.user.is_superuser: # Restrict to Admin
        messages.error(request, "Unauthorized access.")
        return redirect('dashboard')

    batch = get_object_or_404(AssetBatch, pk=pk)

    if request.method == 'POST':
        form = AdminBatchProcessForm(request.POST, instance=batch)
        formset = BatchItemFormSet(request.POST, request.FILES, instance=batch)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Batch details updated successfully.")
            return redirect('process_batch_admin', pk=batch.id) 
    else:
        form = AdminBatchProcessForm(instance=batch)
        formset = BatchItemFormSet(instance=batch)

    return render(request, 'inventory/transaction_batch_process.html', {
        'form': form,
        'formset': formset,
        'batch': batch
    })


# 15. PRINT ACCEPTANCE REPORT (IAR)
@login_required
def print_acceptance_report(request, pk):
    batch = get_object_or_404(AssetBatch, pk=pk)
    items = batch.items.all()
    
    grand_total = sum(item.total_price for item in items)
    
    context = {
        'batch': batch,
        'items': items,
        'grand_total': grand_total,
        'inspection_officer': "Mark Joshua M. Pedrosa", 
        'inspection_position': "Inspection Officer"
    }
    return render(request, 'inventory/print_acceptance_report.html', context)


# 16. PRINT PAR (One PAR per Physical Asset)
@login_required
def print_par(request, pk):
    batch = get_object_or_404(AssetBatch, pk=pk)
    raw_items = batch.items.all()
    
    par_pages = []
    
    for item in raw_items:
        for _ in range(item.quantity):
            par_pages.append({
                'quantity': 1, 
                'unit': item.unit,
                'description': item.description,
                'amount': item.amount,
                'total_cost': item.amount, 
                'image': item.image 
            })

    try:
        requestor_name = batch.requestor.get_full_name().upper() or batch.requestor.username.upper()
    except:
        requestor_name = "UNKNOWN END-USER"

    context = {
        'batch': batch,
        'par_pages': par_pages, 
        'issued_by_name': "ISAGANI L. BAGUS",
        'issued_by_position': "Acting Chief, UP System SPMO",
        'received_by_name': requestor_name,
        'received_by_position': "End-User"
    }
    return render(request, 'inventory/print_par.html', context)

# 17. ADD SERVICE LOG
@login_required
def add_service_log(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        form = ServiceLogForm(request.POST, request.FILES)
        if form.is_valid():
            log = form.save(commit=False)
            log.asset = asset
            log.save()
            messages.success(request, "Service/Maintenance Log added successfully.")
        else:
             messages.error(request, "Error adding log. Please check inputs.")
    return redirect('asset_detail', pk=pk)

# 18. PRINT SERVICE LOG
@login_required
def print_service_log(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    service_logs = asset.service_logs.all().order_by('service_date')
    
    total_cost = sum(log.cost for log in service_logs)
    
    return render(request, 'inventory/print_service_log.html', {
        'asset': asset,
        'service_logs': service_logs,
        'total_cost': total_cost
    })

# 19. DELETE SERVICE LOG (NEW)
@login_required
def delete_service_log(request, pk):
    log = get_object_or_404(ServiceLog, pk=pk)
    asset_id = log.asset.id # Save ID to redirect back
    
    # Optional: Security check (only staff can delete)
    if not request.user.is_staff:
        messages.error(request, "Unauthorized action. Only Admin can delete logs.")
        return redirect('asset_detail', pk=asset_id)

    log.delete()
    messages.success(request, "Service log deleted successfully.")
    return redirect('asset_detail', pk=asset_id)