from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from supplies.models import Product, Department, AnnualProcurementPlan, UserProfile, Category
from supplies.views.client import add_to_cart
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
import json

class Command(BaseCommand):
    help = 'Test allocation logic'

    def handle(self, *args, **kwargs):
        self.stdout.write("--- STARTING ALLOCATION LOGIC TEST ---")

        # 1. Setup Data
        username = 'test_usr_logic'
        dept_name = 'Test Dept Logic'
        
        user, _ = User.objects.get_or_create(username=username)
        dept, _ = Department.objects.get_or_create(name=dept_name)
        
        if not hasattr(user, 'profile'):
            UserProfile.objects.create(user=user, department=dept)
        else:
            user.profile.department = dept
            user.profile.save()

        category, _ = Category.objects.get_or_create(name='Test Category')
        product, _ = Product.objects.get_or_create(name='Test Restricted Item', defaults={'price': 500, 'category': category})
        
        # Ensure NO allocation exists
        AnnualProcurementPlan.objects.filter(department=dept, product=product).delete()
        
        self.stdout.write(f"User: {user.username}, Dept: {dept.name}")
        self.stdout.write(f"Product: {product.name} (Should be RESTRICTED)")

        # 2. Test Add to Cart (Enforcement)
        self.stdout.write("\nAttempting to Add to Cart...")
        
        factory = RequestFactory()
        request = factory.post(f'/add-to-cart/{product.id}/', {'quantity': 1})
        request.user = user
        
        # Simulate Session
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        
        # Mock AJAX
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'

        response = add_to_cart(request, product.id)
        
        self.stdout.write(f"Response Status: {response.status_code}")
        
        if response.status_code == 400:
             content = json.loads(response.content.decode('utf-8'))
             self.stdout.write(self.style.SUCCESS(f"SUCCESS: Blocked Payload: {content['message']}"))
        elif response.status_code == 200:
             self.stdout.write(self.style.ERROR(f"FAILURE: Allowed Payload: {response.content.decode()}"))
        else:
             self.stdout.write(self.style.WARNING(f"Unexpected Status: {response.status_code}"))

        # Cleanup
        # product.delete()
        # user.delete()
        # dept.delete()
