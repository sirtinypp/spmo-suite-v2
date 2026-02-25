from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class TravelBookingRenderingTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_login(self.user)

    def test_booking_form_renders_inputs(self):
        """Verify that the booking form renders HTML inputs and not raw template variables."""
        # Manual Login
        self.client.post(reverse('login'), {'username': 'testuser', 'password': 'password'})
        
        response = self.client.get(reverse('gfa_create'), follow=True)
        
        # Check Status
        if response.status_code != 200:
             print(f"DEBUG: Status {response.status_code}")
             if hasattr(response, 'redirect_chain'):
                 print(f"DEBUG: Redirect Chain: {response.redirect_chain}")
             # print(f"DEBUG: Content: {response.content.decode('utf-8')[:500]}")
        
        self.assertEqual(response.status_code, 200, f"Expected 200 but got {response.status_code}. Redirect chain: {getattr(response, 'redirect_chain', 'N/A')}")
        
        # Check for HTML Input (Success Case)
        self.assertContains(response, 'name="full_name"')
        self.assertContains(response, 'placeholder="Enter your full name"')
        
        # Check for Absence of Raw Variables (Failure Case)
        content = response.content.decode('utf-8')
        if '{{ form.full_name }}' in content:
            self.fail("Found raw template variable '{{ form.full_name }}' in response!")
            
        print("\n✅ Internal Check Passed: Form renders <input> tags correctly.")
