from django.utils import timezone
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import send_mail
from django.conf import settings
from .models import AssetBatch, InspectionRequest, AssetTransferRequest, Asset
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
        steps = None
        if transaction.current_step:
            steps = WorkflowStep.objects.filter(phase__workflow=transaction.current_step.phase.workflow).order_by('order')
        else:
            # System Fix: Fallback for finalized transactions whose active step was natively cleared
            from inventory.models import AssetBatch, AssetTransferRequest, InspectionRequest, AssetReturnRequest, AssetLossReport, PropertyClearanceRequest
            from workflow.models import WorkflowProcess
            process_code = None
            if isinstance(transaction, AssetBatch): process_code = 'BATCH_ACQUISITION'
            elif isinstance(transaction, AssetTransferRequest): process_code = 'TRANSFER'
            elif isinstance(transaction, InspectionRequest): process_code = 'INSPECTION'
            elif isinstance(transaction, AssetReturnRequest): process_code = 'RETURN'
            elif isinstance(transaction, AssetLossReport): process_code = 'LOSS_REPORT'
            elif isinstance(transaction, PropertyClearanceRequest): process_code = 'CLEARANCE'
            
            if process_code:
                process_obj = WorkflowProcess.objects.filter(code=process_code).first()
                if process_obj and process_obj.workflows.exists():
                    steps = process_obj.workflows.first().steps.all().order_by('order')

        if steps:
            logs = transaction.movement_logs.all() if hasattr(transaction, 'movement_logs') else []
            timeline = []
            reached_current = False
            
            for step in steps:
                is_current = getattr(transaction, 'current_step', None) and (transaction.current_step.id == step.id) and transaction.status != 'FINALIZED'

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
                # 1. Forward Move (Next Step)
                next_step = WorkflowStep.objects.filter(
                    phase__workflow=current_step.phase.workflow,
                    order__gt=current_step.order
                ).order_by('order').first()
                
                if next_step:
                    allowed_transitions.append({
                        'target': str(next_step.id),
                        'action': f"Advance to: {next_step.label}",
                        'css_class': 'btn-success',
                        'icon': 'fas fa-arrow-right'
                    })
                else: 
                    # If there's no next step, we are finalizing the workflow
                    allowed_transitions.append({
                        'target': 'FINALIZE',
                        'action': 'Finalize & Close Transaction',
                        'css_class': 'btn-primary',
                        'icon': 'fas fa-check-double'
                    })

                # 2. Backward Move (Return) - Only if not at Step 1
                prev_step = WorkflowStep.objects.filter(
                    phase__workflow=current_step.phase.workflow,
                    order__lt=current_step.order
                ).order_by('-order').first()

                if prev_step:
                    allowed_transitions.append({
                        'target': str(prev_step.id),
                        'action': f"Return to: {prev_step.label}",
                        'css_class': 'btn-warning',
                        'icon': 'fas fa-undo',
                        'is_reverse': True
                    })

                # 3. Terminal Rejection (Only for certain roles/steps)
                # Typically SPMO Officers can reject End-User requests
                if required_role and required_role.code in ['SPMO_AO', 'SPMO_SUPERVISOR', 'SPMO_CHIEF']:
                    allowed_transitions.append({
                        'target': 'REJECT',
                        'action': 'Reject Transaction',
                        'css_class': 'btn-danger',
                        'icon': 'fas fa-times-circle',
                        'is_reverse': True
                    })
        return allowed_transitions

    @staticmethod
    def _realize_assets(batch):
        """
        SOP Implementation: Converts BatchItems into individual Asset records.
        Executed upon Batch Finalization.
        """
        # 1. Prevent double realization
        if batch.generated_assets.exists():
            return
            
        items = batch.items.all()
        assets_created = []
        
        for item in items:
            # Create 'quantity' number of individual assets
            for i in range(item.quantity):
                asset = Asset.objects.create(
                    acquisition_batch=batch,
                    name=item.description[:255],
                    acquisition_cost=item.amount,
                    date_acquired=batch.created_at.date(),
                    department=batch.requesting_unit_obj, # Assuming there's a link or logic to set this
                    assigned_custodian=item.assigned_custodian,
                    # Default class/nature if not specified in batch (SOP refinement)
                    asset_class='OTHER',
                    asset_nature='OTHER',
                    status='SERVICEABLE'
                )
                assets_created.append(asset)
        
        return assets_created

    @staticmethod
    def transition(transaction, target_step_id_or_action, user, remarks='', **kwargs):
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
            action_verb = "Finalized"
        elif target_step_id_or_action == 'REJECT':
            next_step = None
            target_label = "REJECTED"
            action_verb = "Rejected"
        else:
            try:
                next_step = WorkflowStep.objects.get(id=int(target_step_id_or_action))
                target_label = next_step.label
                # Determine if it was a return or advance
                if next_step.order < current_step.order:
                    action_verb = "Returned to"
                else:
                    action_verb = "Advanced to"
            except (ValueError, TypeError, WorkflowStep.DoesNotExist):
                raise ValidationError("Invalid transition target ID.")
                
        # 3. Update Transaction States
        transaction.current_step = next_step
        if hasattr(transaction, 'status'):
            # Keep string field synced for fallback UI views
            if target_label == 'FINALIZED':
                transaction.status = 'PAR_RELEASED'
            elif target_label == 'REJECTED':
                transaction.status = 'REJECTED'
            else:
                 transaction.status = target_label
            
            # PHASE 7: SOP Asset Realization
            if isinstance(transaction, AssetBatch) and target_label == 'FINALIZED':
                WorkflowEngine._realize_assets(transaction)

        transaction.save()
        
        # 4. Generate the Comprehensive Audit Log
        role_label = active_persona.role.name if active_persona else 'Superuser'
        unit_label = active_persona.department.name if active_persona and active_persona.department else 'System/Admin'
        
        # Capture Signature Snapshot (Signature-Lock)
        sig_snapshot = None
        
        # HYBRID LOGIC:
        # 1. Check if a manual signature was provided in the request (Unit Admins / Custodians)
        manual_sig = kwargs.get('manual_signature')
        if manual_sig:
            sig_snapshot = manual_sig
        # 2. Fallback to Persona/Role-based reusable signature if the user has one (SSPMO)
        elif active_persona and active_persona.signature_image:
             from django.core.files.base import ContentFile
             sig_file = active_persona.signature_image
             sig_snapshot = ContentFile(sig_file.read(), name=f"sig_{user.username}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.png")
        # 3. Last fallback: User profile legacy signature (if any)
        elif hasattr(user, 'signature') and user.signature.signature_image:
             from django.core.files.base import ContentFile
             sig_file = user.signature.signature_image
             sig_snapshot = ContentFile(sig_file.read(), name=f"sig_{user.username}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.png")
        
        log_kwargs = {
            'user': user,
            'persona': active_persona,
            'role_name': role_label,
            'unit_name': unit_label,
            'status_label': target_label,
            'action_taken': f"{action_verb} {target_label}",
            'remarks': remarks,
            'signature_snapshot': sig_snapshot
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

        # 5. NEW: Trigger document generation AFTER the log entry is created
        # This ensures the final signature snapshot is available to the Generator
        if target_step_id_or_action == 'FINALIZE':
             if isinstance(transaction, AssetBatch):
                 if transaction.total_value >= 50000:
                     PARGenerator.finalize_par(transaction)
                 else:
                     ICSGenerator.finalize_ics(transaction)
             elif isinstance(transaction, AssetTransferRequest):
                 PTRGenerator.finalize_ptr(transaction)
        
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
