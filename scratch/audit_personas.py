from workflow.models import Role, Persona

print('\n--- ROLE REGISTRY ---')
for role in Role.objects.all().order_by('name'):
    print(f'[{role.code}] {role.name}')

print('\n--- PERSONA REGISTRY ---')
for p in Persona.objects.select_related('user', 'role', 'department').all().order_by('role__name'):
    sig_status = '✅ SET' if p.signature_image else '❌ MISSING'
    dept_name = p.department.name if p.department else "N/A"
    full_name = f"{p.user.first_name} {p.user.last_name}" if p.user.first_name else p.user.username
    print(f'Identity: {full_name} | Role: {p.role.name} | Dept: {dept_name}')
    print(f'  - Position: {p.position_title or "N/A"}')
    print(f'  - Signature: {sig_status}')
