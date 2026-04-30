from .models import AssetBatch, InspectionRequest, AssetTransferRequest, AssetReturnRequest, AssetLossReport, PropertyClearanceRequest
from workflow.models import Persona, Role

def pending_count(request):
    if not request.user.is_authenticated:
        return {'pending_count': 0}
        
    count = 0
    
    # 1. Superuser: Global Pending Count (All stages except FINALIZED)
    if request.user.is_superuser:
        # Simplification: Count all that are not FINALIZE/Released?
        pass # Optional optimization if superuser performance drops
        
    # 2. Persona Count: Tasks assigned explicitly to this user's active Personas
    active_roles = Persona.objects.filter(user=request.user, is_active=True).values_list('role', flat=True)
    if active_roles:
        count += AssetBatch.objects.filter(current_step__required_persona_role__in=active_roles).count()
        count += InspectionRequest.objects.filter(current_step__required_persona_role__in=active_roles).count()
        count += AssetTransferRequest.objects.filter(current_step__required_persona_role__in=active_roles).count()
        count += AssetReturnRequest.objects.filter(current_step__required_persona_role__in=active_roles).count()
        count += AssetLossReport.objects.filter(current_step__required_persona_role__in=active_roles).count()
        count += PropertyClearanceRequest.objects.filter(current_step__required_persona_role__in=active_roles).count()

    return {'pending_count': count}

def suite_wide_perms(request):
    """
    Globally available permission flags for Suite-wide navigation.
    """
    if not request.user.is_authenticated:
        return {'can_view_activity_log': False}
        
    if request.user.is_superuser:
        return {'can_view_activity_log': True}
        
    # Check for Chief/Supervisor active personas
    viewer_roles = ['SPMO_CHIEF', 'SPMO_SUPERVISOR', 'SPMO_ADMIN_SUPERVISOR']
    has_role = Persona.objects.filter(
        user=request.user, 
        is_active=True, 
        role__code__in=viewer_roles
    ).exists()
    
    return {'can_view_activity_log': has_role}


def unread_notifications(request):
    """Temporary disable until AssetNotification is restored."""
    return {
        'unread_notif_count': 0,
        'unread_notifs': [],
    }


def persona_context(request):
    """Inject all roles and active demo role for the Presentation Mode switcher."""
    ctx = {}
    if request.user.is_authenticated and request.user.is_superuser:
        ctx['all_roles'] = Role.objects.all()
        ctx['active_demo_role'] = request.session.get('active_demo_role', '')
    return ctx
