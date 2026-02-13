from django.utils import timezone
from django.core.exceptions import PermissionDenied, ValidationError
from .models import AssetBatch, ApprovalLog, UserSignature

class WorkflowEngine:
    # State Constants
    ANTICIPATORY = 'ANTICIPATORY'
    AWAITING_DELIVERY = 'AWAITING_DELIVERY'
    DELIVERY_VALIDATION = 'DELIVERY_VALIDATION'
    FOR_INSPECTION = 'FOR_INSPECTION'
    FOR_SUPERVISOR_APPROVAL = 'FOR_SUPERVISOR_APPROVAL'
    FOR_CHIEF_PRE_APPROVAL = 'FOR_CHIEF_PRE_APPROVAL'
    FOR_AO_SIGNATURE = 'FOR_AO_SIGNATURE'
    FOR_CHIEF_FINAL_SIGNATURE = 'FOR_CHIEF_FINAL_SIGNATURE'
    PAR_RELEASED = 'PAR_RELEASED'
    REJECTED = 'REJECTED'

    # Role Constants (To be mapped to Django Groups)
    ROLE_AO = 'USER_AO'
    ROLE_ADMIN = 'SPMO_ADMIN'
    ROLE_INSPECTOR = 'INSPECTOR'
    ROLE_SUPERVISOR = 'SUPERVISOR'
    ROLE_CHIEF = 'CHIEF'

    # STRICT TRANSITION MAPPING
    # Current State -> { Allowed Target, Required Role, Description }
    TRANSITIONS = {
        ANTICIPATORY: {
            'target': AWAITING_DELIVERY,
            'role': ROLE_AO,
            'action': 'Submit for Delivery',
        },
        AWAITING_DELIVERY: {
            'target': DELIVERY_VALIDATION,
            'role': ROLE_ADMIN, # "Triggered by SPMO_ADMIN when physical delivery occurs"
            'action': 'Confirm Delivery',
        },
        DELIVERY_VALIDATION: {
            'target': FOR_INSPECTION,
            'role': ROLE_ADMIN,
            'action': 'Validate Documents',
        },
        FOR_INSPECTION: {
            'target': FOR_SUPERVISOR_APPROVAL,
            'role': ROLE_INSPECTOR,
            'action': 'Inspect and Approve',
        },
        FOR_SUPERVISOR_APPROVAL: {
            'target': FOR_CHIEF_PRE_APPROVAL,
            'role': ROLE_SUPERVISOR,
            'action': 'Supervisor Approval',
        },
        FOR_CHIEF_PRE_APPROVAL: {
            'target': FOR_AO_SIGNATURE,
            'role': ROLE_CHIEF,
            'action': 'Pre-Approve PAR Draft',
        },
        FOR_AO_SIGNATURE: {
            'target': FOR_CHIEF_FINAL_SIGNATURE,
            'role': ROLE_AO,
            'action': 'Sign PAR',
        },
        FOR_CHIEF_FINAL_SIGNATURE: {
            'target': PAR_RELEASED,
            'role': ROLE_CHIEF,
            'action': 'Finalize and Release',
        },
    }

    @staticmethod
    def transition(batch: AssetBatch, target_state: str, user):
        """
        Executes a state transition if valid.
        """
        current_state = batch.status
        
        # 0. Check if transition is valid for current state
        if current_state not in WorkflowEngine.TRANSITIONS:
             raise ValidationError(f"Current state {current_state} has no valid transitions.")
        
        transition_rule = WorkflowEngine.TRANSITIONS[current_state]
        
        # 1. Check Target State
        if target_state != transition_rule['target'] and target_state != 'REJECTED':
             raise ValidationError(f"Invalid transition from {current_state} to {target_state}. Expected {transition_rule['target']}.")

        # 2. Check User Role (Groups)
        required_role = transition_rule['role']
        if not user.groups.filter(name=required_role).exists() and not user.is_superuser:
            raise PermissionDenied(f"User {user.username} does not have the required role: {required_role}")

        # 3. Check Signature Requirement (if approving)
        if target_state != 'REJECTED': # Rejections might not need signatures? Let's assume strict for approvals.
            if not hasattr(user, 'signature') or not user.signature.signature_image:
                 raise ValidationError(f"User {user.username} does not have a registered signature. Please upload one in your profile.")

        # 4. Check Document Logic (Fail Conditions)
        WorkflowEngine.validate_requirements(batch, current_state)

        # 5. Execute Transition
        previous_state = batch.status
        batch.status = target_state
        batch.save()
        
        # 6. Log Approval
        ApprovalLog.objects.create(
            batch=batch,
            user=user,
            role=required_role,
            action=transition_rule['action'],
            timestamp=timezone.now(),
            ip_address=None, # TODO: Pass request to capture IP
            # Snapshot signature?
            signature_snapshot=user.signature.signature_image 
        )

        return batch

    @staticmethod
    def validate_requirements(batch, current_state):
        """
        Checks for required documents/fields before leaving a state.
        """
        if current_state == WorkflowEngine.ANTICIPATORY:
            if not batch.doc_1_file: # Assuming doc_1 is PO
                raise ValidationError("Purchase Order (PO) is required.")
            # Technical Specs?
        
        if current_state == WorkflowEngine.DELIVERY_VALIDATION:
            if not batch.doc_2_file: # Assuming doc_2 is DR/SI
                 raise ValidationError("Delivery Receipt / Sales Invoice is required.")
        
        # Add more validation as fields allow
        return True
