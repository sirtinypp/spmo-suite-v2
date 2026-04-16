from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

print("=== SSO Diagnostic ===")
apps = SocialApp.objects.all()
print(f"Total SocialApps: {apps.count()}")
for a in apps:
    print(f"ID: {a.id}, Provider: {a.provider}, Name: {a.name}")
    print(f"  Linked Sites: {[s.id for s in a.sites.all()]}")

sites = Site.objects.all()
print(f"\nTotal Sites: {sites.count()}")
for s in sites:
    print(f"ID: {s.id}, Domain: {s.domain}, Name: {s.name}")
print("======================")
