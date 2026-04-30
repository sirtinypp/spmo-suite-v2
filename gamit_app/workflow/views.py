from django.shortcuts import redirect
from django.contrib import messages
from workflow.models import Role

def switch_persona(request, role_code):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Only Superusers can switch personas.")
        return redirect('dashboard')

    if role_code == 'reset':
        if 'active_demo_role' in request.session:
            del request.session['active_demo_role']
        messages.success(request, "Persona reset to Master Admin.")
    else:
        try:
            role = Role.objects.get(code=role_code)
            request.session['active_demo_role'] = role.code
            messages.success(request, f"Persona switched to: {role.name}")
        except Role.DoesNotExist:
            messages.error(request, f"Role code {role_code} not found.")

    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
