from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# ---------------------------------------------------------
# PUBLIC VIEW (The Main Government Portal)
# ---------------------------------------------------------
def home(request):
    """
    Renders the public facing 'index.html' - simple static version
    """
    context = {
        'title': 'UP SSPMO | Official Public Portal',
    }
    return render(request, 'index.html', context)


# ---------------------------------------------------------
# PRIVATE VIEW (The Internal Dashboard/Launchpad)
# ---------------------------------------------------------
@login_required(login_url='login')
def admin_portal(request):
    """
    The secure dashboard for SPMO Staff.
    Only accessible after logging in.
    """
    apps = [
        {
            'name': 'GAMIT System',
            'description': 'Property & Asset Management',
            'url': 'http://gamit.sspmo.up.edu.ph/', 
            'admin_url': 'http://gamit.sspmo.up.edu.ph/admin/',
            'icon': 'bi-building-gear',
            'color': 'text-amber-600',
            'bg': 'bg-amber-50',
            'port': '80'
        },
        {
            'name': 'Virtual Store',
            'description': 'Office Supplies & Inventory',
            'url': 'http://suplay.sspmo.up.edu.ph/', 
            'admin_url': 'http://suplay.sspmo.up.edu.ph/admin/',
            'icon': 'bi-cart4',
            'color': 'text-emerald-600',
            'bg': 'bg-emerald-50',
            'port': '80'
        },
        {
            'name': 'GFA Portal',
            'description': 'Flight Bookings (PAL/Cebu Pac)',
            'url': 'http://lipad.sspmo.up.edu.ph/',
            'admin_url': 'http://lipad.sspmo.up.edu.ph/admin/',
            'icon': 'bi-airplane-engines',
            'color': 'text-blue-600',
            'bg': 'bg-blue-50',
            'port': '80'
        },
    ]

    context = {
        'apps': apps,
        'user': request.user,
    }
    
    return render(request, 'portal.html', context)
