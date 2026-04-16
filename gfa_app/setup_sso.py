import os
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

site = Site.objects.get(id=1)
site.domain = 'lipad-sspmo-dev.up.edu.ph'
site.name = 'LIPAD Dev'
site.save()

cid = os.environ.get('GOOGLE_CLIENT_ID', '')
sec = os.environ.get('GOOGLE_CLIENT_SECRET', '')
app, created = SocialApp.objects.get_or_create(
    provider='google',
    defaults={'name': 'Google SSO', 'client_id': cid, 'secret': sec}
)
if not created:
    app.client_id = cid
    app.secret = sec
    app.save()
app.sites.add(site)
print('DONE', site.domain, app.client_id[:15])
