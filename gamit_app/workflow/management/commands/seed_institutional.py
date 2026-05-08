# =============================================================
# GAMIT Institutional Seeder v2 — Canonical 5-Process Edition
# =============================================================
# This is the SINGLE SOURCE OF TRUTH for all workflow data.
# Safe to re-run: uses get_or_create throughout.
# Also cleans up deprecated processes (ASSET_RETURN, ASSET_TRANSFER_CU).
# =============================================================

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from workflow.models import (
    Role, Persona, ActionProcess, Workflow, WorkflowPhase,
    WorkflowStep, SignatorySlot
)
from inventory.models import Department


class Command(BaseCommand):
    help = 'Seeds the canonical 5-process institutional data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-ghost-army', action='store_true',
            help='Skip Ghost Army persona creation (for DEV/PROD)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('  GAMIT Institutional Seeder v2'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        self._cleanup_deprecated()
        self._seed_roles()
        self._seed_blueprints()
        self._seed_signatory_slots()

        if not options['skip_ghost_army']:
            self._seed_departments_and_ghosts()
        else:
            self.stdout.write(self.style.WARNING('\n--- Skipping Ghost Army (--skip-ghost-army) ---'))

        self.stdout.write(self.style.SUCCESS('\n✅ Institutional Seeding Complete.'))

    # ====================================
    # PHASE 0: CLEANUP DEPRECATED
    # ====================================
    def _cleanup_deprecated(self):
        self.stdout.write('\n--- Phase 0: Cleanup Deprecated Processes ---')
        deprecated = ['ASSET_RETURN', 'ASSET_TRANSFER_CU']
        for code in deprecated:
            # Cascade: Steps → Phases → Workflow → ActionProcess
            ap = ActionProcess.objects.filter(code=code).first()
            if ap:
                workflows = Workflow.objects.filter(process=ap)
                for wf in workflows:
                    steps_deleted = WorkflowStep.objects.filter(phase__workflow=wf).count()
                    phases_deleted = WorkflowPhase.objects.filter(workflow=wf).count()
                    wf.delete()  # Cascades to phases and steps
                    self.stdout.write(f"  [Removed] {code}: {phases_deleted} phases, {steps_deleted} steps")
                ap.delete()
                self.stdout.write(f"  [Removed] ActionProcess: {code}")
            else:
                self.stdout.write(f"  [Skip] {code} not found")

    # ====================================
    # PHASE 1: ROLES
    # ====================================
    def _seed_roles(self):
        self.stdout.write('\n--- Phase 1: Roles ---')
        roles_data = [
            # OPERATOR roles (SPMO Core Staff)
            ('SPMO_CHIEF',            'Director / SPMO Chief',        'OPERATOR'),
            ('SPMO_ADMIN_SUPERVISOR',  'SPMO Admin Supervisor',        'OPERATOR'),
            ('SPMO_SUPERVISOR',        'SPMO Inventory Supervisor',    'OPERATOR'),
            ('INSPECTION_OFFICER',     'Inspection Officer',           'OPERATOR'),
            ('SPMO_AO',               'SPMO Inventory Officer',       'OPERATOR'),
            ('SPMO_CLERK',            'SPMO Inventory Clerk',         'OPERATOR'),
            # CLIENT roles (Unit/Department Staff)
            ('UNIT_HEAD',             'Unit / Department Head',       'CLIENT'),
            ('UNIT_AO',              'Unit Accountable Officer',     'CLIENT'),
        ]
        for code, name, category in roles_data:
            role, created = Role.objects.get_or_create(
                code=code, defaults={'name': name, 'category': category}
            )
            if not created:
                role.name = name
                role.category = category
                role.save()
            status = 'NEW' if created else 'OK'
            self.stdout.write(f"  [{status}] {code} [{category}]")

    # ====================================
    # PHASE 2: WORKFLOW BLUEPRINTS
    # ====================================
    def _seed_blueprints(self):
        self.stdout.write('\n--- Phase 2: Workflow Blueprints (5 Canonical Processes) ---')

        # First, clean up any duplicate phases/steps from old seeders
        self._deduplicate_existing()

        blueprints = self._get_blueprint_data()

        for proc_code, bp in blueprints.items():
            process, _ = ActionProcess.objects.get_or_create(
                code=proc_code,
                defaults={'name': bp['process_name'], 'order': bp['order']}
            )
            # Update name/order if already exists
            process.name = bp['process_name']
            process.order = bp['order']
            process.save()

            workflow, _ = Workflow.objects.get_or_create(
                process=process,
                defaults={'name': bp['workflow_name']}
            )

            for phase_name, phase_order, steps in bp['phases']:
                phase, _ = WorkflowPhase.objects.get_or_create(
                    workflow=workflow, name=phase_name,
                    defaults={'order': phase_order}
                )
                for step_label, step_order, role_code in steps:
                    role = Role.objects.get(code=role_code) if role_code else None
                    step, created = WorkflowStep.objects.get_or_create(
                        phase=phase, label=step_label,
                        defaults={'order': step_order, 'required_persona_role': role}
                    )
                    if not created and role:
                        step.required_persona_role = role
                        step.order = step_order
                        step.save()

            total_steps = WorkflowStep.objects.filter(phase__workflow=workflow).count()
            total_phases = WorkflowPhase.objects.filter(workflow=workflow).count()
            self.stdout.write(f"  [{proc_code}] {bp['workflow_name']} — {total_phases} phases, {total_steps} steps")

    def _deduplicate_existing(self):
        """Remove duplicate phases created by running old + new seeders."""
        for wf in Workflow.objects.all():
            seen_names = {}
            for phase in WorkflowPhase.objects.filter(workflow=wf).order_by('id'):
                if phase.name in seen_names:
                    # This is a duplicate — delete it and its steps
                    count = phase.steps.count()
                    phase.delete()
                    self.stdout.write(self.style.WARNING(
                        f"  [Dedup] Removed duplicate phase '{phase.name}' ({count} steps)"
                    ))
                else:
                    seen_names[phase.name] = phase

    def _get_blueprint_data(self):
        """
        Returns the canonical blueprint definitions.
        Format: (step_label, step_order, required_role_code)
        """
        return {
            # -----------------------------------------------
            # 1. BATCH ACQUISITION (11 steps, 5 phases)
            # -----------------------------------------------
            'BATCH_ACQUISITION': {
                'process_name': 'Batch Acquisition / Procurement',
                'workflow_name': 'Batch Acquisition Workflow',
                'order': 1,
                'phases': [
                    ('Initiation', 10, [
                        ('Draft / Anticipatory',         10, 'UNIT_AO'),
                        ('For Unit Chief Approval',      20, 'UNIT_HEAD'),
                    ]),
                    ('SPMO Processing', 20, [
                        ('Verify Completeness (SPMO)',   10, 'SPMO_AO'),
                        ('For SPMO AO Signature',        20, 'SPMO_AO'),
                        ('Initiate Inspection',          30, 'INSPECTION_OFFICER'),
                    ]),
                    ('Inspection', 30, [
                        ('For Inspection Signature',     10, 'INSPECTION_OFFICER'),
                        ('Release / Save IAR',           20, 'INSPECTION_OFFICER'),
                    ]),
                    ('Approval', 40, [
                        ('Verify Completeness (Supv)',   10, 'SPMO_SUPERVISOR'),
                        ('For Supervisor Signature',     20, 'SPMO_SUPERVISOR'),
                        ('For Chief Final Approval',     30, 'SPMO_CHIEF'),
                    ]),
                    ('Completion', 50, [
                        ('Awaiting Unit Acceptance',     10, 'UNIT_AO'),
                    ]),
                ],
            },

            # -----------------------------------------------
            # 2. ASSET TRANSFER (8 steps, 4 phases)
            # -----------------------------------------------
            'ASSET_TRANSFER': {
                'process_name': 'Asset Transfer & Accountability',
                'workflow_name': 'Asset Transfer Workflow',
                'order': 2,
                'phases': [
                    ('Initiation', 10, [
                        ('Transfer Request',            10, 'UNIT_AO'),
                        ('For Unit Chief Approval',     20, 'UNIT_HEAD'),
                    ]),
                    ('SPMO Processing', 20, [
                        ('For SPMO AO Signature',       10, 'SPMO_AO'),
                        ('Verify Completeness (Supv)',  20, 'SPMO_SUPERVISOR'),
                        ('For Supervisor Signature',    30, 'SPMO_SUPERVISOR'),
                    ]),
                    ('Approval', 30, [
                        ('For Chief Final Signature',   10, 'SPMO_CHIEF'),
                    ]),
                    ('Completion', 40, [
                        ('Update Values/Confirm',       10, 'SPMO_AO'),
                        ('For Unit AO Receipt',         20, 'UNIT_AO'),
                    ]),
                ],
            },

            # -----------------------------------------------
            # 3. PRE-REPAIR INSPECTION (3 steps, 1 phase)
            # -----------------------------------------------
            'ASSET_INSPECT': {
                'process_name': 'Pre-Repair Inspection',
                'workflow_name': 'Pre-Repair Inspection Workflow',
                'order': 3,
                'phases': [
                    ('Request & Execution', 10, [
                        ('Inspection Request',          10, 'UNIT_AO'),
                        ('Conduct Inspection',          20, 'INSPECTION_OFFICER'),
                        ('Release Inspection Report',   30, 'INSPECTION_OFFICER'),
                    ]),
                ],
            },

            # -----------------------------------------------
            # 4. REPORT LOSS / DAMAGE (5 steps, 2 phases)
            # -----------------------------------------------
            'ASSET_LOSS': {
                'process_name': 'Report of Loss / Damage',
                'workflow_name': 'Loss & Damage Report Workflow',
                'order': 4,
                'phases': [
                    ('Initiation', 10, [
                        ('Request Loss Report',         10, 'UNIT_AO'),
                        ('Unit Head Approval',          20, 'UNIT_HEAD'),
                        ('For Unit AO Signature',       30, 'UNIT_AO'),
                    ]),
                    ('SPMO Approval', 20, [
                        ('For Admin Supervisor Signature', 10, 'SPMO_ADMIN_SUPERVISOR'),
                        ('For Chief Approval',          20, 'SPMO_CHIEF'),
                    ]),
                ],
            },

            # -----------------------------------------------
            # 5. PROPERTY CLEARANCE (4 steps, 2 phases)
            # -----------------------------------------------
            'ASSET_CLEARANCE': {
                'process_name': 'Personnel Property Clearance',
                'workflow_name': 'Property Clearance Workflow',
                'order': 5,
                'phases': [
                    ('Initiation', 10, [
                        ('Unit Head Clearance',         10, 'UNIT_HEAD'),
                        ('SPMO Verification',           20, 'SPMO_AO'),
                    ]),
                    ('SPMO Approval', 20, [
                        ('Admin Supervisor Signature',  10, 'SPMO_ADMIN_SUPERVISOR'),
                        ('Chief Final Clearance',       20, 'SPMO_CHIEF'),
                    ]),
                ],
            },
        }

    # ====================================
    # PHASE 3: SIGNATORY SLOTS
    # ====================================
    def _seed_signatory_slots(self):
        self.stdout.write('\n--- Phase 3: Signatory Slots ---')
        slots = [
            # (process_code, step_label, role_code, slot_label, rank)
            ('BATCH_ACQUISITION', 'Verify Completeness (SPMO)',  'SPMO_AO',           'Prepared By',  1),
            ('BATCH_ACQUISITION', 'Release / Save IAR',          'INSPECTION_OFFICER', 'Inspected By', 2),
            ('BATCH_ACQUISITION', 'Verify Completeness (Supv)',  'SPMO_SUPERVISOR',    'Reviewed By',  3),
            ('BATCH_ACQUISITION', 'For Chief Final Approval',    'SPMO_CHIEF',         'Issued By',    4),
            ('BATCH_ACQUISITION', 'Awaiting Unit Acceptance',    'UNIT_HEAD',          'Received By',  5),
        ]
        for proc_code, step_label, role_code, slot_label, rank in slots:
            step = WorkflowStep.objects.filter(
                label=step_label,
                phase__workflow__process__code=proc_code
            ).first()
            if step:
                role = Role.objects.get(code=role_code)
                _, created = SignatorySlot.objects.get_or_create(
                    step=step, role=role, label=slot_label, rank=rank
                )
                status = 'NEW' if created else 'OK'
                self.stdout.write(f"  [{status}] {slot_label} → {step_label}")
            else:
                self.stdout.write(self.style.WARNING(
                    f"  [MISS] Step '{step_label}' not found for {proc_code}"
                ))

    # ====================================
    # PHASE 4: DEPARTMENTS & GHOST ARMY
    # ====================================
    def _seed_departments_and_ghosts(self):
        self.stdout.write('\n--- Phase 4: Departments & Ghost Army ---')
        dept_names = [
            "Office of the President", "Office of the Vice President",
            "SPMO", "HRDO", "Accounting Office",
            "Cashier's Office", "Budget Office", "Supply Office",
            "Building Services", "Security Division",
            "University Health Service", "University Library",
            "College of Arts & Sciences", "College of Engineering",
            "College of Education", "College of Law",
            "College of Medicine", "College of Nursing",
            "College of Pharmacy", "College of Public Health",
            "College of Social Work", "School of Statistics",
            "Institute of Biology", "Institute of Chemistry",
            "Institute of Physics", "Institute of Mathematics",
            "National Institute of Geological Sciences",
            "Marine Science Institute", "Computer Science",
            "Electrical Engineering", "Mechanical Engineering",
            "Civil Engineering"
        ]

        ghost_user = User.objects.filter(is_superuser=True).first()
        if not ghost_user:
            self.stdout.write(self.style.ERROR("No superuser found."))
            return

        for d_name in dept_names:
            dept, _ = Department.objects.get_or_create(name=d_name)
            Persona.objects.get_or_create(
                user=ghost_user, department=dept,
                role=Role.objects.get(code='UNIT_HEAD'),
                defaults={'position_title': f'Head, {d_name}'}
            )
            Persona.objects.get_or_create(
                user=ghost_user, department=dept,
                role=Role.objects.get(code='UNIT_AO'),
                defaults={'position_title': f'Accountable Officer, {d_name}'}
            )
        self.stdout.write(self.style.SUCCESS(
            f"  [Ghost Army] {len(dept_names)} departments × 2 roles = {len(dept_names)*2} personas"
        ))
