import os
import django
import sys

# Setup Path
sys.path.append(r'c:\Users\Aaron\spmo-suite - Copy\gfa_app')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from travel.models import TravelTrip, Settlement, AirlineCredit, CreditLog, Airport
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

def simulate():
    print("--- STARTING WORKFLOW SIMULATION ---")
    
    # 1. Setup
    groot = User.objects.get(username='grootadmin')
    mnl = Airport.objects.filter(iata_code='MNL').first()
    if not mnl:
        print("Seeding missing MNL airport...")
        mnl = Airport.objects.create(iata_code='MNL', city_name='Manila', name='Ninoy Aquino Intl', is_international=False)
    
    # 2. CREATE TRIP (Unit AO Stage)
    trip = TravelTrip.objects.create(
        full_name="SIMULATION TESTER",
        employee_id="SIM-123",
        email="sim@example.com",
        contact_number="09170000000",
        origin=mnl,
        destination_details="Cebu (CEB)",
        departure_date=timezone.now().date(),
        trip_type='ONEWAY',
        airline='PAL',
        seat_class='ECONOMY',
        baggage_type='PREMIUM',
        is_official=True,
        status='FOR_ADMIN', # Initial submitted state
        created_by=groot
    )
    print(f"Created Trip: ID={trip.id}, Status={trip.status}")

    # 3. ADMIN VERIFICATION (Ruby)
    trip.admin_verified = True
    trip.admin_verified_at = timezone.now()
    trip.status = 'FOR_SUPERVISOR'
    trip.save()
    print(f"Stage 1 OK: Status={trip.status}")

    # 4. SUPERVISOR VERIFICATION (Aaron)
    trip.supervisor_verified = True
    trip.supervisor_verified_at = timezone.now()
    trip.status = 'FOR_CHIEF'
    trip.save()
    print(f"Stage 2 OK: Status={trip.status}")

    # 5. CHIEF APPROVAL (Isagani)
    trip.chief_approved = True
    trip.chief_approved_at = timezone.now()
    trip.status = 'APPROVED'
    trip.save()
    print(f"Stage 3 OK: Status={trip.status}")

    # 6. TICKETING (Staff)
    trip.status = 'BOOKED'
    trip.booking_reference_no = "SIMPNR"
    trip.total_amount = Decimal('5500.00')
    trip.save()
    
    # Log the credit deduction
    credit, _ = AirlineCredit.objects.get_or_create(airline='PAL', defaults={'current_balance': 1000000, 'total_credit_limit': 1000000})
    credit.current_balance -= trip.total_amount
    credit.save()
    
    CreditLog.objects.create(
        airline='PAL',
        transaction_type='DEDUCT',
        amount=trip.total_amount,
        reference_no=f"GFA-{trip.id:06d}",
        remarks=f"Ticketing for SIM-123"
    )
    print(f"Ticketing OK: Status={trip.status}, Amount={trip.total_amount}")

    # 7. SETTLEMENT (Final)
    settlement = Settlement.objects.create(
        pnr_reference="SIMPNR",
        amount=trip.total_amount,
        settlement_date=timezone.now().date(),
        remarks="Simulation Settlement",
        processed_by=groot
    )
    
    # Mark trip as settled
    trip.status = 'SETTLED'
    trip.save()
    
    # Replenish credit
    credit.current_balance += trip.total_amount
    credit.save()
    
    CreditLog.objects.create(
        airline='PAL',
        transaction_type='SETTLE',
        amount=trip.total_amount,
        reference_no=f"GFA-{trip.id:06d}",
        remarks=f"Settlement for SIMPNR"
    )
    print(f"Workflow Complete: Final Status={trip.status}")
    print(f"Verification Trip ID: {trip.id}")

if __name__ == "__main__":
    simulate()
