from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import (
    Asset, 
    UserProfile, 
    InspectionRequest, 
    AssetBatch, 
    BatchItem, # Make sure BatchItem is registered if you want to see items in admin
    AssetTransferRequest,
    ServiceLog # <--- ADDED ServiceLog
)
from .resources import AssetResource

# --- 1. INLINE FOR SERVICE LOGS (View logs inside Asset page) ---
class ServiceLogInline(admin.TabularInline):
    model = ServiceLog
    extra = 0 # Don't show empty rows by default
    fields = ('service_date', 'service_type', 'description', 'service_provider', 'cost', 'service_document')
    readonly_fields = ('created_at',)

# --- CORE ASSET MANAGEMENT (Includes Import/Export) ---

@admin.register(Asset)
class AssetAdmin(ImportExportModelAdmin): 
    # Link the AssetResource to the Admin class
    resource_class = AssetResource 
    
    # Existing Admin configuration
    list_display = ('property_number', 'name', 'assigned_office', 'status', 'acquisition_cost')
    search_fields = ('property_number', 'name', 'assigned_office')
    list_filter = ('asset_class', 'status', 'assigned_office')
    
    # ADDED THE INLINE HERE
    inlines = [ServiceLogInline]

    fieldsets = (
        (None, {
            'fields': (('property_number', 'name'), 'description', 'status', ('date_acquired', 'acquisition_cost'))
        }),
        ('Classification', {
            'fields': (('asset_class', 'asset_nature'),)
        }),
        ('Accountability & Location', {
            'fields': ('assigned_office', ('accountable_firstname', 'accountable_surname'), ('latitude', 'longitude'))
        }),
        ('Documents & Images', {
            'fields': ('image_serial', 'image_condition', 'attachment')
        })
    )

# --- USER PROFILE ---

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'office')
    search_fields = ('user__username', 'office')


# --- TRANSACTION MODELS ---

@admin.register(InspectionRequest)
class InspectionRequestAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'asset', 'requestor', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('transaction_id', 'asset__name', 'requestor__username')
    readonly_fields = ('transaction_id', 'requestor', 'created_at')
    
@admin.register(AssetBatch)
class AssetBatchAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'requestor', 'status', 'created_at', 'admin_remarks')
    list_filter = ('status', 'created_at')
    search_fields = ('transaction_id', 'requestor__username')
    readonly_fields = ('transaction_id', 'requestor', 'created_at')

# Optional: Register BatchItem if you want to see them individually in Admin
@admin.register(BatchItem)
class BatchItemAdmin(admin.ModelAdmin):
    list_display = ('description', 'batch', 'quantity', 'amount')

@admin.register(AssetTransferRequest)
class AssetTransferRequestAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'asset', 'requestor', 'status', 'new_officer_surname', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('transaction_id', 'asset__name', 'requestor__username', 'new_officer_surname')
    readonly_fields = ('transaction_id', 'requestor', 'current_officer', 'created_at')

# --- NEW: SERVICE LOG ADMIN (Standalone Table) ---
@admin.register(ServiceLog)
class ServiceLogAdmin(admin.ModelAdmin):
    list_display = ('service_date', 'asset', 'service_type', 'service_provider', 'cost')
    list_filter = ('service_type', 'service_date')
    search_fields = ('asset__property_number', 'service_provider', 'description')
    date_hierarchy = 'service_date'