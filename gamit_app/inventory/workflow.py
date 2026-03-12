from django.utils import timezone
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import send_mail
from django.conf import settings
from .models import AssetBatch, InspectionRequest, AssetTransferRequest
from workflow.models import Workflow, WorkflowStep, Persona, WorkflowMovementLog
from .services import PARGenerator, ICSGenerator, PTRGenerator

class WorkflowEngine:
    """
    Database-driven Workflow Engine.
    Handles transitions, multi-persona validation, and movement logging.
    """

    @staticmethod
    def get_workflow_steps(transaction):
        """Returns rich step objects for the transaction's workflow (for UI Vertical Timeline)."""
        if transaction.current_step:
            steps = WorkflowStep.objects.filter(phase__workflow=transaction.current_step.phase.workflow).order_by('order')
            
            logs = transaction.movement_logs.all() if hasattr(transaction, 'movement_logs') else []
            timeline = []
            reached_current = False
            
            for step in steps:
                is_current = (transaction.current_step.id == step.id) and transaction.status != 'FINALIZED'
                if is_current:
                    reached_current = True
                    status_class = 'primary'
                    icon = 'fas fa-spinner fa-spin'
                elif not reached_current and transaction.status != 'FINALIZED':
                    status_class = 'success'
                    icon = 'fas fa-check'
                elif transaction.status == 'FINALIZED':
                    status_class = 'success'
                    icon = 'fas fa-check'
                else:
                    status_class = 'secondary'
                    icon = 'fas fa-circle'
                    
                # Attempt to find the log entry for this step
                step_log = None
                for l in logs:
                    if step.label == l.status_label or getattr(l, 'action_taken', '').endswith(step.label):
                        step_log = l
                        break

                timeline.append({
                    'label': step.label,
                    'role_expected': step.required_persona_role.name if step.required_persona_role else 'System',
                    'signatories': list(step.signatory_slots.all().values_list('role__name', flat=True)),
                    'is_current': is_current,
                    'status_class': status_class,
                    'icon': icon,
                    'log': step_log,
                })
            
            # Add FINALIZE pseudo-step
            timeline.append({
                'label': 'FINALIZED',
                'role_expected': 'System',
                'is_current': transaction.status == 'FINALIZED',
                'status_class': 'success' if transaction.status == 'FINALIZED' else 'secondary',
                'icon': 'fas fa-check-double' if transaction.status == 'FINALIZED' else 'fas fa-flag-checkered',
                'log': list(logs)[0] if transaction.status == 'FINALIZED' and logs else None, # Latest log usually finalize
            })
            return timeline
        return []

    @staticmethod
    def get_allowed_transitions(transaction, user):
        """Returns the permitted next steps for the given transaction and user."""
        allowed_transitions = []
        current_step = transaction.current_step
        if not current_step:
            return allowed_transitions
            
        required_role = current_step.required_persona_role
        signatory_roles = list(current_step.signatory_slots.all().values_list('role', flat=True))
        
        has_permission = False
        if required_role:
             has_permission = Persona.objects.filter(user=user, role=required_role, is_active=True).exists()
        
        if not has_permission and signatory_roles:
             has_permission = Persona.objects.filter(user=user, role__id__in=signatory_roles, is_active=True).exists()

        if has_permission or user.is_superuser:
                # Calculate what the next sequential step is
                next_step = WorkflowStep.objects.filter(
                    phase__workflow=current_step.phase.workflow,
                    order__gt=current_step.order
                ).order_by('order').first()
                
                if next_step:
                    allowed_transitions.append({
                        'target': str(next_step.id),
                        'action': f"Advance to: {next_step.label}",
                        'css_class': 'btn-success'
                    })
                else: 
                    # If there's no next step, we are finalizing the workflow
                    allowed_transitions.append({
                        'target': 'FINALIZE',
                        'action': 'Finalize & Close Transaction',
                        'css_class': 'btn-primary'
                    })
        return allowed_transitions

    @staticmethod
    def transition(transaction, target_step_id_or_action, user, remarks=''):
        """Executes a specific workflow transition, strictly enforcing DB rules."""
        current_step = transaction.current_step
        if not current_step:
            raise ValidationError("Transaction has no current workflow step.")
            
        # 1. Enforce Role Permissions & Signatory Slots
        required_role = current_step.required_persona_role
        signatory_roles = list(current_step.signatory_slots.all().values_list('role', flat=True))
        
        active_persona = None
        
        # Check primary role
        if required_role:
            active_persona = Persona.objects.filter(user=user, role=required_role, is_active=True).first()
            
        # Fallback to signatory slots if primary is not met
        if not active_persona and signatory_roles:
            active_persona = Persona.objects.filter(user=user, role__id__in=signatory_roles, is_active=True).first()

        if not active_persona and not user.is_superuser:
            role_names = [required_role.name] if required_role else []
            if signatory_roles:
                from workflow.models import Role
                role_names += list(Role.objects.filter(id__in=signatory_roles).values_list('name', flat=True))
            
            raise PermissionDenied(f"User {user.username} lacks required signatory role(s): {', '.join(set(role_names))}")
        
        # 2. Identify Target Path
        if target_step_id_or_action == 'FINALIZE':
            next_step = None
            target_label = "FINALIZED"
        else:
            try:
                next_step = WorkflowStep.objects.get(id=int(target_step_id_or_action))
                target_label = next_step.label
            except (ValueError, TypeError, WorkflowStep.DoesNotExist):
                raise ValidationError("Invalid transition target ID.")
                
        # 3. Update Transaction States
        transaction.current_step = next_step
        if hasattr(transaction, 'status'):
            # Keep string field synced for fallback UI views
            transaction.status = target_label if target_label != 'FINALIZED' else 'PAR_RELEASED'
            
        # 3.5 Check for Document Generation if Finalized
        if target_step_id_or_action == 'FINALIZE':
            if isinstance(transaction, AssetBatch):
                # Simple logic for now: We assume all items in a batch belong to one type of document.
                # In robust versions, this checks individual asset total values.
                # But typically a batch represents a single acquisition request and generates ONE document representing all items.
                if getattr(transaction, 'total_value', 0) >= 50000:
                    PARGenerator.finalize_par(transaction)
                else:
                    ICSGenerator.finalize_ics(transaction)
            elif isinstance(transaction, AssetTransferRequest):
                PTRGenerator.finalize_ptr(transaction)

        transaction.save()
        
        # 4. Generate the Comprehensive Audit Log
        role_label = active_persona.role.name if active_persona else 'Superuser'
        unit_label = active_persona.department.name if active_persona and active_persona.department else 'System/Admin'
        
        log_kwargs = {
            'user': user,
            'persona': active_persona,
            'role_name': role_label,
            'unit_name': unit_label,
            'status_label': target_label,
            'action_taken': f"Advanced to {target_label}",
            'remarks': remarks
        }
        
        if isinstance(transaction, AssetBatch):
            log_kwargs['batch'] = transaction
        elif isinstance(transaction, InspectionRequest):
            log_kwargs['inspection'] = transaction
        elif isinstance(transaction, AssetTransferRequest):
            log_kwargs['transfer'] = transaction
        elif isinstance(transaction, AssetReturnRequest):
            log_kwargs['return_request'] = transaction
        elif isinstance(transaction, AssetLossReport):
            log_kwargs['loss_report'] = transaction
        elif isinstance(transaction, PropertyClearanceRequest):
            log_kwargs['clearance'] = transaction
            
        WorkflowMovementLog.objects.create(**log_kwargs)
        
        # Trigger Email Notification to the next role
        if next_step:
            WorkflowEngine._send_notification_to_next_role(transaction, next_step)
        
        return transaction

    @staticmethod
    def _send_notification_to_next_role(transaction, next_step):
        """Dispatches an email to all active Personas who match the required role for the next step."""
        if not next_step.required_persona_role:
            return
            
        required_role = next_step.required_persona_role
        
        # Determine strict departmental scope if the transaction has a requesting_unit
        # For Phase 2 baseline, we broadcast to the Role. In production, we'd filter by unit as well.
        target_personas = Persona.objects.filter(role=required_role, is_active=True).select_related('user')
        
        recipient_emails = [p.user.email for p in target_personas if p.user.email]
        
        if recipient_emails:
            subject = f"GAMIT Action Required: {next_step.label}"
            t_id = getattr(transaction, 'transaction_id', 'Transaction')
            message = (
                f"Hello,\n\n"
                f"A transaction requires your attention as a {required_role.name}.\n"
                f"Transaction ID: {t_id}\n"
                f"Current Status: {next_step.label}\n\n"
                f"Please log in to GAMIT to review and process this document."
            )
            try:
                # Use fail_silently=True to prevent SMTP delays from crashing the web request
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@spmo.edu.ph'),
                    recipient_list=list(set(recipient_emails)), 
                    fail_silently=True
                )
            except Exception as e:
                print(f"SMTP Notification Error: {e}")

    @staticmethod
    def initialize_transaction(transaction, workflow_process_code):
        """Used during transaction creation to securely hook it into Step 1 of a specific workflow."""
        try:
            workflow = Workflow.objects.get(process__code=workflow_process_code)
            first_step = WorkflowStep.objects.filter(phase__workflow=workflow).order_by('order').first()
            if first_step:
                transaction.current_step = first_step
                if hasattr(transaction, 'status'):
                    transaction.status = first_step.label
                transaction.save()
        except Workflow.DoesNotExist:
            print(f"Warning: Workflow process code {workflow_process_code} not seeded.")
