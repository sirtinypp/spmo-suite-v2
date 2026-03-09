from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats
from .models import (
    Asset, 
    UserProfile, 
    Department,
    InspectionRequest, 
    AssetBatch, 
    BatchItem,
    AssetTransferRequest,
    ServiceLog,
    AssetChangeLog,
    AssetNotification,
)
from .resources import AssetResource, patch_csv_format

# Apply the global monkeypatch for CSV encoding robustness here too,
# to ensure it's active even if resources.py was imported differently.
patch_csv_format()

# --- 0. DEPARTMENT ADMIN (New) ---
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

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
    
    # Disable automatic Admin decoding; our robust CSV patches handle it.
    from_encoding = None

    def get_import_formats(self):
        """
        Safely returns available import formats.
        """
        formats = super().get_import_formats()
        return [f for f in formats if f().is_available()]    
    # Existing Admin configuration
    list_display = ('property_number', 'name', 'department', 'assigned_office', 'status', 'acquisition_cost')
    search_fields = ('property_number', 'name', 'assigned_office', 'department__name') # Added department lookup
    list_filter = ('asset_class', 'asset_nature', 'status', 'department', 'date_acquired')
    
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
            'fields': ('department', 'assigned_office', ('accountable_firstname', 'accountable_surname'), ('latitude', 'longitude'))
        }),
        ('Documents & Images', {
            'fields': ('image_serial', 'image_condition', 'attachment')
        }),
        ('Finance & Valuation', {
            'classes': ('collapse',),
            'fields': ('fair_market_value', 'salvage_value', 'useful_life_years', 'depreciation_method', 'accumulated_depreciation', 'depreciation_start_date')
        }),
        ('Lifecycle', {
            'classes': ('collapse',),
            'fields': ('warranty_expiry', 'insurance_value', 'disposal_date', 'disposal_method', 'disposal_proceeds')
        }),
        ('Government / COA', {
            'classes': ('collapse',),
            'fields': ('uacs_object_code', 'fund_source', 'property_classification', 'appraisal_date', 'appraised_value')
        }),
    )

# --- USER PROFILE INLINE (Embedded in Standard User Admin) ---
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'GAMIT Profile'
    fk_name = 'user'

# Re-register UserAdmin
class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_department', 'get_role')
    
    def get_department(self, instance):
        return instance.userprofile.department.name if hasattr(instance, 'userprofile') and instance.userprofile.department else '-'
    get_department.short_description = 'Department'

    def get_role(self, instance):
        return instance.userprofile.get_role_display() if hasattr(instance, 'userprofile') else '-'
    get_role.short_description = 'Role'

# Unregister default User and register new one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


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

# --- 9. ASSET CHANGE LOG ---
@admin.register(AssetChangeLog)
class AssetChangeLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'asset', 'user', 'tab', 'field_name', 'old_value', 'new_value')
    list_filter = ('tab', 'timestamp')
    search_fields = ('asset__property_number', 'user__username', 'field_name')
    readonly_fields = ('asset', 'user', 'tab', 'field_name', 'old_value', 'new_value', 'timestamp', 'ip_address')
    date_hierarchy = 'timestamp'

# --- 10. ASSET NOTIFICATION ---
@admin.register(AssetNotification)
class AssetNotificationAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'recipient_role', 'asset', 'message', 'triggered_by', 'is_read')
    list_filter = ('recipient_role', 'is_read', 'created_at')
    search_fields = ('asset__property_number', 'message')
    date_hierarchy = 'created_at'