# 🔍 SUPLAY Out-of-Stock Filter - Logic Analysis

**Date:** 2026-01-29 09:25 PHT  
**Analyzer:** Logic Specialist  
**Status:** 🐛 BUG FOUND & FIXED

---

## Issue Summary

**User Request:** Verify out-of-stock items display when filter is clicked

**Finding:** Out-of-stock filter was non-functional due to parameter name mismatch between template and view.

---

## Root Cause

### Parameter Mismatch

**Template (home.html, lines 242-244):**
```html
<a href="?stock=out_of_stock...">
    Out of Stock
</a>
```
Template sends: `?stock=out_of_stock`

**View (client.py, line 133):**
```python
stock_status = request.GET.get('status')  # ❌ WRONG!
```
View checks: `?status=out_of_stock`

**Result:** Clicking "Out of Stock" filter had no effect because view never received the parameter.

---

## Current Logic Flow (Post-Fix)

### View Logic (`client.py` lines 132-149)

```python
search_query = request.GET.get('q')
stock_status = request.GET.get('stock')  # ✅ FIXED

if search_query:
    # Search: Show all items (in + out of stock)
    products = products.filter(
        Q(name__icontains=search_query) | 
        Q(item_code__icontains=search_query) |
        Q(description__icontains=search_query)
    )
else:
    # No search: Apply stock filter
    if stock_status == 'out_of_stock':
        products = products.filter(stock=0)  # Only out-of-stock
    else:
        products = products.filter(stock__gt=0)  # Default: in-stock only
```

### Template Filter UI (`home.html` lines 233-245)

**Availability Section:**
- **Any Status:** `?` (clears all filters, shows in-stock by default)
- **In Stock Only:** `?stock=in_stock` (explicitly shows stock > 0)
- **Out of Stock:** `?stock=out_of_stock` (shows stock = 0)

---

## Behavior Matrix

| URL Parameter | View Logic | Products Displayed |
|:---|:---|:---|
| (none) | Default | ✅ In-stock only (`stock > 0`) |
| `?stock=in_stock` | `else` branch | ✅ In-stock only (`stock > 0`) |
| `?stock=out_of_stock` | `if stock_status == 'out_of_stock'` | ✅ Out-of-stock only (`stock = 0`) |
| `?q=paper` | Search mode | ✅ All matching items (in + out of stock) |

---

## Fix Applied

### Change Made
**File:** `client.py`  
**Line 133:** Changed from `request.GET.get('status')` to `request.GET.get('stock')`

```diff
- stock_status = request.GET.get('status')
+ stock_status = request.GET.get('stock')
```

**Impact:** Out-of-stock filter now works correctly

---

## Testing Checklist

### Manual Verification Steps
1. ✅ Navigate to SUPLAY homepage (shows in-stock items by default)
2. ✅ Click "Out of Stock" filter in sidebar
3. ✅ Verify URL changes to `?stock=out_of_stock`
4. ✅ Verify only products with `stock=0` are displayed
5. ✅ Click "In Stock Only" filter
6. ✅ Verify only products with `stock>0` are displayed
7. ✅ Click "Any Status" to clear filter

### Expected Results
- Default view: In-stock items only
- Out-of-stock filter: Only zero-stock items
- Search: All items regardless of stock

---

## Additional Observations

### Filter Preservation
Template correctly preserves filters across navigation:
```html
?stock=out_of_stock
  &category={{ request.GET.category }}
  &supplier={{ request.GET.supplier }}
```

This allows users to combine:
- Category filters
- Supplier filters
- Stock availability filters

### UI Styling
- Active filter highlighted with `fw-bold text-danger` (out-of-stock)
- Active filter highlighted with `fw-bold text-success` (in-stock)

---

## Deployment

**Status:** Local fix applied  
**Next Step:** Deploy to production

**Commands:**
```bash
scp client.py server:/path/to/supplies/views/
docker restart app_store
```

---

## Conclusion

**Bug:** Parameter name mismatch prevented filter from working  
**Fix:** One-line change to align parameter names  
**Impact:** Out-of-stock filter now fully functional  

This was a simple but critical bug that completely disabled the availability filter feature.

---
*Analysis completed by Logic Specialist | 2026-01-29 09:25 PHT*
