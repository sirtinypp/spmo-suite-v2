import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'office_supplies_project.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from supplies.models import Product, Department, AnnualProcurementPlan
from supplies.views.client import home, add_to_cart
from django.contrib.sessions.middleware import SessionMiddleware

def run_test():
    print("--- STARTING ALLOCATION LOGIC TEST ---")

    # 1. Setup Data
    user, _ = User.objects.get_or_create(username='test_user_dept')
    dept, _ = Department.objects.get_or_create(name='Test Department')
    if not hasattr(user, 'profile'):
        from supplies.models import UserProfile
        UserProfile.objects.create(user=user, department=dept)
    else:
        user.profile.department = dept
        user.profile.save()

    product, _ = Product.objects.get_or_create(name='Test Product Restricted', price=100)
    
    # Ensure NO allocation exists for this year/previous year
    AnnualProcurementPlan.objects.filter(department=dept, product=product).delete()
    
    print(f"User: {user.username}, Dept: {dept.name}")
    print(f"Product: {product.name} (Should be RESTRICTED)")

    # 2. Test Home View (Visibility)
    factory = RequestFactory()
    request = factory.get('/')
    request.user = user
    
    # Simulate Session
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()

    response = home(request)
    
    # In home view, products are filtered from context. 
    # We can't easily check context without rendering, but we can check if product is in the queryset if we extracted the logic.
    # Instead, let's trust the add_to_cart logic which returns explicit errors.

    # 3. Test Add to Cart (Enforcement)
    print("\nAttempting to Add to Cart...")
    request = factory.post(f'/add-to-cart/{product.id}/', {'quantity': 1})
    request.user = user
    middleware.process_request(request)
    request.session.save()
    
    # Mock AJAX to get JSON response
    request.headers = {'x-requested-with': 'XMLHttpRequest'}

    response = add_to_cart(request, product.id)
    
    print(f"Response Status: {response.status_code}")
    if response.status_code == 400:
         print(f"SUCCESS: Blocked Payload: {response.content.decode()}")
    elif response.status_code == 200:
         print(f"FAILURE: Allowed Payload: {response.content.decode()}")
    else:
         print(f"Unexpected Status: {response.status_code}")

    # 4. Cleanup
    # Product.objects.filter(name='Test Product Restricted').delete()
    # User.objects.get(username='test_user_dept').delete()
    # Department.objects.get(name='Test Department').delete()
    print("\n--- TEST COMPLETE ---")

if __name__ == '__main__':
    run_test()
