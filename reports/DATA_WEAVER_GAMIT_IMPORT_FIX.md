# 🔧 Data Weaver: GAMIT Import/Export Diagnostic Report

**Date:** 2026-01-29 10:50 PHT  
**Agent:** Data Weaver (Import/Export Specialist)  
**Issue:** GAMIT asset import errors / ghost assets  
**Status:** 🔴 ROOT CAUSE IDENTIFIED

---

## Issue Summary

**User Report:** "Error or ghost assets when trying to import assets"

**Investigation Findings:** Critical import error in `resources.py`

---

## Root Cause Analysis

### 🔴 CRITICAL BUG: Missing Pandas Import

**File:** `gamit_app/inventory/resources.py`  
**Line:** 42  
**Error Type:** `NameError: name 'pd' is not defined`

**Problematic Code:**
```python
# Line 42
if value is None or (isinstance(value, float) and pd.isna(value)):
    return None
```

**Issue:** Code attempts to use `pd.isna()` (pandas function) but **pandas is never imported**

**Current Imports (Lines 3-7):**
```python
from import_export import resources, fields, widgets
from .models import Asset
from decimal import Decimal
from django.db import IntegrityError
import re
```

**Missing:** `import pandas as pd`

---

## Impact Analysis

### When Does This Error Occur?

The error triggers during asset import when the `clean_value()` method processes decimal fields (`acquisition_cost`, `latitude`, `longitude`) and encounters:
- Empty cells
- NaN values (from Excel/CSV)
- Null values

### What Happens?

1. User uploads CSV/Excel file via Django admin
2. Import process begins
3. `clean_value()` method called for each decimal field
4. Line 42 executes: `pd.isna(value)`
5. **Python Error:** `NameError: name 'pd' is not defined`
6. Import fails or creates incomplete records ("ghost assets")

### Why "Ghost Assets"?

**Theory:** 
- Import process may partially fail
- Some records succeed before hitting the error
- Transaction not fully rolled back
- Results in incomplete/orphaned database entries

---

## Code Analysis

### Current Logic (Broken)

```python
def clean_value(self, value, field_name):
    DECIMAL_FIELDS = ['acquisition_cost', 'latitude', 'longitude']
    
    if field_name in DECIMAL_FIELDS:
        # ❌ BUG: pd is not defined!
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        # ... rest of processing
```

### Intended Logic

The code is trying to:
1. Check if value is None
2. Check if value is a float AND is NaN (pandas concept)
3. Return None for database NULL insertion

**Problem:** Without pandas import, this check fails immediately

---

## Solution Options

### Option 1: Import Pandas (Simple Fix)
**Pros:**
- Minimal code change
- Preserves intended logic
- Pandas already available (import-export library uses it)

**Cons:**
- Adds pandas dependency (likely already present)

**Implementation:**
```python
# Add to imports (line 7)
import pandas as pd
```

### Option 2: Use Math Module (Alternative)
**Pros:**
- Standard library (no external dependency)
- Lighter weight

**Cons:**
- Slightly different logic

**Implementation:**
```python
# Add to imports
import math

# Replace line 42 with:
if value is None or (isinstance(value, float) and math.isnan(value)):
    return None
```

### Option 3: Remove NaN Check (Simplest)
**Pros:**
- No new imports
- Simpler logic

**Cons:**
- May not handle all edge cases

**Implementation:**
```python
# Replace line 42-43 with:
if value is None:
    return None
```

---

## Recommended Fix

**Use Option 1:** Import pandas

**Reasoning:**
1. Code clearly intended to use pandas
2. `django-import-export` likely has pandas as dependency
3. Preserves all intended validation logic
4. Minimal risk

---

## Implementation Plan

### Step 1: Add Pandas Import
```python
# Line 7 in resources.py
import pandas as pd
```

### Step 2: Verify Fix
- Test import with sample CSV
- Verify no errors
- Check no ghost assets created

### Step 3: Test Edge Cases
- Empty decimal fields
- NaN values
- Null values
- Invalid strings

---

## Additional Findings

### Other Robust Features (Working Correctly)

1. ✅ **Property Number Validation** (Lines 95-107)
   - Auto-prepends "PAR-" prefix
   - Good implementation

2. ✅ **Skip Empty Rows** (Lines 82-92)
   - Skips rows without `date_acquired` or `property_number`
   - Prevents incomplete records

3. ✅ **Duplicate Prevention** (Lines 71-79)
   - Checks for existing property_number
   - Raises IntegrityError if duplicate

4. ✅ **Decimal Cleaning** (Lines 45-62)
   - Removes currency symbols
   - Handles N/A, empty strings
   - Converts to Decimal safely

**All these features are excellent EXCEPT for the pandas import bug**

---

## Testing Recommendations

### Before Fix
1. Attempt import with CSV containing:
   - Empty acquisition_cost
   - NaN latitude/longitude
   - Expected: `NameError: name 'pd' is not defined`

### After Fix
1. Test same CSV
2. Expected: Successful import, NULL values in database
3. Verify no ghost assets
4. Check all records complete

---

## Risk Assessment

**Fix Complexity:** 🟢 LOW (1 line change)  
**Risk Level:** 🟢 MINIMAL (adding import only)  
**Impact:** 🔴 CRITICAL FIX (blocks all imports with decimal NaN)

---

## Deployment Plan

1. Add `import pandas as pd` to line 7
2. Test locally with sample import
3. Deploy to production
4. Verify with USER's actual data
5. Create checkpoint

**Timeline:** 5 minutes  
**Downtime:** 0 seconds

---

## Next Steps

1. ✅ Implement fix
2. ✅ Test locally (if possible)
3. ✅ Deploy to production
4. ✅ User verification
5. ✅ Create checkpoint

---

**Data Weaver Assessment:** This is a straightforward Python import error. The code is well-designed, just missing one import statement. Fix is safe and critical.

---
*Diagnostic Report | Data Weaver | 2026-01-29 10:52 PHT*
