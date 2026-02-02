from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from supplies.models import Category, Product

class Command(BaseCommand):
    help = 'Advanced Deduplication: Merges complex variations and generates descriptions.'

    def handle(self, *args, **kwargs):
        self.stdout.write("--- Starting Advanced Category Cleanup ---")
        
        # 1. HARDCODED MERGES (The heavy lifters)
        # Target Name : [List of substrings/variations to merge into Target]
        merge_map = {
            "Software": [
                "Software (Note: Please Indicate Price Of Items)",
                "Software (Note: Please Indicate Price Of Items"
            ],
            "Measuring and Observing and Testing Equipment": [
                "Measuring And Observing And Testing",
                "Measuring And Observing And Testing Equipment Of Items)",
                "Measuring And Observing And Testing Equipment" # Ensure target case match
            ],
            "Information and Communication Technology (ICT) Equipment and Devices and Accessories": [
                "Information And Communication Technology (Ict) Equipment And Devices And Accessories",
                "Information And Communication Technology"
            ],
            "Office Equipment and Accessories and Supplies": [
                "Office Equipment And Accessories And Supplies",
                "Office Equipment And Accessories And Supplies (Consumables)"
            ]
        }

        for target_name, variations in merge_map.items():
            self.complex_merge(target_name, variations)

        # 2. "AND" vs "&" Normalization (Standardize on "and")
        # Strategy: Find any category with "&", check if "and" version exists.
        # If yes, merge. If no, rename.
        self.normalize_ampersands()

        # 3. Description Generation
        self.generate_descriptions()

        self.stdout.write(self.style.SUCCESS("\n--- Advanced Cleanup Complete ---"))

    def complex_merge(self, target_name, variations):
        # Ensure Target Exists
        target, created = Category.objects.get_or_create(name=target_name)
        if created:
            self.stdout.write(f"Created Target: '{target_name}'")
        else:
            self.stdout.write(f"Using Target: '{target_name}' (ID {target.id})")

        # Find and Merge Variations
        for var in variations:
            if var == target_name: continue
            
            # Find categories matching this variation (exact or close)
            # We use 'name__iexact' to catch case differences too
            to_merge = Category.objects.filter(name__iexact=var).exclude(id=target.id)
            
            for spare in to_merge:
                self.merge_category(spare, target)

    def normalize_ampersands(self):
        self.stdout.write("\n--- Normalizing '&' to 'and' ---")
        cats_with_amp = Category.objects.filter(name__contains='&')
        
        for spare in cats_with_amp:
            new_name = spare.name.replace('&', 'and').strip()
            # Fix double spaces if any
            while '  ' in new_name:
                new_name = new_name.replace('  ', ' ')
            
            # Check if new_name exists
            target = Category.objects.filter(name__iexact=new_name).exclude(id=spare.id).first()
            
            if target:
                self.stdout.write(f"Merging '{spare.name}' -> '{target.name}'")
                self.merge_category(spare, target)
            else:
                self.stdout.write(f"Renaming '{spare.name}' -> '{new_name}'")
                spare.name = new_name
                spare.save()

    def merge_category(self, spare, target):
        with transaction.atomic():
            count = Product.objects.filter(category=spare).update(category=target)
            self.stdout.write(f"  - Moved {count} products from '{spare.name}' (ID {spare.id})")
            spare.delete()

    def generate_descriptions(self):
        self.stdout.write("\n--- Generating Descriptions ---")
        cats = Category.objects.filter(Q(description__isnull=True) | Q(description__exact=''))
        count = 0
        for c in cats:
            c.description = f"General category for {c.name}."
            c.save()
            count += 1
        self.stdout.write(f"Updated {count} descriptions.")
