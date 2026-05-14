from supplies.models import Product, Category

def populate_safety_levels():
    # 1. Standardized Threshold Mapping (5, 10, 20 only)
    thresholds = {
        'Office Supplies': 20,
        'Paper Materials And Products': 20,
        'Writing And Correction': 20,
        'Janitorial & Cleaning': 10,
        'Cleaning Equipment And Supplies': 10,
        'Medical & First Aid': 10,
        'Medicine': 10,
        'Printer Or Facsimile Or Photocopier Supplies (Consumables)': 5,
        'IT Equipment & Consumables': 5,
        'Information and Communication Technology (ICT) Equipment and Devices and Accessories': 5,
        'Electrical & Hardware': 10,
        'Lighting And Fixtures And Accessories': 10,
    }

    print("--- Initiating Institutional Safety Level Population ---")
    
    products = Product.objects.all()
    updated_count = 0
    
    for product in products:
        category_name = product.category.name
        
        # Determine Threshold
        new_threshold = thresholds.get(category_name, 5) # Default to 5 for others
        
        # Override for high-value furniture/equipment (ordered on request)
        if any(keyword in category_name.lower() for keyword in ['furniture', 'electronics', 'vehicle', 'equipment']):
            new_threshold = 0
            
        if product.reorder_point != new_threshold:
            product.reorder_point = new_threshold
            product.save()
            updated_count += 1
            
    print(f"✅ Successfully updated {updated_count} assets with realistic safety levels.")

if __name__ == "__main__":
    populate_safety_levels()
