from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.db.models import Q
from .models import NewsPost, InspectionSchedule, Activity

# ---------------------------------------------------------
# PUBLIC VIEW (The Main Government Portal)
# ---------------------------------------------------------
def home(request):
    """
    Renders the public facing 'index.html' with dynamic News and Activity data.
    """
    # 1. Fetch Latest News
    try:
        news_list = NewsPost.objects.filter(is_published=True).order_by('-date_posted')[:3]
    except:
        news_list = []

    # 2. Fetch Upcoming Activities (Next 6)
    from django.utils import timezone
    now = timezone.now()
    try:
        activity_list = Activity.objects.filter(
            is_public=True,
            start_date__gte=now
        ).order_by('start_date')[:6]
    except:
        activity_list = []

    context = {
        'title': 'UP SSPMO | Official Public Portal',
        'news_list': news_list,
        'activity_list': activity_list,
        'current_time': now,
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
            'url': 'http://gamit-sspmo.up.edu.ph/', 
            'admin_url': 'http://gamit-sspmo.up.edu.ph/admin/',
            'icon': 'bi-building-gear',
            'color': 'text-amber-600',
            'bg': 'bg-amber-50',
            'port': '80'
        },
        {
            'name': 'Virtual Store',
            'description': 'Office Supplies & Inventory',
            'url': 'http://suplay-sspmo.up.edu.ph/', 
            'admin_url': 'http://suplay-sspmo.up.edu.ph/admin/',
            'icon': 'bi-cart4',
            'color': 'text-emerald-600',
            'bg': 'bg-emerald-50',
            'port': '80'
        },
        {
            'name': 'GFA Portal',
            'description': 'Flight Bookings (PAL/Cebu Pac)',
            'url': 'http://lipad-sspmo.up.edu.ph/',
            'admin_url': 'http://lipad-sspmo.up.edu.ph/admin/',
            'icon': 'bi-airplane-engines',
            'color': 'text-blue-600',
            'bg': 'bg-blue-50',
            'port': '80'
        },
    ]

    # --- REAL-TIME METRICS (Postgres Connection) ---
    import psycopg2
    import os

    def get_external_count(db_name, query):
        """Helper to safely fetch counts from other databases in the docker network"""
        try:
            # Use environment variables for connection, defaulting to docker-compose values
            conn = psycopg2.connect(
                dbname=db_name,
                user=os.environ.get('DB_USER', 'spmo_admin'),
                password=os.environ.get('DB_PASSWORD', 'secret_password'),
                host=os.environ.get('DB_HOST', 'db'), # 'db' is the service name in docker-compose
                port='5432'
            )
            cur = conn.cursor()
            cur.execute(query)
            result = cur.fetchone()[0]
            cur.close()
            conn.close()
            return result
        except Exception as e:
            # print(f"DB Error ({db_name}): {e}") # Debug only
            return 0

    # 1. GAMIT Metrics (Assets)
    active_assets = get_external_count('db_gamit', "SELECT COUNT(*) FROM inventory_asset WHERE status != 'DISPOSED'")
    pending_inspections = get_external_count('db_gamit', "SELECT COUNT(*) FROM inventory_inspectionrequest WHERE status = 'Pending Inspection'")

    # 2. SUPLAY Metrics (Supplies)
    # Using raw SQL to check stock <= reorder_point
    critical_stock = get_external_count('db_store', "SELECT COUNT(*) FROM supplies_product WHERE stock <= reorder_point")
    pending_orders = get_external_count('db_store', "SELECT COUNT(*) FROM supplies_order WHERE status = 'pending'")

    # 3. LIPAD Metrics (Travel)
    active_travels = get_external_count('db_gfa', "SELECT COUNT(*) FROM travel_bookingrequest WHERE status IN ('APPROVED', 'BOOKED')")
    pending_bookings = get_external_count('db_gfa', "SELECT COUNT(*) FROM travel_bookingrequest WHERE status = 'PENDING'")

    context = {
        'apps': apps,
        'user': request.user,
        'metrics': {
            'assets': active_assets,
            'pending_inspections': pending_inspections,
            'critical_stock': critical_stock,
            'pending_orders': pending_orders,
            'active_travels': active_travels,
            'pending_bookings': pending_bookings
        }
    }
    
    return render(request, 'portal.html', context)

class NewsArchiveView(ListView):
    model = NewsPost
    template_name = 'news_archive.html'
    context_object_name = 'news_list'
    paginate_by = 9
    ordering = ['-date_posted']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Search (?q=...)
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(summary__icontains=query)
            )
        
        # Category Filter (?cat=...)
        category = self.request.GET.get('cat')
        if category and category in dict(NewsPost.CATEGORY_CHOICES):
            queryset = queryset.filter(category=category)
            
        # Year Filter (?year=...)
        year = self.request.GET.get('year')
        if year:
             queryset = queryset.filter(date_posted__year=year)
             
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass current filters to context to maintain state in UI
        context['current_category'] = self.request.GET.get('cat', '')
        context['current_query'] = self.request.GET.get('q', '')
        
        year_param = self.request.GET.get('year')
        context['current_year'] = int(year_param) if year_param and year_param.isdigit() else None
        
        context['categories'] = NewsPost.CATEGORY_CHOICES
        # Get unique years for filter
        context['years'] = NewsPost.objects.dates('date_posted', 'year', order='DESC')
        return context