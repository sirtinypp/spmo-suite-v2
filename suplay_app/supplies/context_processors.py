from .models import Order, APRRequest, Product, Settlement
from django.db.models import F

def sidebar_pulse(request):
    """
    Surgically injects real-time database counts into the global context 
    for the Admin Console Sidebar.
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        return {}

    try:
        pulse_data = {
            'pulse_pending_orders': Order.objects.filter(status='pending').count(),
            'pulse_open_aprs': APRRequest.objects.exclude(status__in=['CLOSED', 'CANCELLED']).count(),
            'pulse_low_stock': Product.objects.filter(stock__lte=F('reorder_point')).count(),
            'pulse_incoming_deliveries': APRRequest.objects.filter(status__in=['SENT', 'PAID', 'PARTIALLY_RECEIVED']).count(),
        }
    except Exception:
        # Fail-safe for migrations or schema mismatches
        pulse_data = {}

    return pulse_data
