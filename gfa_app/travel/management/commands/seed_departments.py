from django.core.management.base import BaseCommand
from travel.models import Department

class Command(BaseCommand):
    help = 'Seeds the Department table with the 31 requested offices'

    def handle(self, *args, **kwargs):
        departments = [
            ("Center For Integrative Development Studies", "CIDS"),
            ("Center For Women And Gender Studies", "CWGS"),
            ("Centre International de Formation des Autorités et Leaders", "CIFAL"),
            ("Executive House", "EH"),
            ("Information Technology Development Center", "ITDC"),
            ("Media and Public Relation", "MPRO"),
            ("Office of Admissions", "OAD"),
            ("Office of Alumni Relation", "OAR"),
            ("Office of Design and Planning Initiatives", "ODPI"),
            ("Office of International Linkages", "OIL"),
            ("Office of Sectoral Regents", "OSR"),
            ("Office of the President", "OP"),
            ("Office of the Secretary of the University", "OSU"),
            ("Office of the Vice President for Academic Affairs", "OVPAA"),
            ("Office of the Vice President for Administration", "OVPA"),
            ("Office of the Vice President for Development", "OVPD"),
            ("Office of the Vice President for Legal Affairs", "OVPLA"),
            ("Office of the Vice President for Planning and Finance", "OVPPF"),
            ("Office of the Vice President for Public Affairs", "OVPPA"),
            ("Office of the Vice President for Research and Innovation", "OVPRI"),
            ("Padayon Public Service Office", "PPSO"),
            ("Philippine Genome Center", "PGC"),
            ("Project Management Office", "PMO"),
            ("System Accounting Office", "SAO"),
            ("System Budget Office", "SBO"),
            ("System Cash Office", "SCO"),
            ("System Supply and Property Management Office", "SSPMO"),
            ("TVUP", "TVUP"),
            ("UP Press", "UP_PRESS"),
            ("UP Procurement Office", "UPPO"),
            ("UP Resilience Institute", "UPRI"),
        ]

        count = 0
        mother_units = ["OP", "OVPAA", "OVPA", "OVPD", "OVPLA", "OVPPF", "OVPPA", "OVPRI"]

        for name, code in departments:
            is_mother = code in mother_units
            obj, created = Department.objects.update_or_create(
                code=code,
                defaults={'name': name, 'is_mother_unit': is_mother}
            )
            if created:
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {count} new departments.'))
