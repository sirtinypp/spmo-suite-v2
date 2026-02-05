from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Asset, UserProfile
from django.urls import reverse
from datetime import date

class AssetSecurityTests(TestCase):
    def setUp(self):
        # 1. Create a "Finance" User
        self.user_finance = User.objects.create_user(username='finance_user', password='password123')
        UserProfile.objects.create(user=self.user_finance, office='Finance')

        # 2. Create an "IT" User
        self.user_it = User.objects.create_user(username='it_user', password='password123')
        UserProfile.objects.create(user=self.user_it, office='IT')

        # 3. Create Assets for both offices
        self.asset_finance = Asset.objects.create(
            property_number='FIN-001',
            name='Finance Laptop',
            date_acquired=date(2023, 1, 1),
            acquisition_cost=50000,
            assigned_office='Finance',
            status='SERVICEABLE'
        )

        self.asset_it = Asset.objects.create(
            property_number='IT-001',
            name='Server Rack',
            date_acquired=date(2023, 1, 1),
            acquisition_cost=100000,
            assigned_office='IT',
            status='SERVICEABLE'
        )

        self.client = Client()

    def test_asset_creation(self):
        """Test that assets are created correctly in the DB"""
        self.assertEqual(Asset.objects.count(), 2)
        self.assertEqual(self.asset_finance.assigned_office, 'Finance')

    def test_finance_user_sees_only_finance_assets(self):
        """
        CRITICAL TEST: 
        Log in as Finance User. 
        Should see Finance Asset.
        Should NOT see IT Asset.
        """
        self.client.login(username='finance_user', password='password123')
        response = self.client.get(reverse('asset_list'))
        
        # Check that Finance asset is in the list
        self.assertContains(response, 'Finance Laptop')
        # Check that IT asset is NOT in the list
        self.assertNotContains(response, 'Server Rack')

    def test_detail_view_security(self):
        """
        CRITICAL TEST:
        Finance User tries to access IT Asset URL directly.
        Should get 404 Not Found.
        """
        self.client.login(username='finance_user', password='password123')
        
        # Try to access the IT asset details
        url = reverse('asset_detail', args=[self.asset_it.id])
        response = self.client.get(url)
        
        # Should return 404 (Not Found), effectively hiding it
        self.assertEqual(response.status_code, 404)