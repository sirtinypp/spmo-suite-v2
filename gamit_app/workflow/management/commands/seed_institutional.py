from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from workflow.models import Role, Persona, ActionProcess, Workflow, WorkflowPhase, WorkflowStep, SignatorySlot
from inventory.models import Department

class Command(BaseCommand):
    help = 'Seeds institutional data (Blueprints, Roles, Ghost Army Personas, and Signatory Slots)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Institutional Seeding...'))

        # ====================================
        # 0. WORKFLOW BLUEPRINTS
        # ====================================
        self.stdout.write('\n--- Phase 0: Workflow Blueprints ---')

        # Action Processes (Top-Level Categories)
        processes = [
            ('BATCH_ACQUISITION', 'Batch Acquisition / Procurement', 1),
            ('ASSET_TRANSFER', 'Asset Transfer (Unit to Unit)', 2),
            ('ASSET_TRANSFER_CU', 'Asset Transfer (Inter-CU)', 3),
            ('ASSET_INSPECT', 'Inspection (Repair & Maintenance)', 4),
            ('ASSET_RETURN', 'Asset Return', 5),
            ('ASSET_LOSS', 'Asset Loss Report', 6),
            ('ASSET_CLEARANCE', 'Personnel Property Clearance', 7),
        ]
        for code, name, order in processes:
            ActionProcess.objects.get_or_create(code=code, defaults={'name': name, 'order': order})
            self.stdout.write(f"  [Process] {code}")

        # Blueprint: Each process gets one Workflow with phases and steps
        # Structure: (process_code, workflow_name, phases_with_steps)
        blueprints = {
            'BATCH_ACQUISITION': {
                'workflow': 'Batch Acquisition Workflow',
                'phases': [
                    ('Initiation', 10, [
                        ('Draft / Anticipatory', 10),
                        ('For Unit Chief Approval', 20),
                    ]),
                    ('SPMO Processing', 20, [
                        ('Verify Completeness (SPMO)', 10),
                        ('For SPMO AO Signature', 20),
                        ('Initiate Inspection', 30),
                    ]),
                    ('Inspection', 30, [
                        ('For Inspection Signature', 10),
                        ('Release / Save IAR', 20),
                    ]),
                    ('Approval', 40, [
                        ('Verify Completeness (Supv)', 10),
                        ('For Supervisor Signature', 20),
                        ('For Chief Final Approval', 30),
                    ]),
                    ('Completion', 50, [
                        ('Awaiting Unit Acceptance', 10),
                    ]),
                ],
            },
            'ASSET_TRANSFER': {
                'workflow': 'Asset Transfer Workflow',
                'phases': [
                    ('Initiation', 10, [
                        ('Transfer Request', 10),
                        ('For Unit Chief Approval', 20),
                    ]),
                    ('SPMO Processing', 20, [
                        ('For SPMO AO Signature', 10),
                        ('Verify Completeness (Supv)', 20),
                        ('For Supervisor Signature', 30),
                    ]),
                    ('Approval & Completion', 30, [
                        ('For Chief Final Signature', 10),
                        ('Update Values/Confirm', 20),
                        ('For Unit AO Receipt', 30),
                    ]),
                ],
            },
            'ASSET_TRANSFER_CU': {
                'workflow': 'Inter-CU Transfer Workflow',
                'phases': [
                    ('Initiation', 10, [
                        ('Transfer Request', 10),
                        ('For Unit Chief Approval', 20),
                    ]),
                    ('SPMO Processing', 20, [
                        ('For SPMO AO Signature', 10),
                        ('Verify Completeness (Supv)', 20),
                        ('For Supervisor Signature', 30),
                    ]),
                    ('Approval & Completion', 30, [
                        ('For Chief Final Signature', 10),
                        ('For VP Approval', 20),
                        ('Update Values/Confirm', 30),
                        ('For Unit AO Receipt', 40),
                    ]),
                ],
            },
            'ASSET_INSPECT': {
                'workflow': 'Inspection Workflow',
                'phases': [
                    ('Request & Execution', 10, [
                        ('Inspection Request', 10),
                        ('Conduct Inspection', 20),
                        ('Release Inspection Report', 30),
                    ]),
                ],
            },
            'ASSET_RETURN': {
                'workflow': 'Asset Return Workflow',
                'phases': [
                    ('Initiation', 10, [
                        ('Request Return', 10),
                        ('Unit Head Approval', 20),
                        ('For Unit AO Signature', 30),
                    ]),
                    ('SPMO Approval', 20, [
                        ('For Supervisor Signature', 10),
                        ('For Chief Approval', 20),
                    ]),
                ],
            },
            'ASSET_LOSS': {
                'workflow': 'Asset Loss Report Workflow',
                'phases': [
                    ('Initiation', 10, [
                        ('Request Loss Report', 10),
                        ('Unit Head Approval', 20),
                        ('For Unit AO Signature', 30),
                    ]),
                    ('SPMO Approval', 20, [
                        ('For Admin Supervisor Signature', 10),
                        ('For Chief Approval', 20),
                    ]),
                ],
            },
            'ASSET_CLEARANCE': {
                'workflow': 'Property Clearance Workflow',
                'phases': [
                    ('Initiation', 10, [
                        ('Unit Head Clearance', 10),
                        ('SPMO Verification', 20),
                    ]),
                    ('SPMO Approval', 20, [
                        ('Admin Supervisor Signature', 10),
                        ('Chief Final Clearance', 20),
                    ]),
                ],
            },
        }

        for proc_code, bp_data in blueprints.items():
            process = ActionProcess.objects.get(code=proc_code)
            workflow, _ = Workflow.objects.get_or_create(
                process=process, defaults={'name': bp_data['workflow']}
            )
            for phase_name, phase_order, steps in bp_data['phases']:
                phase, _ = WorkflowPhase.objects.get_or_create(
                    workflow=workflow, name=phase_name, defaults={'order': phase_order}
                )
                for step_label, step_order in steps:
                    WorkflowStep.objects.get_or_create(
                        phase=phase, label=step_label, defaults={'order': step_order}
                    )
            self.stdout.write(f"  [Blueprint] {proc_code}: {bp_data['workflow']}")

        # ====================================
        # 1. ROLES WITH CATEGORIES
        # ====================================
        self.stdout.write('\n--- Phase 1: Roles ---')
        roles_data = [
            ('SPMO_CHIEF', 'Director / SPMO Chief', 'OPERATOR'),
            ('SPMO_ADMIN_SUPERVISOR', 'SPMO Admin Supervisor', 'OPERATOR'),
            ('SPMO_SUPERVISOR', 'SPMO Inventory Supervisor', 'OPERATOR'),
            ('INSPECTION_OFFICER', 'Inspection Officer', 'OPERATOR'),
            ('SPMO_AO', 'SPMO Inventory Officer', 'OPERATOR'),
            ('SPMO_CLERK', 'SPMO Inventory Clerk', 'OPERATOR'),
            ('UNIT_HEAD', 'Unit / Department Head', 'CLIENT'),
            ('UNIT_AO', 'Unit Accountable Officer', 'CLIENT'),
        ]

        for code, name, category in roles_data:
            role, created = Role.objects.get_or_create(code=code, defaults={'name': name, 'category': category})
            if not created:
                role.category = category
                role.save()
            self.stdout.write(f"  [Role] {code} - {category}")

        # ====================================
        # 2. DEPARTMENTS & GHOST ARMY
        # ====================================
        self.stdout.write('\n--- Phase 2: Ghost Army ---')
        dept_names = [
            "Office of the President", "Office of the Vice President", "SPMO", "HRDO", "Accounting Office",
            "Cashier's Office", "Budget Office", "Supply Office", "Building Services", "Security Division",
            "University Health Service", "University Library", "College of Arts & Sciences", "College of Engineering",
            "College of Education", "College of Law", "College of Medicine", "College of Nursing",
            "College of Pharmacy", "College of Public Health", "College of Social Work", "School of Statistics",
            "Institute of Biology", "Institute of Chemistry", "Institute of Physics", "Institute of Mathematics",
            "National Institute of Geological Sciences", "Marine Science Institute", "Computer Science",
            "Electrical Engineering", "Mechanical Engineering", "Civil Engineering"
        ]

        ghost_user = User.objects.filter(is_superuser=True).first()
        if not ghost_user:
            self.stdout.write(self.style.ERROR("No superuser found. Create one first."))
            return

        for d_name in dept_names:
            dept, _ = Department.objects.get_or_create(name=d_name)
            Persona.objects.get_or_create(
                user=ghost_user, department=dept, role=Role.objects.get(code='UNIT_HEAD'),
                defaults={'position_title': f'Head, {d_name}'}
            )
            Persona.objects.get_or_create(
                user=ghost_user, department=dept, role=Role.objects.get(code='UNIT_AO'),
                defaults={'position_title': f'Accountable Officer, {d_name}'}
            )
        self.stdout.write(self.style.SUCCESS(f"  [Ghost Army] 64 Personas across {len(dept_names)} departments."))

        # ====================================
        # 3. SIGNATORY SLOTS (Batch Acquisition)
        # ====================================
        self.stdout.write('\n--- Phase 3: Signatory Slots ---')
        slots_to_add = [
            ('Verify Completeness (SPMO)', 'SPMO_AO', 'Prepared By', 1),
            ('Release / Save IAR', 'INSPECTION_OFFICER', 'Inspected By', 2),
            ('Verify Completeness (Supv)', 'SPMO_SUPERVISOR', 'Reviewed By', 3),
            ('For Chief Final Approval', 'SPMO_CHIEF', 'Issued By', 4),
            ('Awaiting Unit Acceptance', 'UNIT_HEAD', 'Received By', 5),
        ]

        for step_label, role_code, slot_label, rank in slots_to_add:
            step = WorkflowStep.objects.filter(label=step_label, phase__workflow__process__code='BATCH_ACQUISITION').first()
            if step:
                role = Role.objects.get(code=role_code)
                SignatorySlot.objects.get_or_create(step=step, role=role, label=slot_label, rank=rank)
                self.stdout.write(f"  [Slot] Wired: {slot_label} -> {step_label}")
            else:
                self.stdout.write(self.style.WARNING(f"  [Slot] Step [{step_label}] not found. Skipping."))

        self.stdout.write(self.style.SUCCESS('\nInstitutional Seeding Complete.'))
