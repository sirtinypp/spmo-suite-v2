import json
from collections import Counter
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Updated Imports
from .models import Asset, UserProfile, InspectionRequest, AssetBatch, AssetTransferRequest, ServiceLog, AssetChangeLog, AssetNotification

from .forms import (
    AddAssetForm, AssetTransactionForm, InspectionRequestForm, AssetBatchForm, 
    AssetTransferRequestForm, AdminBatchProcessForm, BatchItemFormSet,
    ServiceLogForm,
    PropertyTabForm, FinanceTabForm, LifecycleTabForm, GovernmentTabForm,
)

@login_required
def dashboard(request):
    # 1. INITIAL QUERYSET
    assets = Asset.objects.all()
    
    # PERMISSION FILTER: Non-staff users only see their Department's assets
    if not request.user.is_staff:
        try:
            profile = request.user.userprofile
            if profile.department:
                assets = assets.filter(department=profile.department)
            else:
                assets = Asset.objects.none()
        except UserProfile.DoesNotExist:
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
    active_count = assets.filter(status='SERVICEABLE').count()
    active_percentage = (active_count / total_count * 100) if total_count > 0 else 0
    inactive_count = assets.filter(status__in=['INACTIVE', 'DISPOSED', 'UNSERVICEABLE']).count()
    repair_count = assets.filter(status='UNDER_REPAIR').count()
    
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
    
    # Metrics using Department model
    office_breakdown = assets.values('department__name').annotate(count=Count('id')).order_by('-count')
    top_office = office_breakdown[0] if office_breakdown else None
    top_office_name = top_office['department__name'] if top_office else "N/A"
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
            insight_text = f"{active_percentage:.0f}% of your inventory is serviceable. Top office: {top_office_name} with {top_office_count} assets."
    else:
        insight_text = "No inventory data available to generate insights."

    # 6. CONTEXT
    all_classes = [c[1] for c in Asset.CLASS_CHOICES]
    all_natures = [n[1] for n in Asset.ASSET_TYPE_CHOICES]
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
        # Dropdown Options
        'all_classes': all_classes,
        'all_natures': all_natures,
        'all_statuses': all_statuses,
    }
    return render(request, 'inventory/dashboard.html', context)


# 2. ASSET LIST
@login_required
def asset_list(request):
    assets = Asset.objects.all()
    
    # 1. Permission Filter: Non-staff users only see their Department's assets
    user_department = None
    if not request.user.is_staff:
        try:
            profile = request.user.userprofile
            user_department = profile.department
            if user_department:
                assets = assets.filter(department=user_department)
            else:
                assets = Asset.objects.none()
        except (UserProfile.DoesNotExist, AttributeError):
            assets = Asset.objects.none()

    # 2. Slicer Filters (Dropdowns)
    selected_class = request.GET.get('asset_class', '')
    selected_nature = request.GET.get('asset_nature', '')
    selected_status = request.GET.get('status', '') # Status filter
    selected_department = request.GET.get('department', '') # NEW: Department ID filter

    if selected_class:
        assets = assets.filter(asset_class=selected_class)
    if selected_nature:
        assets = assets.filter(asset_nature=selected_nature)
    if selected_status:
        assets = assets.filter(status=selected_status)
    if selected_department and request.user.is_staff: # Only staff can filter by other departments
         assets = assets.filter(department__id=selected_department)

    # 3. Search Bar Filter
    search_term = request.GET.get('search', '').strip()
    if search_term:
        search_filter = (
            Q(property_number__icontains=search_term) |
            Q(name__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(accountable_firstname__icontains=search_term) |
            Q(accountable_surname__icontains=search_term) |
            Q(department__name__icontains=search_term) 
        )
        assets = assets.filter(search_filter)

    # 4. Sorting logic
    sort_by = request.GET.get('sort', 'name')
    direction = request.GET.get('dir', 'asc')
    
    allowed_sort_fields = {
        'name': 'name',
        'prop': 'property_number',
        'date': 'date_acquired',
        'class': 'asset_class',
        'nature': 'asset_nature',
        'status': 'status',
        'dept': 'department__name'
    }
    
    sort_field = allowed_sort_fields.get(sort_by, 'name')
    if direction == 'desc':
        sort_field = '-' + sort_field
        
    assets = assets.order_by(sort_field)

    # 5. Pagination
    per_page = request.GET.get('per_page', 20)
    try:
        per_page = int(per_page)
    except (ValueError, TypeError):
        per_page = 20
        
    paginator = Paginator(assets, per_page)
    page = request.GET.get('page')
    try:
        assets_paginated = paginator.page(page)
    except PageNotAnInteger:
        assets_paginated = paginator.page(1)
    except EmptyPage:
        assets_paginated = paginator.page(paginator.num_pages)

    # 5. Context Data for Dropdowns
    all_classes = [c[1] for c in Asset.CLASS_CHOICES]
    all_natures = [n[1] for n in Asset.ASSET_TYPE_CHOICES]
    all_statuses = [s[0] for s in Asset.STATUS_CHOICES]
    
    # Get Departments for the dropdown
    from .models import Department # Ensure Department is imported locally or at top
    if request.user.is_staff:
        # Staff can see all departments
        all_departments = Department.objects.all().order_by('name')
    else:
        # Regular users only see their own department (or nothing if none assigned)
        if user_department:
            all_departments = [user_department]
        else:
            all_departments = []

    context = {
        'object_list': assets_paginated,
        'num_pages': paginator.num_pages,
        'total_count_all': assets.count(), # Full filtered count
        'search_term': search_term,
        
        # Dropdown Options
        'all_classes': all_classes,
        'all_natures': all_natures,
        'all_statuses': all_statuses,
        'all_departments': all_departments, # Renamed from all_offices

        # Selected Values (to keep dropdowns selected)
        'selected_class': selected_class,
        'selected_nature': selected_nature,
        'selected_status': selected_status,
        'selected_department': int(selected_department) if selected_department else '',
        
        # Sorting
        'sort_by': sort_by,
        'direction': direction,
        'per_page': per_page,
    }
    
    # Generate Sorting URLs
    def get_sort_url(field):
        curr_params = request.GET.copy()
        new_dir = 'desc' if (sort_by == field and direction == 'asc') else 'asc'
        curr_params['sort'] = field
        curr_params['dir'] = new_dir
        if 'page' in curr_params:
            curr_params.pop('page')
        return f"?{curr_params.urlencode()}"

    context['sort_urls'] = {
        'prop': get_sort_url('prop'),
        'name': get_sort_url('name'),
        'class': get_sort_url('class'),
        'nature': get_sort_url('nature'),
        'status': get_sort_url('status'),
        'dept': get_sort_url('dept'),
    }

    return render(request, 'inventory/asset_list.html', context)


# 3. ASSET DETAIL (Phase 5: Tab Forms + Role-Based Access)

def get_user_tab_permissions(user):
    """Returns dict of which tabs the user can edit based on role."""
    perms = {'property': False, 'finance': False, 'lifecycle': False, 'government': False}
    if not user.is_authenticated:
        return perms
    # Superusers can edit everything
    if user.is_superuser:
        return {k: True for k in perms}
    try:
        role = user.userprofile.role
    except (UserProfile.DoesNotExist, AttributeError):
        return perms
    # SPMO Admin: Property, Lifecycle, Government
    if role in ('SPMO_ADMIN', 'ADMIN_OFFICER'):
        perms['property'] = True
        perms['lifecycle'] = True
        perms['government'] = True
    # Accounting Admin: Finance only
    if role == 'ACCT_ADMIN':
        perms['finance'] = True
    return perms


def _detect_changes(asset, form, tab_name, user, request):
    """Detect field changes and create AssetChangeLog entries. Returns list of changed field names."""
    changed = []
    for field_name in form.changed_data:
        old_val = getattr(asset, field_name, None)
        new_val = form.cleaned_data.get(field_name)
        # Stringify for storage
        old_str = str(old_val) if old_val is not None else ''
        new_str = str(new_val) if new_val is not None else ''
        if old_str != new_str:
            AssetChangeLog.objects.create(
                asset=asset,
                user=user,
                tab=tab_name,
                field_name=field_name,
                old_value=old_str[:500],
                new_value=new_str[:500],
                ip_address=request.META.get('REMOTE_ADDR', ''),
            )
            changed.append(field_name)
    return changed


def _create_cross_office_notification(asset, user, tab_name, changed_fields):
    """Alert the OTHER office when changes are made."""
    if not changed_fields:
        return
    field_list = ', '.join(changed_fields[:5])
    suffix = f' (+{len(changed_fields) - 5} more)' if len(changed_fields) > 5 else ''
    msg = f"{user.get_full_name() or user.username} updated {tab_name}: {field_list}{suffix}"
    # SPMO edits → notify Accounting; Accounting edits → notify SPMO
    if tab_name in ('property', 'lifecycle', 'government'):
        target_role = 'ACCT_ADMIN'
    else:
        target_role = 'SPMO_ADMIN'
    AssetNotification.objects.create(
        asset=asset,
        recipient_role=target_role,
        triggered_by=user,
        message=msg,
    )


@login_required
def asset_detail(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if not request.user.is_staff:
        try:
            user_office = request.user.userprofile.office
            # Secure check: Verify user has access to this asset's department
            if asset.department != user.userprofile.department:
                raise Http404("You are not authorized to view this asset.")
        except (UserProfile.DoesNotExist, AttributeError):
            raise Http404("User profile not found.")

    # Role permissions
    tab_perms = get_user_tab_permissions(request.user)

    # Handle POST (tab-specific save)
    active_tab = request.POST.get('active_tab', 'property')
    if request.method == 'POST' and active_tab in ('property', 'finance', 'lifecycle', 'government'):
        TAB_FORMS = {
            'property': PropertyTabForm,
            'finance': FinanceTabForm,
            'lifecycle': LifecycleTabForm,
            'government': GovernmentTabForm,
        }
        if tab_perms.get(active_tab):
            FormClass = TAB_FORMS[active_tab]
            form_tab = FormClass(request.POST, instance=asset)
            if form_tab.is_valid():
                changed = _detect_changes(asset, form_tab, active_tab, request.user, request)
                form_tab.save()
                _create_cross_office_notification(asset, request.user, active_tab, changed)
                messages.success(request, f'{active_tab.title()} tab updated successfully.')
                return redirect('asset_detail', pk=pk)
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            messages.error(request, 'You do not have permission to edit this tab.')

    # Build form instances for each tab (GET or after POST errors)
    property_form = PropertyTabForm(instance=asset)
    finance_form = FinanceTabForm(instance=asset)
    lifecycle_form = LifecycleTabForm(instance=asset)
    government_form = GovernmentTabForm(instance=asset)

    # Fetch related service logs
    service_logs = asset.service_logs.all().order_by('-service_date')
    form = ServiceLogForm()

    return render(request, 'inventory/asset_detail.html', {
        'asset': asset,
        'service_logs': service_logs,
        'form': form,
        'tab_perms': tab_perms,
        'property_form': property_form,
        'finance_form': finance_form,
        'lifecycle_form': lifecycle_form,
        'government_form': government_form,
        'active_tab': active_tab if request.method == 'POST' else 'property',
    })


# 4. SITEMAP
@login_required
def sitemap(request):
    return render(request, 'inventory/sitemap.html')

# 5. ADD ASSET
@login_required
def add_asset_transaction(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to add assets.")
        return redirect('asset_list')
    
    if request.method == 'POST':
        form = AddAssetForm(request.POST, request.FILES)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.save()
            messages.success(request, f"Asset {asset.property_number} successfully added!")
            return redirect('asset_detail', pk=asset.pk)
    else:
        form = AddAssetForm()
    return render(request, 'inventory/asset_add.html', {'form': form})

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
        formset = BatchItemFormSet(request.POST, request.FILES)
        
        if form.is_valid() and formset.is_valid():
            batch = form.save(commit=False)
            batch.requestor = request.user
            batch.requesting_unit = current_office 
            
            # Auto-names for required docs
            batch.doc_1_name = "Purchase Order"
            batch.doc_2_name = "Purchase Request"
            if batch.doc_3_file:
                batch.doc_3_name = "Additional Document"

            batch.save()
            
            # Save Items
            formset.instance = batch
            formset.save()

            messages.success(request, f"Batch {batch.transaction_id} submitted successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AssetBatchForm(initial={
            'requesting_unit': current_office,
            'date_created': current_date_str
        })
        formset = BatchItemFormSet()

    return render(request, 'inventory/transaction_batch.html', {
        'form': form,
        'formset': formset
    })

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

# ==========================================
# 20. WORKFLOW VIEWS (NEW)
# ==========================================
from .models import UserSignature
from .forms import UserSignatureForm
from .workflow import WorkflowEngine
from .services import PARGenerator

@login_required
def upload_signature(request):
    """
    Allows users to upload their digital signature for PAR signing.
    """
    try:
        signature = request.user.signature
    except UserSignature.DoesNotExist:
        signature = None

    if request.method == 'POST':
        form = UserSignatureForm(request.POST, request.FILES, instance=signature)
        if form.is_valid():
            sig = form.save(commit=False)
            sig.user = request.user
            sig.save()
            messages.success(request, "Signature updated successfully.")
            return redirect('dashboard')
    else:
        form = UserSignatureForm(instance=signature)

    return render(request, 'inventory/upload_signature.html', {'form': form})

@login_required
def batch_detail(request, pk):
    """
    Detailed view for AssetBatch with Workflow Controls.
    """
    batch = get_object_or_404(AssetBatch, pk=pk)
    items = batch.items.all()
    logs = batch.approval_logs.all().order_by('-timestamp')
    
    # Check permissions logic
    # Determine allowed transitions for current user
    allowed_transitions = []
    
    try:
        current_state_rules = WorkflowEngine.TRANSITIONS.get(batch.status)
        if current_state_rules:
            required_role = current_state_rules['role']
            # Check if user has this role
            if request.user.groups.filter(name=required_role).exists() or request.user.is_superuser:
                 allowed_transitions.append({
                     'target': current_state_rules['target'],
                     'action': current_state_rules['action'],
                     'css_class': 'btn-success'  # simplified
                 })
    except Exception as e:
        print(f"Workflow error: {e}")

    return render(request, 'inventory/batch_detail.html', {
        'batch': batch,
        'items': items,
        'logs': logs,
        'allowed_transitions': allowed_transitions,
        'workflow_steps': [
            'ANTICIPATORY', 'AWAITING_DELIVERY', 'DELIVERY_VALIDATION', 
            'FOR_INSPECTION', 'FOR_SUPERVISOR_APPROVAL', 'FOR_CHIEF_PRE_APPROVAL',
            'FOR_AO_SIGNATURE', 'FOR_CHIEF_FINAL_SIGNATURE', 'PAR_RELEASED'
        ]
    })

@login_required
def approve_batch_workflow(request, pk, target_state):
    """
    Executes a workflow transition.
    """
    batch = get_object_or_404(AssetBatch, pk=pk)
    
    if request.method == 'POST':
        try:
            # Execute Transition
            WorkflowEngine.transition(batch, target_state, request.user)
            messages.success(request, f"Successfully transitioned to {target_state}")
            
            # TRIGGER PDF GENERATION
            # If moved to FOR_AO_SIGNATURE, generate Draft
            if target_state == 'FOR_AO_SIGNATURE':
                PARGenerator.generate_draft(batch)
                messages.info(request, "PAR Draft generated for AO Signature.")
            
            # If moved to PAR_RELEASED, Finalize
            elif target_state == 'PAR_RELEASED':
                PARGenerator.finalize_par(batch)
                messages.success(request, "PAR Finalized and Sealed!")

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            
    return redirect('batch_detail', pk=pk)