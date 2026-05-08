import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()
from workflow.models import (
    ActionProcess, Workflow, WorkflowPhase, WorkflowStep, SignatorySlot
)

# Order of deletion to respect FKs
models = [
    SignatorySlot,
    WorkflowStep,
    WorkflowPhase,
    Workflow,
    ActionProcess
]

print('Purging Workflow Metadata...')
for model in models:
    count = model.objects.count()
    model.objects.all().delete()
    print(f'  Deleted {count} {model.__name__} records')

print('\nWorkflow Metadata Purge Complete.')
