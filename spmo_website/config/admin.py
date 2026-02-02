from django.contrib import admin
from .models import NewsPost, InspectionSchedule, Activity

@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date_posted', 'is_published', 'created_by')
    list_filter = ('category', 'is_published')
    search_fields = ('title', 'summary')

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'start_date', 'status', 'is_public')
    list_filter = ('category', 'status', 'is_public')
    search_fields = ('title', 'location', 'description')
    date_hierarchy = 'start_date'

@admin.register(InspectionSchedule)
class InspectionScheduleAdmin(admin.ModelAdmin):
    list_display = ('unit_name', 'activity', 'scheduled_date', 'status')
