from django.contrib import admin
from .models import (
    Role,
    Persona,
    ActionProcess,
    Workflow,
    WorkflowPhase,
    WorkflowStep,
    SignatorySlot,
    WorkflowMovementLog,
)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'department', 'is_active')
    list_filter = ('role', 'is_active', 'department')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'department__name')

@admin.register(ActionProcess)
class ActionProcessAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ('name', 'process')
    list_filter = ('process',)

class WorkflowStepInline(admin.TabularInline):
    model = WorkflowStep
    extra = 1

@admin.register(WorkflowPhase)
class WorkflowPhaseAdmin(admin.ModelAdmin):
    list_display = ('workflow', 'name', 'order')
    list_filter = ('workflow',)
    inlines = [WorkflowStepInline]

class SignatorySlotInline(admin.TabularInline):
    model = SignatorySlot
    extra = 1

@admin.register(WorkflowStep)
class WorkflowStepAdmin(admin.ModelAdmin):
    list_display = ('label', 'phase', 'order', 'required_persona_role')
    list_filter = ('phase__workflow', 'phase')
    inlines = [SignatorySlotInline]

@admin.register(WorkflowMovementLog)
class WorkflowMovementLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'status_label', 'user', 'role_name', 'unit_name', 'action_taken')
    list_filter = ('status_label', 'role_name')
    search_fields = ('user__username', 'action_taken')
    date_hierarchy = 'timestamp'
