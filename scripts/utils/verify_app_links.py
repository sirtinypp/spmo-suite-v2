from supplies.models import AnnualProcurementPlan, Product

# Check relationships
total_app = AnnualProcurementPlan.objects.count()
print(f"Total APP Allocations: {total_app}")

# Check how many have valid product links
app_with_products = AnnualProcurementPlan.objects.filter(product__isnull=False).count()
print(f"APP with valid Product link: {app_with_products}")

# Check for any broken links
broken_links = total_app - app_with_products
print(f"Broken/Null Product links: {broken_links}")

# Sample some records
print("\nSample APP Records:")
for app in AnnualProcurementPlan.objects.select_related("product", "department")[:5]:
    print(
        f"  - Dept: {app.department} | Product ID: {app.product_id} | Product: {app.product.name} | Year: {app.year}"
    )

# Check if products have item_code
print("\nProduct Fields Check:")
sample_product = Product.objects.first()
if sample_product:
    print(f"  Product ID: {sample_product.id}")
    print(f"  Name: {sample_product.name}")
    print(f"  Item Code: {sample_product.item_code}")
    print(f"  Brand: {sample_product.brand}")
