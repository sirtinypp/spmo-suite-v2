from django.contrib import admin
from .models import NewsPost, InspectionSchedule

@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date_posted', 'is_published')
    list_filter = ('category', 'is_published')
    search_fields = ('title', 'summary')

@admin.register(InspectionSchedule)
class InspectionScheduleAdmin(admin.ModelAdmin):
    list_display = ('unit_name', 'activity', 'scheduled_date', 'status')
    list_filter = ('status', 'scheduled_date')
    search_fields = ('unit_name', 'activity')
    date_hierarchy = 'scheduled_date'