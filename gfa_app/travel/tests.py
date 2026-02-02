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
        response = self.client.get(reverse('gfa_create'))
        
        # Check Status
        self.assertEqual(response.status_code, 200)
        
        # Check for HTML Input (Success Case)
        self.assertContains(response, '<input type="text" name="full_name"', status_code=200)
        self.assertContains(response, 'placeholder="Enter your full name"', status_code=200)
        
        # Check for Absence of Raw Variables (Failure Case)
        content = response.content.decode('utf-8')
        if '{{ form.full_name }}' in content:
            self.fail("Found raw template variable '{{ form.full_name }}' in response!")
            
        print("\n✅ Internal Check Passed: Form renders <input> tags correctly.")
