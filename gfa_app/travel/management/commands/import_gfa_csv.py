import csv
import re
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date, parse_time
from travel.models import BookingRequest, Department

# Fuzzy map for airline normalization
AIRLINE_MAP = {
    'philippine airlines': 'PAL', 'pal': 'PAL', 'pr': 'PAL',
    'cebu pacific': 'CEB', 'cebupac': 'CEB', 'ceb': 'CEB', '5j': 'CEB',
}

SEAT_MAP = {
    'economy': 'ECONOMY', 'business': 'BUSINESS', 'business class': 'BUSINESS',
    'premium': 'PREMIUM', 'first class': 'PREMIUM', 'premium / first class': 'PREMIUM',
}

TRIP_MAP = {
    'one-way': 'ONE_WAY', 'one way': 'ONE_WAY',
    'round-trip': 'ROUND_TRIP', 'round trip': 'ROUND_TRIP', 'roundtrip': 'ROUND_TRIP',
    'multi-city': 'MULTI_CITY', 'multi city': 'MULTI_CITY',
}

BAGGAGE_MAP = {
    'hand-carry only': 'HAND_CARRY', 'hand carry': 'HAND_CARRY', 'hand-carry': 'HAND_CARRY',
    'additional check-in baggage': 'CHECK_IN', 'check-in': 'CHECK_IN', 'check in': 'CHECK_IN',
}

STATUS_MAP = {
    'done': 'BOOKED', 'booked': 'BOOKED', 'confirmed': 'BOOKED',
    'pending': 'PENDING', 'approved': 'APPROVED', 'cancelled': 'CANCELLED',
    'draft': 'DRAFT', 'returned': 'RETURNED',
}


def parse_flexible_date(val):
    """Parse dates in multiple formats: MM/DD/YYYY, YYYY-MM-DD, M/D/YYYY, etc."""
    if not val or not val.strip():
        return None
    val = val.strip()
    for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%m/%d/%y', '%B %d, %Y', '%b %d, %Y', '%d/%m/%Y'):
        try:
            return datetime.strptime(val, fmt).date()
        except ValueError:
            continue
    return None


def parse_flexible_time(val):
    """Parse times in multiple formats: HH:MM AM/PM, HH:MM, etc."""
    if not val or not val.strip():
        return None
    val = val.strip()
    for fmt in ('%I:%M %p', '%H:%M', '%I:%M%p', '%H:%M:%S'):
        try:
            return datetime.strptime(val, fmt).time()
        except ValueError:
            continue
    return None


def fuzzy_department(name, dept_cache):
    """Try to match a department by code or substring of name."""
    if not name or not name.strip():
        return None
    name = name.strip()
    # Exact code match
    if name.upper() in dept_cache:
        return dept_cache[name.upper()]
    # Try extracting code from parentheses: "Office of X (OVPAA)" -> OVPAA
    m = re.search(r'\(([^)]+)\)', name)
    if m and m.group(1).upper() in dept_cache:
        return dept_cache[m.group(1).upper()]
    # Substring match on name
    name_lower = name.lower()
    for code, dept in dept_cache.items():
        if name_lower in dept.name.lower() or dept.name.lower() in name_lower:
            return dept
    return None


class Command(BaseCommand):
    help = 'Import legacy GFA Google Form CSV into BookingRequest'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Path to the CSV file')
        parser.add_argument('--dry-run', action='store_true', help='Preview without saving')

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        dry_run = options.get('dry_run', False)

        # Build department cache: {CODE: Department}
        dept_cache = {d.code.upper(): d for d in Department.objects.all()}
        # Also index by name for fuzzy matching
        
        created = 0
        skipped = 0
        errors = []

        with open(csv_path, encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=2):  # Row 2 = first data row
                try:
                    # --- Required Field Parsing ---
                    full_name = (row.get('Official Name of Traveler(s)  (First, Middle, Last)') or '').strip()
                    if not full_name:
                        skipped += 1
                        continue

                    # Airline
                    airline_raw = (row.get('Airline Preference') or '').strip().lower()
                    airline = AIRLINE_MAP.get(airline_raw, 'PAL')

                    # Status
                    status_raw = (row.get('STATUS') or 'DRAFT').strip().lower()
                    status = STATUS_MAP.get(status_raw, 'DRAFT')

                    # Departments
                    unit_office = fuzzy_department(row.get('Unit Office', ''), dept_cache)
                    mother_unit = fuzzy_department(row.get('Mother Unit', ''), dept_cache)

                    if not unit_office or not mother_unit:
                        # Fallback: use first available department
                        fallback = Department.objects.first()
                        unit_office = unit_office or fallback
                        mother_unit = mother_unit or fallback
                        if not dry_run:
                            errors.append(f'Row {i}: Used fallback dept for "{row.get("Unit Office","")}" / "{row.get("Mother Unit","")}"')

                    # Dates
                    dep_date = parse_flexible_date(row.get('Departure Date'))
                    ret_date = parse_flexible_date(row.get('Return Date'))
                    birthday = parse_flexible_date(row.get('Birthday'))
                    approval_date = parse_flexible_date(row.get('Date of Approval'))

                    if not dep_date:
                        errors.append(f'Row {i}: No departure date, skipping')
                        skipped += 1
                        continue

                    # Times (use col 7/8 first, fallback to 30/31)
                    dep_time = parse_flexible_time(row.get('Specific Time (Departure)'))
                    ret_time = parse_flexible_time(row.get('Specific Time (Return Time)'))

                    # Trip Type / Seat / Baggage
                    trip_raw = (row.get('Trip Type') or 'round-trip').strip().lower()
                    trip_type = TRIP_MAP.get(trip_raw, 'ROUND_TRIP')

                    seat_raw = (row.get('Seat Class') or 'economy').strip().lower()
                    seat_class = SEAT_MAP.get(seat_raw, 'ECONOMY')

                    bag_raw = (row.get('Baggage Type') or 'hand-carry only').strip().lower()
                    baggage_type = BAGGAGE_MAP.get(bag_raw, 'HAND_CARRY')

                    # Boolean fields
                    is_official = 'yes' in (row.get('Is this Travel Official and Approved?') or '').lower()
                    avail_insurance = 'yes' in (row.get('Would you like to avail of travel insurance for this trip?') or '').lower()

                    if dry_run:
                        self.stdout.write(f'  [DRY] Row {i}: {full_name} -> {row.get("Destination Details","")} ({airline}, {status})')
                        created += 1
                        continue

                    BookingRequest.objects.create(
                        full_name=full_name,
                        email=row.get('Email Address', '') or 'noemail@up.edu.ph',
                        employee_id=row.get('Employee ID', '') or 'N/A',
                        unit_office=unit_office,
                        mother_unit=mother_unit,
                        birthday=birthday or dep_date,  # fallback
                        designation=row.get('Designation', '') or 'N/A',
                        up_mail=row.get('UP Mail', '') or 'nomail@up.edu.ph',
                        contact_number=row.get('Contact Phone Number', '') or 'N/A',
                        admin_officer=row.get('Admin Officer (requesting staff)', '') or 'N/A',
                        purpose=row.get('Purpose of Travel', '') or 'Legacy GFA Import',
                        trip_type=trip_type,
                        origin='Manila',
                        destination_details=row.get('Destination Details', '') or 'Unknown',
                        departure_date=dep_date,
                        departure_time=dep_time or datetime.strptime('08:00', '%H:%M').time(),
                        return_date=ret_date,
                        return_time=ret_time,
                        is_official=is_official,
                        airline=airline,
                        seat_class=seat_class,
                        avail_insurance=avail_insurance,
                        baggage_type=baggage_type,
                        special_requests=row.get('Special Requests', ''),
                        supervisor_name=row.get("Immediate Supervisor's Name", '') or 'N/A',
                        supervisor_email=row.get("Supervisor's Email", '') or 'noemail@up.edu.ph',
                        approval_date=approval_date or dep_date,
                        remarks=row.get('Remarks', ''),
                        agreed_to_policy=True,
                        status=status,
                    )
                    created += 1

                except Exception as e:
                    import traceback
                    errors.append(f'Row {i}: {type(e).__name__}: {e}')
                    if len(errors) <= 3:
                        traceback.print_exc()
                    skipped += 1

        self.stdout.write(self.style.SUCCESS(f'\nImport complete: {created} created, {skipped} skipped'))
        if errors:
            self.stdout.write(self.style.WARNING(f'{len(errors)} warnings:'))
            for e in errors[:20]:
                self.stdout.write(f'  > {e}')
            if len(errors) > 20:
                self.stdout.write(f'  ... and {len(errors)-20} more')
