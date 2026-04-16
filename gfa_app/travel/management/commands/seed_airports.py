from django.core.management.base import BaseCommand
from travel.models import Airport

AIRPORTS = [
    ('MNL', 'Ninoy Aquino International Airport', 'Manila', True),
    ('CEB', 'Mactan-Cebu International Airport', 'Cebu', True),
    ('DVO', 'Francisco Bangoy International Airport', 'Davao', True),
    ('CRK', 'Clark International Airport', 'Clark/Pampanga', True),
    ('ILO', 'Iloilo International Airport', 'Iloilo', True),
    ('KLO', 'Kalibo International Airport', 'Kalibo', True),
    ('PPS', 'Puerto Princesa International Airport', 'Puerto Princesa', True),
    ('LAO', 'Laoag International Airport', 'Laoag', True),
    ('BCD', 'Bacolod-Silay Airport', 'Bacolod', False),
    ('CGY', 'Laguindingan Airport', 'Cagayan de Oro', False),
    ('GES', 'General Santos International Airport', 'General Santos', True),
    ('TAC', 'Daniel Z. Romualdez Airport', 'Tacloban', False),
    ('MPH', 'Godofredo P. Ramos Airport', 'Caticlan/Boracay', False),
    ('USU', 'Francisco B. Reyes Airport', 'Coron/Busuanga', False),
    ('TAG', 'Bohol-Panglao International Airport', 'Tagbilaran', True),
    ('ZAM', 'Zamboanga International Airport', 'Zamboanga', True),
    ('BXU', 'Bancasi Airport', 'Butuan', False),
    ('DPL', 'Dipolog Airport', 'Dipolog', False),
    ('DGT', 'Sibulan Airport', 'Dumaguete', False),
    ('OZC', 'Labo Airport', 'Ozamiz', False),
    ('PAG', 'Pagadian Airport', 'Pagadian', False),
    ('CBO', 'Awang Airport', 'Cotabato', False),
    ('IAO', 'Sayak Airport', 'Siargao', False),
    ('ENI', 'El Nido Airport', 'El Nido', False),
    ('WNP', 'Naga Airport', 'Naga', False),
    ('TUG', 'Tuguegarao Airport', 'Tuguegarao', False),
    ('BSO', 'Basco Airport', 'Basco/Batanes', False),
    ('RXS', 'Roxas Airport', 'Roxas', False),
    ('CYP', 'Calbayog Airport', 'Calbayog', False),
    ('OMC', 'Ormoc Airport', 'Ormoc', False),
    ('SJI', 'San Jose Airport', 'San Jose/Mindoro', False),
    ('MBT', 'Moises R. Espinosa Airport', 'Masbate', False),
    ('CYZ', 'Cauayan Airport', 'Cauayan', False),
    ('SUG', 'Surigao Airport', 'Surigao', False),
    ('CGM', 'Camiguin Airport', 'Camiguin', False),
    ('CRM', 'Catarman Airport', 'Catarman', False),
    ('MRQ', 'Marinduque Airport', 'Marinduque', False),
    ('VRC', 'Virac Airport', 'Virac/Catanduanes', False),
    ('JOL', 'Jolo Airport', 'Jolo', False),
    ('CYU', 'Cuyo Airport', 'Cuyo', False),
]

class Command(BaseCommand):
    help = 'Seed the database with Philippine airports'

    def handle(self, *args, **options):
        created = 0
        for iata, name, city_name, is_intl in AIRPORTS:
            _, was_created = Airport.objects.get_or_create(
                iata_code=iata,
                defaults={'name': name, 'city_name': city_name, 'is_international': is_intl}
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Seeded {created} airports ({Airport.objects.count()} total)'))
