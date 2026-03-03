from .models import InspectionRequest, AssetNotification, UserProfile

def pending_count(request):
    # Only calculate this for Superusers (Admins)
    if request.user.is_authenticated and request.user.is_superuser:
        # Count requests that match the default status from your models.py
        count = InspectionRequest.objects.filter(status='Pending Inspection').count()
        return {'pending_count': count}
    
    # Return 0 for everyone else
    return {'pending_count': 0}


def unread_notifications(request):
    """Return unread AssetNotification count for the current user's role."""
    if not request.user.is_authenticated:
        return {'unread_notif_count': 0, 'unread_notifs': []}
    
    try:
        role = request.user.userprofile.role
    except (UserProfile.DoesNotExist, AttributeError):
        role = None
    
    # Superusers see all unread notifications
    if request.user.is_superuser:
        qs = AssetNotification.objects.filter(is_read=False).order_by('-created_at')[:10]
    elif role:
        qs = AssetNotification.objects.filter(recipient_role=role, is_read=False).order_by('-created_at')[:10]
    else:
        qs = AssetNotification.objects.none()
    
    return {
        'unread_notif_count': qs.count(),
        'unread_notifs': qs,
    }
