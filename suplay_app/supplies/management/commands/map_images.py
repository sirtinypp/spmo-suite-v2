from django.core.management.base import BaseCommand
from supplies.models import Product
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Map product images based on item_code'

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        updated_count = 0
        
        media_root = settings.MEDIA_ROOT
        products_dir = os.path.join(media_root, 'products')

        self.stdout.write(f"Scanning {products_dir} for images...")

        if not os.path.exists(products_dir):
             self.stdout.write(self.style.ERROR(f"Directory not found: {products_dir}"))
             return

        for product in products:
            if not product.item_code:
                continue
            
            # Check for jpg, jpeg, png
            found = False
            for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']:
                filename = f"{product.item_code}{ext}"
                file_path = os.path.join(products_dir, filename)
                
                if os.path.exists(file_path):
                    # Relative path from MEDIA_ROOT
                    db_path = f"products/{filename}"
                    if product.image != db_path:
                        product.image = db_path
                        product.save()
                        self.stdout.write(self.style.SUCCESS(f"Mapped {product.item_code} -> {db_path}"))
                        updated_count += 1
                        found = True
                    break
            
            if not found and product.image:
                # Optional: Check if existing image is valid? No, let's just map new ones.
                pass

        self.stdout.write(self.style.SUCCESS(f"Successfully mapped {updated_count} product images."))
