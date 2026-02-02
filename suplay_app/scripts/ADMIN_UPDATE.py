# suplay_app/supplies/admin.py

# --- CUSTOM FILTERS ---
class StockStatusFilter(admin.SimpleListFilter):
    title = 'Stock Status'
    parameter_name = 'stock_status'

    def lookups(self, request, model_admin):
        return (
            ('in_stock', 'In Stock'),
            ('out_of_stock', 'Out of Stock'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'in_stock':
            return queryset.filter(stock__gt=0)
        if self.value() == 'out_of_stock':
            return queryset.filter(stock=0)

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    # Shows Item Code, Name, and Brand in the list
    list_display = ('item_code', 'name', 'brand', 'category', 'supplier', 'price', 'stock')
    search_fields = ('name', 'item_code', 'brand') 
    list_filter = ('category', 'brand', 'supplier', StockStatusFilter)
