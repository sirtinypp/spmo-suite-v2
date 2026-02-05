from django.core.management.base import BaseCommand
from django.db import transaction
from supplies.models import Category, Product


class Command(BaseCommand):
    help = "Fixes the specific ICT category merge missed in previous runs."

    def handle(self, *args, **kwargs):
        self.stdout.write("--- Fixing ICT Category Merge ---")

        # The correct target name with "ICT" capitalized properly
        target_name = "Information and Communication Technology (ICT) Equipment and Devices and Accessories"

        # Variations to find (renamed from previous title-casing or original imports)
        variations = [
            "Ict Equipment And Devices And Accessories",
            "Information And Communication Technology (Ict) Equipment And Devices And Accessories",
            "Information and Communication Technology (Ict) Equipment and Devices and Accessories",
        ]

        target, created = Category.objects.get_or_create(name=target_name)
        if created:
            self.stdout.write(f"Created Target: '{target_name}'")
        else:
            self.stdout.write(f"Using Target: '{target_name}' (ID {target.id})")

        with transaction.atomic():
            for var in variations:
                # Find categories matching this variation (case-insensitive)
                to_merge = Category.objects.filter(name__iexact=var).exclude(
                    id=target.id
                )

                for spare in to_merge:
                    count = Product.objects.filter(category=spare).update(
                        category=target
                    )
                    self.stdout.write(
                        f"Merging '{spare.name}' (ID {spare.id}) -> Target"
                    )
                    self.stdout.write(f"  - Moved {count} products.")
                    spare.delete()
                    self.stdout.write(f"  - Deleted '{spare.name}'")

        self.stdout.write(self.style.SUCCESS("\n--- ICT Merge Complete ---"))
