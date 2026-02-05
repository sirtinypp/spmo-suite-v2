from django.core.management.base import BaseCommand
from supplies.models import Category, Product


class Command(BaseCommand):
    help = "Deduplicates Categories, preferring Title Case versions."

    def handle(self, *args, **kwargs):
        self.stdout.write("--- Deduplicating Categories ---")

        # 1. Group by normalized name
        normalized_map = {}
        all_cats = Category.objects.all()

        for cat in all_cats:
            norm_name = cat.name.strip().lower()
            if norm_name not in normalized_map:
                normalized_map[norm_name] = []
            normalized_map[norm_name].append(cat)

        duplicates_found = 0

        for norm_name, cats in normalized_map.items():
            if len(cats) > 1:
                duplicates_found += 1

                # 2. Pick the Best Keeper
                # Score: 10 = Exact Title Case ("Films"), 5 = Capitalized ("Films"), 0 = Global Upper ("FILMS")/Lower
                # Tie-breaker: Lower ID (keep older one)
                def score_cat(c):
                    s = 0
                    if c.name == c.name.title():
                        s = 10
                    elif c.name == c.name.capitalize():
                        s = 5
                    return (
                        s,
                        -c.id,
                    )  # Sort descending by score, then ascending by ID (via negative ID text? No, Python sort tuples properly)
                    # We want high score, low ID.
                    # Sort key: (score, -id) -> reversed sort will give high score, high id.
                    # Let's simple sort:

                # Sort: Best FIRST
                # Primary: Score (Desc), Secondary: ID (Asc)
                cats.sort(
                    key=lambda c: (
                        (
                            10
                            if c.name == c.name.title()
                            else (5 if c.name == c.name.capitalize() else 0)
                        ),
                        -c.id,
                    ),
                    reverse=True,
                )

                keeper = cats[0]
                spares = cats[1:]

                self.stdout.write(
                    f"\nProcessing '{norm_name}': Keeping '{keeper.name}' (ID {keeper.id})."
                )

                for spare in spares:
                    # 3. Migrate Products
                    products = Product.objects.filter(category=spare)
                    count = products.count()
                    if count > 0:
                        products.update(category=keeper)
                        self.stdout.write(
                            f"  - Moved {count} products from '{spare.name}' (ID {spare.id}) to keeper."
                        )
                    else:
                        self.stdout.write(
                            f"  - '{spare.name}' (ID {spare.id}) is empty."
                        )

                    # 4. Delete Spare
                    spare.delete()
                    self.stdout.write(f"  - Deleted '{spare.name}'.")

        if duplicates_found == 0:
            self.stdout.write(self.style.SUCCESS("No duplicate categories found."))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n--- Resolved {duplicates_found} Category Groups ---"
                )
            )
