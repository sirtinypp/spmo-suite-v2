from django.db import models
from django.contrib.auth.models import User

# ==========================================
# 1. CORE PERSONA / ROLES
# ==========================================

class Role(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Role Title")
    code = models.CharField(max_length=50, unique=True, verbose_name="System Code")
    description = models.TextField(blank=True, null=True)

    def __str__(self): return self.name

class Persona(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personas')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    department = models.ForeignKey('inventory.Department', on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'role', 'department')

    def __str__(self): 
        dept_str = f" ({self.department.name})" if self.department else ""
        return f"{self.user.username} as {self.role.name}{dept_str}"


# ==========================================
# 2. WORKFLOW BLUEPRINTS
# ==========================================

class ActionProcess(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self): return self.name

class Workflow(models.Model):
    name = models.CharField(max_length=150, unique=True)
    process = models.ForeignKey(ActionProcess, on_delete=models.CASCADE, related_name='workflows')
    description = models.TextField(blank=True, null=True)

    def __str__(self): return self.name

class WorkflowPhase(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='phases')
    name = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=10)

    class Meta:
        ordering = ['order']

    def __str__(self): return f"{self.workflow.name} - {self.name}"

class WorkflowStep(models.Model):
    phase = models.ForeignKey(WorkflowPhase, on_delete=models.CASCADE, related_name='steps')
    label = models.CharField(max_length=150, verbose_name="Step Label (Status)")
    order = models.PositiveIntegerField(default=10)
    
    # Required actor logic
    required_persona_role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Required Role to Action")

    class Meta:
        ordering = ['phase__order', 'order']

    def __str__(self): return f"[{self.phase.workflow.name}] {self.label}"

class SignatorySlot(models.Model):
    step = models.ForeignKey(WorkflowStep, on_delete=models.CASCADE, related_name='signatory_slots')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    label = models.CharField(max_length=100, help_text="e.g. 'Prepared By', 'Approved By'")
    rank = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['rank']

    def __str__(self): return f"{self.label} ({self.role.name})"


# ==========================================
# 3. MOVEMENT LOG
# ==========================================

class WorkflowMovementLog(models.Model):
    # Weak linkage to inventory models using lazy string reference
    batch = models.ForeignKey('inventory.AssetBatch', on_delete=models.CASCADE, null=True, blank=True, related_name='movement_logs')
    transfer = models.ForeignKey('inventory.AssetTransferRequest', on_delete=models.CASCADE, null=True, blank=True, related_name='movement_logs')
    inspection = models.ForeignKey('inventory.InspectionRequest', on_delete=models.CASCADE, null=True, blank=True, related_name='movement_logs')
    return_request = models.ForeignKey('inventory.AssetReturnRequest', on_delete=models.CASCADE, null=True, blank=True, related_name='movement_logs')
    loss_report = models.ForeignKey('inventory.AssetLossReport', on_delete=models.CASCADE, null=True, blank=True, related_name='movement_logs')
    clearance = models.ForeignKey('inventory.PropertyClearanceRequest', on_delete=models.CASCADE, null=True, blank=True, related_name='movement_logs')

    # Actor Context
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    persona = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True)
    role_name = models.CharField(max_length=100)
    unit_name = models.CharField(max_length=150)

    # Logic Snapshot
    status_label = models.CharField(max_length=150)
    action_taken = models.CharField(max_length=255)
    remarks = models.TextField(blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self): return f"Move: {self.status_label} by {self.user}"
