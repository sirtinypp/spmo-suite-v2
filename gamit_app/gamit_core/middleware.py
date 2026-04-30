from django.utils.deprecation import MiddlewareMixin
from workflow.models import Persona
import logging

logger = logging.getLogger(__name__)

class PresentationModeMiddleware(MiddlewareMixin):
    """
    Middleware to handle 'Presentation Mode' role hijacking for superusers.
    """
    def process_request(self, request):
        if request.user.is_authenticated and request.user.is_superuser:
            role_code = request.session.get('active_demo_role')
            if role_code:
                try:
                    # FIX: Filter via role__code
                    persona = Persona.objects.filter(role__code=role_code, is_active=True).first()
                    if persona:
                        request.user.active_demo_role = role_code
                        request.user.demo_persona = persona
                except Exception as e:
                    logger.error(f"PresentationModeMiddleware Error: {e}")
                    request.user.active_demo_role = None
            else:
                request.user.active_demo_role = None
        else:
            if hasattr(request.user, 'active_demo_role'):
                request.user.active_demo_role = None
