from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
# IMPORT AirlineCredit HERE
from .models import BookingRequest, UserProfile, AirlineCredit 

# 1. User Profile Inline
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Office Assignment (Tagging)'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    def get_inline_instances(self, request, obj=None):
        if not obj: return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# 2. Booking Request Admin
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'unit_office', 'destination_details', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'unit_office', 'airline')
    search_fields = ('full_name', 'unit_office', 'id')
    ordering = ('-created_at',)

admin.site.register(BookingRequest, BookingRequestAdmin)

# 3. NEW: Airline Credit Admin (This makes it show up)
class AirlineCreditAdmin(admin.ModelAdmin):
    list_display = ('airline', 'current_balance', 'total_credit_limit', 'last_updated')
    readonly_fields = ('last_updated',)

admin.site.register(AirlineCredit, AirlineCreditAdmin)