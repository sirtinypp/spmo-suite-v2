from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import render
from django.contrib.auth import get_user_model

User = get_user_model()


class UPSSOAdapter(DefaultSocialAccountAdapter):
    """
    Custom Social Account Adapter for SPMO Suite.
    Enforces:
    1. Only @up.edu.ph emails allowed
    2. Only pre-existing Django users (no self-registration)
    3. Auto-links Google account to existing user by email
    """

    def pre_social_login(self, request, sociallogin):
        email = sociallogin.account.extra_data.get('email', '')

        # Rule 1: Restrict to @up.edu.ph
        if not email.endswith('@up.edu.ph'):
            raise ImmediateHttpResponse(
                render(request, 'sso_error.html', {
                    'error': 'Access denied. Only @up.edu.ph email addresses are allowed.',
                    'email': email,
                })
            )

        # Rule 2: Must match an existing Django user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ImmediateHttpResponse(
                render(request, 'sso_error.html', {
                    'error': 'No account found for this email address. Please contact your administrator.',
                    'email': email,
                })
            )

        # Rule 3: Auto-link Google to existing Django user
        if not sociallogin.is_existing:
            sociallogin.connect(request, user)

    def is_open_for_signup(self, request, sociallogin):
        """Block all self-registration via SSO."""
        return False
