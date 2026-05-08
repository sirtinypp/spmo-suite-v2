import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()
from django.contrib.auth.models import User
from workflow.models import Persona, Role

# Remove SYSTEM_DEVELOPER from ajbasa
ajbasa = User.objects.get(username='ajbasa')
sysdev_role = Role.objects.get(code='SYSTEM_DEVELOPER')
Persona.objects.filter(user=ajbasa, role=sysdev_role).delete()
print("Removed SYSTEM_DEVELOPER from ajbasa")

# Also, grootadmin shouldn't have all those UNIT_HEAD/UNIT_AO personas left over from before we purged the users.
# Wait, those were assigned TO grootadmin because grootadmin is the fallback user? 
# Ah, the users were deleted, but maybe the departments had grootadmin as their fallback head.
# I'll leave grootadmin alone, since grootadmin is god mode anyway.
