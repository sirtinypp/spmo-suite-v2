from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def role_required(*roles):
    """
    Decorator for views that checks if a user has one of the allowed roles.
    Uses UserProfile.role.
    """
    def check_role(user):
        if not user.is_authenticated:
            return False
        if not hasattr(user, 'profile'):
            return False
        if user.profile.role in roles:
            return True
        return False
        
    return user_passes_test(check_role)

def scope_required(scope_name):
    """
    Decorator for views that checks if a user has access to a specific permission scope.
    Example: @scope_required('can_manage_assets')
    """
    def check_scope(user):
        if not user.is_authenticated:
            return False
        if not hasattr(user, 'profile'):
            return False
        # Dynamically check the property on UserProfile
        return getattr(user.profile, scope_name, False)
        
    return user_passes_test(check_scope)
