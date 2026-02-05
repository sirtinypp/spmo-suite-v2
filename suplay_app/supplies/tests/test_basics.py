from django.test import SimpleTestCase
from django.conf import settings

class BasicTests(SimpleTestCase):
    def test_environment(self):
        """Verify that Django settings are loaded."""
        self.assertTrue(settings.INSTALLED_APPS)

    def test_math(self):
        """Simple check to verify test runner."""
        self.assertEqual(1 + 1, 2)
