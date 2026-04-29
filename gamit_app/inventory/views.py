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
from .models import Asset, UserProfile, InspectionRequest, AssetBatch, AssetTransferRequest, ServiceLog, AssetChangeLog, AssetNotification, AssetReturnRequest, AssetLossReport, PropertyClearanceRequest, Department
from workflow.models import WorkflowMovementLog, WorkflowStep, Persona

from .forms import (
    AddAssetForm, AssetTransactionForm, InspectionRequestForm, AssetBatchForm, 
    AssetTransferRequestForm, AdminBatchProcessForm, BatchItemFormSet,
    ServiceLogForm,
    PropertyTabForm, FinanceTabForm, LifecycleTabForm, GovernmentTabForm,
    AssetReturnRequestForm, AssetLossReportForm, PropertyClearanceRequestForm
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
    all_classes = Asset.CLASS_CHOICES
    all_natures = Asset.ASSET_TYPE_CHOICES
    all_statuses = Asset.STATUS_CHOICES
    recent_assets = assets.order_by('-created_at')[:5]

    context = {
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
        # Support full-name search
        if " " in search_term:
            parts = search_term.split()
            search_filter |= (Q(accountable_firstname__icontains=parts[0]) & Q(accountable_surname__icontains=parts[-1]))
            
        assets = assets.filter(search_filter)

    # 4. Sorting logic
    sort_by = request.GET.get('sort', 'prop')
    direction = request.GET.get('dir', 'desc')
    
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

    # 5. Context Data for Dropdowns (Standardized Tuples)
    all_classes = Asset.CLASS_CHOICES
    all_natures = Asset.ASSET_TYPE_CHOICES
    all_statuses = Asset.STATUS_CHOICES
    
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
    if not form.changed_data:
        return changed

    # IMPORTANT: form.is_valid() has already mutated the 'asset' instance.
    # We must fetch the original state from the database to compare.
    old_instance = Asset.objects.get(pk=asset.pk)

    for field_name in form.changed_data:
        old_val = getattr(old_instance, field_name, None)
        new_val = form.cleaned_data.get(field_name)
        
        # Stringify for storage
        old_str = str(old_val) if old_val is not None else ''
        new_str = str(new_val) if new_val is not None else ''
        
        if old_str != new_str:
            AssetChangeLog.objects.create(
                asset=asset,
                user=user,
                tab=tab_name.upper(), # Standardize to match TAB_CHOICES
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
            
            # Trigger dynamic engine to place at Step 1
            WorkflowEngine.initialize_transaction(batch, 'BATCH_ACQ')

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

# 8. TRANSACTION HISTORY LIST (PERSONA TASK INBOX)
@login_required
def transaction_history(request):
    from workflow.models import Persona
    
    active_roles = Persona.objects.filter(user=request.user, is_active=True).values_list('role', flat=True)
    
    if request.user.is_superuser:
        inspections = InspectionRequest.objects.all()
        batches = AssetBatch.objects.all()
        transfers = AssetTransferRequest.objects.all()
        returns = AssetReturnRequest.objects.all()
        losses = AssetLossReport.objects.all()
        clearances = PropertyClearanceRequest.objects.all()
    else:
        # My Requests
        my_i = InspectionRequest.objects.filter(requestor=request.user)
        my_b = AssetBatch.objects.filter(requestor=request.user)
        my_t = AssetTransferRequest.objects.filter(requestor=request.user)
        my_r = AssetReturnRequest.objects.filter(requestor=request.user)
        my_l = AssetLossReport.objects.filter(requestor=request.user)
        my_c = PropertyClearanceRequest.objects.filter(requestor=request.user)
        
        if active_roles:
            # My Persona Tasks
            as_i = InspectionRequest.objects.filter(current_step__required_persona_role__in=active_roles)
            as_b = AssetBatch.objects.filter(current_step__required_persona_role__in=active_roles)
            as_t = AssetTransferRequest.objects.filter(current_step__required_persona_role__in=active_roles)
            as_r = AssetReturnRequest.objects.filter(current_step__required_persona_role__in=active_roles)
            as_l = AssetLossReport.objects.filter(current_step__required_persona_role__in=active_roles)
            as_c = PropertyClearanceRequest.objects.filter(current_step__required_persona_role__in=active_roles)
            
            inspections = (my_i | as_i).distinct()
            batches = (my_b | as_b).distinct()
            transfers = (my_t | as_t).distinct()
            returns = (my_r | as_r).distinct()
            losses = (my_l | as_l).distinct()
            clearances = (my_c | as_c).distinct()
        else:
            inspections = my_i
            batches = my_b
            transfers = my_t
            returns = my_r
            losses = my_l
            clearances = my_c

    # Calculate real-time metrics for the Smart Dashboard
    total_count = inspections.count() + batches.count() + transfers.count() + returns.count() + losses.count() + clearances.count()
    
    approved_count = (
        inspections.filter(status__iexact='Approved').count() +
        batches.filter(status__iexact='APPROVED').count() +
        transfers.filter(status__iexact='APPROVED').count() +
        returns.filter(status__iexact='FINALIZED').count() +
        losses.filter(status__iexact='FINALIZED').count() +
        clearances.filter(status__iexact='FINALIZED').count()
    )
    
    returned_count = (
        inspections.filter(Q(status__iexact='Returned') | Q(status__iexact='Rejected')).count() +
        batches.filter(Q(status__iexact='RETURNED') | Q(status__iexact='REJECTED')).count() +
        transfers.filter(Q(status__iexact='RETURNED') | Q(status__iexact='REJECTED')).count() +
        returns.filter(Q(status__icontains='RETURN') | Q(status__icontains='REJECT')).count() +
        losses.filter(Q(status__icontains='RETURN') | Q(status__icontains='REJECT')).count() +
        clearances.filter(Q(status__icontains='RETURN') | Q(status__icontains='REJECT')).count()
    )
    
    pending_count = total_count - (approved_count + returned_count)

    # Smart Insight: Office with most requests in current view
    all_requestors = (
        list(inspections.values_list('requestor__userprofile__office', flat=True)) +
        list(batches.values_list('requestor__userprofile__office', flat=True)) +
        list(transfers.values_list('requestor__userprofile__office', flat=True))
    )
    from collections import Counter
    counts = Counter(o for o in all_requestors if o)
    top_office = counts.most_common(1)
    office_insight = {'requestor_office': top_office[0][0], 'pending_count': top_office[0][1]} if top_office else None

    context = {
        'inspections': inspections.order_by('-created_at'),
        'batches': batches.order_by('-created_at'),
        'transfers': transfers.order_by('-created_at'),
        'returns': returns.order_by('-created_at'),
        'losses': losses.order_by('-created_at'),
        'clearances': clearances.order_by('-created_at'),
        'metrics': {
            'total': total_count,
            'approved': approved_count,
            'returned': returned_count,
            'pending': max(0, pending_count),
            'office_breakdown': office_insight,
        }
    }
    return render(request, 'inventory/transaction_list.html', context)

# 8b. TRANSACTION LEDGER (Unified History with Search/Filter/Sort)
@login_required
def transaction_ledger(request):
    search = request.GET.get('q', '').strip()
    type_filter = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')
    sort_by = request.GET.get('sort', 'date')
    direction = request.GET.get('dir', 'desc')

    is_admin = request.user.is_superuser
    active_roles = list(Persona.objects.filter(
        user=request.user, is_active=True
    ).values_list('role', flat=True)) if not is_admin else []

    def base_qs(model, related=None):
        if is_admin:
            qs = model.objects.all()
        else:
            qs = model.objects.filter(requestor=request.user)
            if active_roles:
                qs = qs | model.objects.filter(
                    current_step__required_persona_role__in=active_roles)
            qs = qs.distinct()
        if related:
            qs = qs.select_related(*related)
        return qs

    def normalize_status(raw):
        u = str(raw).upper()
        if u in ('APPROVED', 'PAR_RELEASED', 'FINALIZED'):
            return 'Approved'
        if u in ('RETURNED', 'REJECTED'):
            return 'Returned'
        return 'Pending'

    TYPE_MAP = {
        'BATCH': ('Acquisition', 'fas fa-boxes-packing', 'success',
                  AssetBatch, False, ['requestor']),
        'REQ':   ('Inspection', 'fas fa-search', 'info',
                  InspectionRequest, True, ['asset', 'requestor']),
        'TRF':   ('Transfer', 'fas fa-exchange-alt', 'warning',
                  AssetTransferRequest, True, ['asset', 'requestor']),
        'RET':   ('Return', 'fas fa-undo', 'primary',
                  AssetReturnRequest, True, ['asset', 'requestor']),
        'LOSS':  ('Loss Report', 'fas fa-exclamation-triangle', 'danger',
                  AssetLossReport, True, ['asset', 'requestor']),
        'CLR':   ('Clearance', 'fas fa-file-signature', 'secondary',
                  PropertyClearanceRequest, False, ['requestor']),
    }

    DETAIL_URLS = {
        'BATCH': 'batch_detail', 'TRF': 'transfer_detail',
        'RET': 'return_detail', 'LOSS': 'loss_detail', 'CLR': 'clearance_detail',
    }

    rows = []
    for code, (label, icon, color, model, has_asset, related) in TYPE_MAP.items():
        if type_filter and type_filter != code:
            continue

        qs = base_qs(model, related)

        # Search
        if search:
            # Support multi-word name searches
            q_s = (Q(transaction_id__icontains=search) |
                   Q(requestor__first_name__icontains=search) |
                   Q(requestor__last_name__icontains=search) |
                   Q(requestor__username__icontains=search))
            
            if " " in search:
                parts = search.split()
                q_s |= (Q(requestor__first_name__icontains=parts[0]) & Q(requestor__last_name__icontains=parts[-1]))

            if has_asset:
                q_s |= (Q(asset__name__icontains=search) |
                        Q(asset__property_number__icontains=search))
            elif code == 'BATCH':
                q_s |= (Q(supplier_name__icontains=search) |
                        Q(requesting_unit__icontains=search) |
                        Q(po_number__icontains=search))
            elif code == 'CLR':
                q_s |= Q(purpose__icontains=search)
            qs = qs.filter(q_s)

        # Status filter (Case-Insensitive & Inclusive)
        if status_filter == 'APPROVED':
            # Capture all successful/finalized states
            qs = qs.filter(Q(status__iexact='Approved') | Q(status__iexact='APPROVED') | 
                           Q(status__iexact='FINALIZED') | Q(status__iexact='PAR_RELEASED'))
        elif status_filter == 'PENDING':
            # Filter for anything NOT in a final state
            qs = qs.exclude(Q(status__iexact='Approved') | Q(status__iexact='APPROVED') | 
                            Q(status__iexact='FINALIZED') | Q(status__iexact='PAR_RELEASED') |
                            Q(status__iexact='RETURNED') | Q(status__iexact='REJECTED') |
                            Q(status__iexact='Rejected') | Q(status__iexact='Returned'))
        elif status_filter == 'RETURNED':
            qs = qs.filter(Q(status__iexact='RETURNED') | Q(status__iexact='REJECTED') |
                           Q(status__iexact='Returned') | Q(status__iexact='Rejected'))

        for obj in qs.order_by('-created_at')[:200]:
            if has_asset:
                a_label = obj.asset.property_number
                a_name = obj.asset.name
            elif code == 'BATCH':
                a_label = obj.supplier_name or obj.requesting_unit or '-'
                a_name = f"PO: {obj.po_number}" if obj.po_number else ''
            else:
                a_label = (obj.purpose[:50] + '...') if obj.purpose and len(obj.purpose) > 50 else (obj.purpose or '-')
                a_name = ''

            url_name = DETAIL_URLS.get(code, '')
            detail_url = reverse(url_name, args=[obj.pk]) if url_name else ''

            raw_status = obj.status or 'Pending'
            rows.append({
                'transaction_id': obj.transaction_id,
                'type_code': code,
                'type_label': label,
                'type_icon': icon,
                'type_color': color,
                'asset_label': a_label,
                'asset_name': a_name,
                'requestor_name': obj.requestor.get_full_name() or obj.requestor.username,
                'created_at': obj.created_at,
                'raw_status': raw_status,
                'norm_status': normalize_status(raw_status),
                'detail_url': detail_url,
            })

    # Sort
    rev = (direction == 'desc')
    sort_keys = {
        'id': lambda r: r['transaction_id'],
        'type': lambda r: r['type_label'],
        'status': lambda r: r['norm_status'],
    }
    rows.sort(key=sort_keys.get(sort_by, lambda r: r['created_at']), reverse=rev)

    # Paginate
    paginator = Paginator(rows, 20)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        'rows': page_obj,
        'total_count': len(rows),
        'search': search,
        'type_filter': type_filter,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'direction': direction,
        'type_choices': [
            ('BATCH', 'Acquisition'), ('REQ', 'Inspection'),
            ('TRF', 'Transfer'), ('RET', 'Return'),
            ('LOSS', 'Loss Report'), ('CLR', 'Clearance'),
        ],
        'status_choices': [
            ('PENDING', 'Pending'), ('APPROVED', 'Approved / Finalized'),
            ('RETURNED', 'Returned / Rejected'),
        ],
    }
    return render(request, 'inventory/transaction_history.html', context)


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


# 13b. PRINT PTR (Property Transfer Report)
@login_required
def print_ptr(request, pk):
    transfer = get_object_or_404(AssetTransferRequest, pk=pk)

    # Inject signatures from movement logs
    movement_logs = transfer.movement_logs.filter(signature_snapshot__isnull=False).order_by('timestamp') \
        if hasattr(transfer, 'movement_logs') else []
    signatures = {}

    for log in movement_logs:
        role_code = log.persona.role.code if log.persona and log.persona.role else ''
        entry = {
            'name': log.user.get_full_name() or log.user.username,
            'pos': log.persona.position_title if log.persona else '',
            'date': log.timestamp.date(),
            'img': log.signature_snapshot.url,
        }
        if role_code == 'SPMO_CLERK' and 'prepared' not in signatures:
            signatures['prepared'] = entry
        elif role_code == 'SPMO_SUPERVISOR' and 'reviewed' not in signatures:
            signatures['reviewed'] = entry
        elif role_code == 'SPMO_CHIEF' and 'approved' not in signatures:
            signatures['approved'] = entry

    # Released By = same as SPMO AO (re-use prepared or second AO log)
    if 'prepared' in signatures and 'released' not in signatures:
        signatures['released'] = signatures['prepared']

    # Posted By = SPMO Supervisor
    if 'reviewed' in signatures:
        signatures['posted'] = signatures['reviewed']

    return render(request, 'inventory/print_ptr.html', {
        'transfer': transfer,
        'signatures': signatures,
    })



# 13c. TRANSFER DETAIL PAGE
@login_required
def transfer_detail(request, pk):
    transfer = get_object_or_404(AssetTransferRequest, pk=pk)

    try:
        allowed_transitions = WorkflowEngine.get_allowed_transitions(transfer, request.user)
        workflow_steps = WorkflowEngine.get_workflow_steps(transfer)
    except Exception:
        allowed_transitions = []
        workflow_steps = []

    return render(request, 'inventory/transfer_detail.html', {
        'transfer': transfer,
        'req': transfer,  # alias for vertical_timeline snippet compatibility
        'allowed_transitions': allowed_transitions,
        'workflow_steps': workflow_steps,
    })


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

    first_item = batch.items.first()
    context = {
        'batch': batch,
        'par_pages': par_pages,
        'issued_by_name': "ISAGANI L. BAGUS",
        'issued_by_position': "Acting Chief, UP System SPMO",
        'received_name': requestor_name,
        'received_by_position': first_item.custodian_position if first_item else "End-User",
        'total_value': sum(item.amount for item in batch.items.all())
    }
    return render(request, 'inventory/print_par.html', context)


# 16b. PRINT PAR v2 (Alternate Template — Clean Modern Government Minimalist)
# Implements 1 Asset = 1 PAR page for print output
@login_required
def print_par_v2(request, pk):
    batch = get_object_or_404(AssetBatch, pk=pk)

    # Build one PAR page per physical asset
    par_pages = []
    
    # Primary: Use generated assets (finalized batches)
    assets = batch.generated_assets.all()
    if assets.exists():
        # Pre-fetch batch items for metadata lookup
        batch_items = list(batch.items.all())
        first_item = batch_items[0] if batch_items else None
        
        for asset in assets:
            # Try to match asset to its source BatchItem by description
            matched_item = None
            for bi in batch_items:
                if bi.description and asset.name and bi.description.lower() in asset.name.lower():
                    matched_item = bi
                    break
            if not matched_item:
                matched_item = first_item  # fallback
            
            par_pages.append({
                'property_number': asset.property_number or 'N/A',
                'description': asset.name,
                'custodian_position': matched_item.custodian_position if matched_item else '',
                'unit': matched_item.unit if matched_item else 'pc',
                'amount': asset.acquisition_cost or (matched_item.amount if matched_item else 0),
                'date_acquired': asset.date_acquired,
            })
    else:
        # Fallback: Use batch items (pre-finalization), one page per unit qty
        for item in batch.items.all():
            for i in range(item.quantity):
                par_pages.append({
                    'property_number': '(Pending)',
                    'description': item.description,
                    'custodian_position': item.custodian_position or '',
                    'unit': item.unit or 'pc',
                    'amount': item.amount,
                    'date_acquired': batch.created_at,
                })

    # --- SIGNATURE INJECTION (New for Simulation/PARv2) ---
    movement_logs = batch.movement_logs.filter(signature_snapshot__isnull=False).order_by('timestamp')
    signatures = {}
    
    # Map steps to specific signature keys for the template
    # Prepared (SPMO_AO)
    prep_log = movement_logs.filter(status_label__icontains='SPMO AO').first()
    if prep_log:
        signatures['prepared'] = {
            'name': prep_log.user.get_full_name() or prep_log.user.username,
            'pos': prep_log.persona.position_title if prep_log.persona else "SPMO Admin",
            'date': prep_log.timestamp.date(),
            'img': prep_log.signature_snapshot.url
        }

    # Inspected (INSPECTION_OFFICER)
    insp_log = movement_logs.filter(status_label__icontains='Inspection Signature').first()
    if insp_log:
        signatures['inspected'] = {
            'name': insp_log.user.get_full_name() or insp_log.user.username,
            'pos': insp_log.persona.position_title if insp_log.persona else "Inspection Officer",
            'date': insp_log.timestamp.date(),
            'img': insp_log.signature_snapshot.url
        }

    # Reviewed (SPMO_SUPERVISOR)
    rev_log = movement_logs.filter(status_label__icontains='Supervisor Signature').first()
    if rev_log:
        signatures['reviewed'] = {
            'name': rev_log.user.get_full_name() or rev_log.user.username,
            'pos': rev_log.persona.position_title if rev_log.persona else "SPMO Supervisor",
            'date': rev_log.timestamp.date(),
            'img': rev_log.signature_snapshot.url
        }

    # Authorized (SPMO_CHIEF)
    auth_log = movement_logs.filter(status_label__icontains='Chief Final Approval').first()
    if auth_log:
        signatures['authorized'] = {
            'name': auth_log.user.get_full_name() or auth_log.user.username,
            'pos': auth_log.persona.position_title if auth_log.persona else "Chief, SPMO",
            'date': auth_log.timestamp.date(),
            'img': auth_log.signature_snapshot.url
        }

    try:
        requestor_name = batch.requestor.get_full_name().upper() or batch.requestor.username.upper()
    except:
        requestor_name = "UNKNOWN END-USER"

    first_item = batch.items.first()
    context = {
        'batch': batch,
        'par_pages': par_pages,
        'issued_by_name': signatures.get('authorized', {}).get('name', "ISAGANI L. BAGUS"),
        'issued_by_position': signatures.get('authorized', {}).get('pos', "Director / SPMO Chief"),
        'received_name': requestor_name,
        'received_by_position': first_item.custodian_position if first_item else "End-User",
        'total_value': sum(item.amount for item in batch.items.all()),
        'signatures': signatures
    }
    return render(request, 'inventory/PARv2.html', context)


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

# 18.5 PRINT PROPERTY CARD (Single Asset)
@login_required
def print_property_card(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    return render(request, 'inventory/print_property_card.html', {
        'asset': asset
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
from .forms import PersonaSignatureForm
from workflow.models import Persona
from .workflow import WorkflowEngine
from .services import PARGenerator

@login_required
def upload_signature(request):
    """
    Allows users to manage digital signatures for their active Personas.
    """
    personas = Persona.objects.filter(user=request.user, is_active=True)
    
    if request.method == 'POST':
        persona_id = request.POST.get('persona_id')
        persona = get_object_or_404(Persona, id=persona_id, user=request.user)
        form = PersonaSignatureForm(request.POST, request.FILES, instance=persona)
        if form.is_valid():
            form.save()
            messages.success(request, f"Signature for {persona.role.name} updated.")
            return redirect('upload_signature')
    
    # Check completeness
    for p in personas:
        p.has_sig = bool(p.signature_image)
        p.form = PersonaSignatureForm(instance=p)

    return render(request, 'inventory/upload_signature.html', {
        'personas': personas
    })

@login_required
def batch_detail(request, pk):
    """
    Detailed view for AssetBatch with Workflow Controls.
    """
    batch = get_object_or_404(AssetBatch, pk=pk)
    items = batch.items.all()
    logs = batch.movement_logs.all().order_by('-timestamp')
    
    # Determine allowed transitions for current user based on DB setup
    try:
        allowed_transitions = WorkflowEngine.get_allowed_transitions(batch, request.user)
        workflow_steps = WorkflowEngine.get_workflow_steps(batch)
    except Exception as e:
        print(f"Workflow logic error: {e}")
        allowed_transitions = []
        workflow_steps = []

    return render(request, 'inventory/batch_detail.html', {
        'batch': batch,
        'items': items,
        'logs': logs,
        'allowed_transitions': allowed_transitions,
        'workflow_steps': workflow_steps

    })

@login_required
def approve_batch_workflow(request, pk, target_state):
    """
    Executes a workflow transition.
    """
    batch = get_object_or_404(AssetBatch, pk=pk)
    
    if request.method == 'POST':
        try:
            # 1. Capture Feedback / Remarks
            remarks = request.POST.get('remarks', '')
            
            # 2. Capture Manual Signature (if provided)
            manual_sig = request.FILES.get('manual_signature')
            
            # Execute Transition
            WorkflowEngine.transition(batch, target_state, request.user, remarks=remarks, manual_signature=manual_sig)
            
            messages.success(request, f"Workflow step executed successfully!")
            
            # TRIGGER PDF GENERATION
            # If moved to FOR_AO_SIGNATURE, generate Draft
            if batch.current_step and 'AO SIGNATURE' in batch.current_step.label.upper():
                # PARGenerator logic can be kept if it exists
                pass
            
            # If moved to FINALIZED
            elif target_state == 'FINALIZE':
                # PARGenerator logic here
                pass

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            
    return redirect('batch_detail', pk=pk)

# ==========================================
# 9. RETURN REQUEST (Creation & Detail)
# ==========================================
@login_required
def create_return_request(request):
    if request.method == 'POST':
        form = AssetReturnRequestForm(request.POST, request.FILES)
        if form.is_valid():
            req = form.save(commit=False)
            req.requestor = request.user
            req.save()
            WorkflowEngine.initialize_transaction(req, 'ASSET_RETURN')
            messages.success(request, f"Return Request {req.transaction_id} submitted.")
            return redirect('dashboard')
    else:
        form = AssetReturnRequestForm()
    return render(request, 'inventory/transaction_return.html', {'form': form})

@login_required
def return_detail(request, pk):
    req = get_object_or_404(AssetReturnRequest, pk=pk)
    logs = req.movement_logs.all().order_by('-timestamp')
    try:
        allowed_transitions = WorkflowEngine.get_allowed_transitions(req, request.user)
        workflow_steps = WorkflowEngine.get_workflow_steps(req)
    except Exception as e:
        allowed_transitions = []
        workflow_steps = []
    return render(request, 'inventory/return_detail.html', {
        'req': req, 'logs': logs, 'allowed_transitions': allowed_transitions, 'workflow_steps': workflow_steps
    })

@login_required
def approve_return_workflow(request, pk, target_state):
    req = get_object_or_404(AssetReturnRequest, pk=pk)
    if request.method == 'POST':
        try:
            WorkflowEngine.transition(req, target_state, request.user)
            messages.success(request, "Workflow step executed successfully.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    return redirect('return_detail', pk=pk)

# ==========================================
# 10. LOSS REPORT (Creation & Detail)
# ==========================================
@login_required
def create_loss_report(request):
    if request.method == 'POST':
        form = AssetLossReportForm(request.POST, request.FILES)
        if form.is_valid():
            req = form.save(commit=False)
            req.requestor = request.user
            req.save()
            WorkflowEngine.initialize_transaction(req, 'ASSET_LOSS_REPORT')
            messages.success(request, f"Loss Report {req.transaction_id} submitted.")
            return redirect('dashboard')
    else:
        form = AssetLossReportForm()
    return render(request, 'inventory/transaction_loss.html', {'form': form})

@login_required
def loss_detail(request, pk):
    req = get_object_or_404(AssetLossReport, pk=pk)
    logs = req.movement_logs.all().order_by('-timestamp')
    try:
        allowed_transitions = WorkflowEngine.get_allowed_transitions(req, request.user)
        workflow_steps = WorkflowEngine.get_workflow_steps(req)
    except Exception as e:
        allowed_transitions = []
        workflow_steps = []
    return render(request, 'inventory/loss_detail.html', {
        'req': req, 'logs': logs, 'allowed_transitions': allowed_transitions, 'workflow_steps': workflow_steps
    })

@login_required
def print_rlsddp(request, pk):
    req = get_object_or_404(AssetLossReport, pk=pk)
    return render(request, 'inventory/print_rlsddp.html', {
        'req': req,
        'asset': req.asset
    })

@login_required
def approve_loss_workflow(request, pk, target_state):
    req = get_object_or_404(AssetLossReport, pk=pk)
    if request.method == 'POST':
        try:
            WorkflowEngine.transition(req, target_state, request.user)
            messages.success(request, "Workflow step executed successfully.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    return redirect('loss_detail', pk=pk)

# ==========================================
# 11. CLEARANCE REQUEST (Creation & Detail)
# ==========================================
@login_required
def create_clearance_request(request):
    if request.method == 'POST':
        form = PropertyClearanceRequestForm(request.POST, request.FILES)
        if form.is_valid():
            req = form.save(commit=False)
            req.requestor = request.user
            req.save()
            WorkflowEngine.initialize_transaction(req, 'ASSET_CLEARANCE')
            messages.success(request, f"Clearance Request {req.transaction_id} submitted.")
            return redirect('dashboard')
    else:
        form = PropertyClearanceRequestForm()
    return render(request, 'inventory/transaction_clearance.html', {'form': form})

@login_required
def clearance_detail(request, pk):
    req = get_object_or_404(PropertyClearanceRequest, pk=pk)
    logs = req.movement_logs.all().order_by('-timestamp')
    try:
        allowed_transitions = WorkflowEngine.get_allowed_transitions(req, request.user)
        workflow_steps = WorkflowEngine.get_workflow_steps(req)
    except Exception as e:
        allowed_transitions = []
        workflow_steps = []
    return render(request, 'inventory/clearance_detail.html', {
        'req': req, 'logs': logs, 'allowed_transitions': allowed_transitions, 'workflow_steps': workflow_steps
    })

@login_required
def approve_clearance_workflow(request, pk, target_state):
    req = get_object_or_404(PropertyClearanceRequest, pk=pk)
    if request.method == 'POST':
        try:
            WorkflowEngine.transition(req, target_state, request.user)
            messages.success(request, "Workflow step executed successfully.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    return redirect('clearance_detail', pk=pk)

# ==========================================
# 12. IIRUP (Under Development Placeholder)
# ==========================================
@login_required
def create_iirup_request(request):
    return render(request, 'inventory/transaction_iirup.html')

# ==========================================
# 21. ADMINISTRATION: ACTIVITY LOG (NEW)
# ==========================================
@login_required
def activity_log(request):
    """
    Centralized Audit Trail for SPMO Administration.
    Visible to Superusers, Chief, and Supervisors.
    """
    from workflow.models import WorkflowMovementLog, Persona

    # 1. PERMISSION CHECK
    is_admin_viewer = False
    if request.user.is_superuser:
        is_admin_viewer = True
    else:
        # Check for Chief/Supervisor active personas
        viewer_roles = ['SPMO_CHIEF', 'SPMO_SUPERVISOR', 'SPMO_ADMIN_SUPERVISOR']
        if Persona.objects.filter(user=request.user, is_active=True, role__code__in=viewer_roles).exists():
            is_admin_viewer = True

    if not is_admin_viewer:
        messages.error(request, "Access denied. Only SPMO Administration can view global activity logs.")
        return redirect('dashboard')    # 2. QUERY LOGS
    all_logs = WorkflowMovementLog.objects.all().select_related(
        'user', 'persona', 'batch', 'transfer', 'inspection', 
        'return_request', 'loss_report', 'clearance'
    ).order_by('-timestamp')

    # 3. FILTERS (Apply to the base query before grouping)
    from .models import Department
    all_departments = Department.objects.all().order_by('name')
    
    dept_id = request.GET.get('department')
    selected_department = None
    if dept_id:
        try:
            selected_department = int(dept_id)
            all_logs = all_logs.filter(persona__department_id=selected_department)
        except (ValueError, TypeError):
            pass

    # Date Range Filters
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    from datetime import datetime, time
    from django.utils import timezone

    if start_date:
        try:
            dt_start = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            all_logs = all_logs.filter(timestamp__gte=dt_start)
        except ValueError:
            pass

    if end_date:
        try:
            dt_end = timezone.make_aware(datetime.combine(datetime.strptime(end_date, '%Y-%m-%d'), time.max))
            all_logs = all_logs.filter(timestamp__lte=dt_end)
        except ValueError:
            pass

    # Process Type Filter
    process_type = request.GET.get('process_type', '')
    if process_type:
        if process_type == 'BATCH':
            all_logs = all_logs.filter(batch__isnull=False)
        elif process_type == 'TRANSFER':
            all_logs = all_logs.filter(transfer__isnull=False)
        elif process_type == 'INSPECT':
            all_logs = all_logs.filter(inspection__isnull=False)
        elif process_type == 'RETURN':
            all_logs = all_logs.filter(return_request__isnull=False)
        elif process_type == 'LOSS':
            all_logs = all_logs.filter(loss_report__isnull=False)
        elif process_type == 'CLEARANCE':
            all_logs = all_logs.filter(clearance__isnull=False)

    # 4. DATA GROUPING (Process Monitor Logic)
    # We want to group logs by their parent transaction
    from collections import OrderedDict
    # --- UNIFIED LIVE ACTIVITY PULSE (ROBUST) ---
    # Fetch 50 latest of each type to ensure a deep enough pool for sorting
    workflow_moves = all_logs[:50]
    
    from .models import AssetChangeLog, Asset, ServiceLog
    asset_revisions = AssetChangeLog.objects.all().select_related('user', 'asset').order_by('-timestamp')[:50]
    new_assets = Asset.objects.all().order_by('-created_at')[:50]
    recent_services = ServiceLog.objects.all().select_related('asset').order_by('-created_at')[:50]
    
    # Normalize and Combine
    unified_pulse = []
    
    # 1. Workflow Moves (Standardized IDs)
    for log in workflow_moves:
        t_id = 'SYS'
        if log.batch: t_id = log.batch.transaction_id
        elif log.transfer: t_id = log.transfer.transaction_id
        elif log.inspection: t_id = log.inspection.transaction_id
        elif log.return_request: t_id = log.return_request.transaction_id
        elif log.loss_report: t_id = log.loss_report.transaction_id
        elif log.clearance: t_id = log.clearance.transaction_id

        unified_pulse.append({
            'user': log.user,
            'timestamp': log.timestamp,
            'action': log.action_taken,
            'type': 'WORKFLOW',
            'category': 'BATCH' if log.batch else 'TRANSFER' if log.transfer else 'INSPECT' if log.inspection else 'MOVE',
            'target_id': t_id
        })
        
    # 2. Asset Revisions (Edits)
    for rev in asset_revisions:
        unified_pulse.append({
            'user': rev.user,
            'timestamp': rev.timestamp,
            'action': f"Updated {rev.get_tab_display()}: {rev.field_name}",
            'type': 'REVISION',
            'category': 'EDIT',
            'target_id': rev.asset.property_number
        })

    # 3. New Asset Registrations
    for asset in new_assets:
        unified_pulse.append({
            'user': None,
            'timestamp': asset.created_at,
            'action': f"Newly Registered: {asset.name[:50]}",
            'type': 'CREATION',
            'category': 'NEW',
            'target_id': asset.property_number
        })

    # 4. Service / Maintenance Logs
    for service in recent_services:
        unified_pulse.append({
            'user': None,
            'timestamp': service.created_at,
            'action': f"{service.get_service_type_display()}: {service.description[:50]}",
            'type': 'SERVICE',
            'category': 'MAINT',
            'target_id': service.asset.property_number
        })
        
    # Final Sort and Slice (Top 25 for UI)
    live_feed = sorted(unified_pulse, key=lambda x: x['timestamp'], reverse=True)[:25]

    # Process Monitor Groups (Paginate groups, not individual moves)
    grouped_data = OrderedDict()
    
    for log in all_logs:
        # Determine unique key for transaction
        t_key = None
        if log.batch: t_key = f"batch_{log.batch.id}"
        elif log.transfer: t_key = f"transfer_{log.transfer.id}"
        elif log.inspection: t_key = f"inspect_{log.inspection.id}"
        elif log.return_request: t_key = f"return_{log.return_request.id}"
        elif log.loss_report: t_key = f"loss_{log.loss_report.id}"
        elif log.clearance: t_key = f"clear_{log.clearance.id}"
        else: t_key = f"sys_{log.id}" # Fallback for system logs

        if t_key not in grouped_data:
            grouped_data[t_key] = {
                'latest': log,
                'history': [],
                'type': t_key.split('_')[0]
            }
        else:
            grouped_data[t_key]['history'].append(log)

    # 5. PAGINATION (Paginate the groups)
    group_items = list(grouped_data.values())
    paginator = Paginator(group_items, 15) # 15 processes per page is better for vertical space
    page = request.GET.get('page')
    groups_paginated = paginator.get_page(page)

    return render(request, 'inventory/activity_log.html', {
        'grouped_transactions': groups_paginated,
        'live_feed': live_feed,
        'all_departments': all_departments,
        'selected_department': selected_department,
        'start_date': start_date,
        'end_date': end_date,
        'process_type': process_type
    })

# ==========================================
# 20. REPORTS & ANALYTICS
# ==========================================
@login_required
def reports_home(request):
    """Landing page for all inventory reports."""
    return render(request, 'inventory/reports_home.html')

@login_required
def rpcppe_report(request):
    """
    COA-Compliant Report on Physical Count of Property, Plant & Equipment (RPCPPE).
    Grouped by Department with totals.
    """
    # Filter by Serviceable PPE assets (excluding semi-expandable/expendable if needed)
    # The requirement is "reflect all assets grouped by department"
    assets_qs = Asset.objects.filter(status='SERVICEABLE').select_related('department').order_by('department__name', 'asset_class', 'name')
    
    grouped_data = {}
    grand_total_cost = 0

    total_assets_count = 0
    for asset in assets_qs:
        dept_name = asset.department.name if asset.department else "UNASSIGNED / GENERAL"
        if dept_name not in grouped_data:
            grouped_data[dept_name] = {
                'assets': [],
                'dept_total_cost': 0,
            }
        
        # Calculations for COA alignment
        qty_card = 1 # Asset is serialized by default
        qty_physical = asset.quantity_physical_count or 0
        unit_cost = asset.acquisition_cost or 0
        total_price = unit_cost * qty_physical
        
        # Attach to asset object for template access
        asset.qty_card = qty_card
        asset.total_price = total_price
        
        grouped_data[dept_name]['assets'].append(asset)
        grouped_data[dept_name]['dept_total_cost'] += total_price
        grand_total_cost += total_price
        total_assets_count += qty_physical

    context = {
        'grouped_data': grouped_data,
        'grand_total_cost': grand_total_cost,
        'total_assets_count': total_assets_count,
        'dept_count': len(grouped_data),
        'report_date': timezone.now().date(),
    }
    return render(request, 'inventory/rpcppe_report.html', context)