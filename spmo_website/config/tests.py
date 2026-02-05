from django.test import TestCase, Client
from django.urls import reverse

class WebsiteTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_status(self):
        try:
            url = reverse('home')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
        except Exception as e:
            self.fail(f"Home page failed to load: {e}")

    def test_login_page_status(self):
        try:
            url = reverse('login')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
        except Exception as e:
            self.fail(f"Login page failed to load: {e}")
