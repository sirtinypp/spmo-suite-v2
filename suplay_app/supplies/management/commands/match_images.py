from django.core.management.base import BaseCommand
from django.conf import settings
from supplies.models import Product
import os


class Command(BaseCommand):
    help = "Matches product images based on item_code"

    def handle(self, *args, **options):
        products = Product.objects.exclude(item_code__isnull=True).exclude(item_code="")
        media_products_dir = os.path.join(settings.MEDIA_ROOT, "products")

        if not os.path.exists(media_products_dir):
            self.stdout.write(
                self.style.ERROR(f"Directory not found: {media_products_dir}")
            )
            return

        self.stdout.write(f"Scanning {media_products_dir} for matching images...")

        matched_count = 0
        total_products = products.count()

        for product in products:
            code = product.item_code.strip()
            # Check common extensions
            found = False
            for ext in [".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"]:
                filename = f"{code}{ext}"
                file_path = os.path.join(media_products_dir, filename)

                if os.path.exists(file_path):
                    # Save relative path to DB field
                    product.image = f"products/{filename}"
                    product.save()
                    self.stdout.write(
                        self.style.SUCCESS(f"Matched: {code} -> {filename}")
                    )
                    matched_count += 1
                    found = True
                    break

            if not found:
                # Optional: specific debug if needed, otherwise silent
                pass

        self.stdout.write(
            self.style.SUCCESS(
                f"Done! Matched {matched_count} images out of {total_products} products with item codes."
            )
        )
