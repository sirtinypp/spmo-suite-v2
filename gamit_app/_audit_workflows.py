import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from workflow.models import Workflow, WorkflowPhase, WorkflowStep

with open('workflow_audit.md', 'w') as f:
    f.write("# GAMIT Workflow Blueprint Audit\n\n")
    
    workflows = Workflow.objects.all().order_by('name')
    if not workflows.exists():
        f.write("No Workflows found in the database.\n")
        
    for process in workflows:
        f.write(f"## {process.name} (`{process.process_id}`)\n")
        f.write(f"**Description:** {process.description}\n\n")
        
        phases = WorkflowPhase.objects.filter(workflow=process).order_by('order')
        for phase in phases:
            f.write(f"### Phase {phase.order}: {phase.name}\n")
            
            steps = WorkflowStep.objects.filter(phase=phase).order_by('order')
            for step in steps:
                req_role = step.required_persona_role.name if step.required_persona_role else "None"
                
                signatories = step.signatory_slots.all()
                sig_roles = [sig.role.name for sig in signatories]
                sig_str = ", ".join(sig_roles) if sig_roles else "None"
                
                f.write(f"- **Step {step.order}:** {step.label}\n")
                f.write(f"  - Required Primary Role: **{req_role}**\n")
                f.write(f"  - Signatory Slots: **{sig_str}**\n")
            f.write("\n")
        f.write("---\n\n")

print("Workflow audit generated.")
