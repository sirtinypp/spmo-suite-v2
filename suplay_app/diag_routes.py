import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'office_supplies_project.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from supplies import views

# Set up test user
user, _ = User.objects.get_or_create(username='test_diag_all', is_staff=True)

factory = RequestFactory()
routes_to_test = [
    'admin_dashboard',
    'transaction_list',
    'inventory_list',
    'receive_delivery',
    'batch_list',
    'order_history',
    'home'
]

print(f"{'Route':<20} | {'Status':<10} | {'Error'}")
print("-" * 50)

for route_name in routes_to_test:
    try:
        url = reverse(route_name)
        request = factory.get(url)
        request.user = user
        
        # Get the view function from the route name (this is a bit hacky but works for simple URLs)
        # Actually I'll just use the view directly if I can or use the resolver
        from django.urls import resolve
        match = resolve(url)
        view_func = match.func
        
        response = view_func(request, **match.kwargs)
        if response.status_code == 200:
            print(f"{route_name:<20} | 200 OK     | None")
        else:
            print(f"{route_name:<20} | {response.status_code:<10} | Unexpected Status")
    except Exception as e:
        print(f"{route_name:<20} | CRASH      | {str(e)[:50]}")
