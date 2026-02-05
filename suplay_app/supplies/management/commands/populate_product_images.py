import os
from django.core.management.base import BaseCommand
from supplies.models import Product


class Command(BaseCommand):
    help = "Populate product image paths from existing media files"

    def handle(self, *args, **options):
        media_dir = "/app/media/products/"

        if not os.path.exists(media_dir):
            self.stdout.write(
                self.style.ERROR(f"Media directory not found: {media_dir}")
            )
            return

        # Get all image files
        image_files = [
            f
            for f in os.listdir(media_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
        ]
        self.stdout.write(
            self.style.SUCCESS(f"Found {len(image_files)} image files in {media_dir}")
        )

        updated_count = 0
        matched_count = 0

        # Try to match each image to a product by item_code
        for filename in image_files:
            # Extract item code from filename (e.g., "01162026-PR-A02.jpg" -> "01162026-PR-A02")
            item_code = os.path.splitext(filename)[0]

            try:
                # Find product by exact item_code match
                product = Product.objects.get(item_code=item_code)
                matched_count += 1

                # Update image field (Django expects relative path from MEDIA_ROOT)
                new_image_path = f"products/{filename}"

                if product.image != new_image_path:
                    product.image = new_image_path
                    product.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Updated: {product.name} -> {filename}")
                    )
                else:
                    self.stdout.write(f"  Skipped: {product.name} (already set)")

            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"✗ No product found for item_code: {item_code}")
                )
            except Product.MultipleObjectsReturned:
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ Multiple products found for item_code: {item_code}"
                    )
                )

        self.stdout.write(self.style.SUCCESS(f"\n=== Summary ==="))
        self.stdout.write(self.style.SUCCESS(f"Image files found: {len(image_files)}"))
        self.stdout.write(self.style.SUCCESS(f"Products matched: {matched_count}"))
        self.stdout.write(self.style.SUCCESS(f"Database updated: {updated_count}"))
