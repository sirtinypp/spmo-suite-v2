from .models import InspectionRequest

def pending_count(request):
    # Only calculate this for Superusers (Admins)
    if request.user.is_authenticated and request.user.is_superuser:
        # Count requests that match the default status from your models.py
        count = InspectionRequest.objects.filter(status='Pending Inspection').count()
        return {'pending_count': count}
    
    # Return 0 for everyone else
    return {'pending_count': 0}