# Log: Data Weaver

## Historical Background (Synthesized from History)
The Data Weaver has been responsible for cleaning up fragmented data from legacy systems and ensuring strict allocation logic.

### Key Milestones
- **Product Deduplication (Jan 2026)**: Developed `deduplicate_products.py` and `deduplicate_categories.py` to clean the SUPLAY database.
- **APP Allocation Logic**: Resolved the "0 items found" error by ensuring product visibility was tied correctly to Department APP allocations for years 2025 and 2026.
- **Bulk Imports**: Managed the migration of product master lists from CSV templates into the SUPLAY `virtual_store`.

- **Strict Monthly Limits (Jan 2026)**: Implemented `check_monthly_allocation` helper in `client.py` to enforce month-by-month departmental allocation limits, preventing users from exceeding their allocated quantity for any given month.

### Data Assets
- `scripts/deduplicate_products.py`
- `import_templates/products_master_template.csv`
- `scripts/debug_missing_allocations.py`
- `suplay_app/supplies/management/commands/test_monthly_limit.py`
- `suplay_app/supplies/management/commands/test_search_filters.py`
- `suplay_app/supplies/management/commands/test_cart_security.py`
