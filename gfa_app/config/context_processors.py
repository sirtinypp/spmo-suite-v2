"""
Context processors for LIPAD application.
"""
from django.conf import settings


def sspmo_hub_url(request):
    """
    Make SSPMO_HUB_URL available in all templates.
    """
    return {
        'SSPMO_HUB_URL': settings.SSPMO_HUB_URL
    }
