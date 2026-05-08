from django.contrib.auth.models import User
from inventory.models import Department
from workflow.models import Role, Persona

def generate_ghost_army():
    ao_role = Role.objects.get(code='UNIT_AO')
    head_role = Role.objects.get(code='UNIT_HEAD')
    password = "spmo2026"
    
    departments = Department.objects.all()
    print(f"Deploying Ghost Army for {departments.count()} departments...")
    
    count = 0
    for dept in departments:
        code = dept.code.lower().replace(' ', '_') if dept.code else f"dept_{dept.id}"
        
        # 1. Create/Get AO User
        ao_username = f"ao.{code}"
        ao_user, created = User.objects.get_or_create(username=ao_username)
        if created:
            ao_user.set_password(password)
            ao_user.first_name = "Unit AO"
            ao_user.last_name = dept.name[:30]
            ao_user.save()
            
        # Create AO Persona
        Persona.objects.get_or_create(
            user=ao_user,
            role=ao_role,
            department=dept,
            defaults={'position_title': f"Administrative Officer - {dept.name}"}
        )
        
        # 2. Create/Get Head User
        head_username = f"head.{code}"
        head_user, created = User.objects.get_or_create(username=head_username)
        if created:
            head_user.set_password(password)
            head_user.first_name = "Unit Head"
            head_user.last_name = dept.name[:30]
            head_user.save()
            
        # Create Head Persona
        Persona.objects.get_or_create(
            user=head_user,
            role=head_role,
            department=dept,
            defaults={'position_title': f"Office Head - {dept.name}"}
        )
        
        count += 2
        print(f"  [+] Plotted: {dept.name}")

    print(f"\nSUCCESS: {count} Personas deployed across {departments.count()} departments.")

if __name__ == "__main__":
    generate_ghost_army()
