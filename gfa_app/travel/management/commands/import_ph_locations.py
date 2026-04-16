import os
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from travel.models import Province, City

class Command(BaseCommand):
    help = 'Imports Philippine Provinces and Cities from the cloned SQL repository'

    def handle(self, *args, **options):
        # Use settings.BASE_DIR to find the project root
        sql_path = os.path.join(settings.BASE_DIR, 'tmp_ph_locations', 'philippine_provinces_and_cities.sql')
        
        if not os.path.exists(sql_path):
            # Fallback for local dev if BASE_DIR is gfa_app
            sql_path = os.path.join(os.path.dirname(settings.BASE_DIR), 'tmp_ph_locations', 'philippine_provinces_and_cities.sql')
        
        if not os.path.exists(sql_path):
            self.stdout.write(self.style.ERROR(f"SQL file not found at {sql_path}"))
            return

        with open(sql_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.stdout.write("Importing Provinces...")
        # 1. Parse Provinces
        # Pattern: (id, 'Name')
        prov_matches = re.findall(r"\((\d+),\s*'([^']+)'\)", content.split("INSERT INTO `provinces`")[1].split(";")[0])
        
        province_map = {} # SQL ID -> Model Instance
        for sql_id, name in prov_matches:
            province, created = Province.objects.get_or_create(name=name)
            province_map[sql_id] = province
            if created:
                self.stdout.write(f"  + Added Province: {name}")

        self.stdout.write(f"Total Provinces: {len(province_map)}")

        self.stdout.write("Importing Cities...")
        # 2. Parse Cities
        # Pattern: (id, 'Name', province_id, 'zipcode')
        city_section = content.split("INSERT INTO `cities`")[1].split(";")[0]
        # Regex for city rows: (\d+,\s*'[^']+',\s*\d+,\s*'[^']*')
        city_rows = re.findall(r"\((\d+),\s*'([^']+)',\s*(\d+),\s*'([^']*)'\)", city_section)
        
        cities_to_create = []
        existing_cities = set(City.objects.values_list('name', 'province_id'))
        
        for sql_id, name, prov_sql_id, zipcode in city_rows:
            province = province_map.get(prov_sql_id)
            if not province:
                continue
            
            # Simple deduplication check
            if (name, province.id) not in existing_cities:
                cities_to_create.append(City(
                    name=name,
                    province=province,
                    zipcode=zipcode if zipcode else None
                ))

        if cities_to_create:
            City.objects.bulk_create(cities_to_create)
            self.stdout.write(self.style.SUCCESS(f"Successfully imported {len(cities_to_create)} new cities."))
        else:
            self.stdout.write(self.style.WARNING("No new cities to import."))

        self.stdout.write(self.style.SUCCESS("Location synchronization complete."))
