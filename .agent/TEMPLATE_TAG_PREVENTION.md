# Django Template Tag Fix - Prevention Guide

## ⚠️ CRITICAL: Never Split Template Tags Across Lines

### The Problem
Django template tags MUST be on a single line. Split tags cause literal text display:

```html
<!-- ❌ WRONG - Will display as literal text -->
<label>Name</label> {{
    form.field_name }}

<!-- ✅ CORRECT - Will render properly -->
<label>Name</label> {{ form.field_name }}
```

---

## File Editing Rules

### ✅ SAFE Methods

#### 1. Python Script (RECOMMENDED)
```python
import re

with open('file.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix split tags
content = re.sub(r'\{\{\s*\r?\n\s+', '{{ ', content)

with open('file.html', 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(content)
```

**Why**: Preserves UTF-8 encoding, line endings, and file structure

#### 2. Manual Editing in VS Code
- Use Find & Replace with regex
- Pattern: `\{\{\s*\n\s+`
- Replace: `{{ `
- **IMPORTANT**: Save with UTF-8 encoding

### ❌ UNSAFE Methods

#### 1. PowerShell `Set-Content`
```powershell
# ❌ DON'T USE - Removes ALL line breaks
(Get-Content "file.html") | Set-Content "file.html"
```
**Result**: Entire HTML file on one line, completely broken

#### 2. PowerShell `Out-File` without encoding
```powershell
# ❌ DON'T USE - Corrupts UTF-8 characters
... | Out-File -FilePath "file.html"
```
**Result**: ₱ becomes ã,‡ and other garbled text

---

## Automated Prevention

### 1. EditorConfig (.editorconfig)
Add to project root:
```ini
[*.html]
# Prevent auto-formatters from wrapping Django template tags
max_line_length = off
trim_trailing_whitespace = true
insert_final_newline = true
charset = utf-8
```

### 2. Pre-commit Hook (.git/hooks/pre-commit)
```bash
#!/bin/bash
# Check for split Django template tags

FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.html$')

for FILE in $FILES; do
    if grep -Pzo '\{\{\s*\n' "$FILE" > /dev/null; then
        echo "ERROR: Split Django template tag found in $FILE"
        echo "Template tags must be on a single line"
        exit 1
    fi
done
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

### 3. CI/CD Template Linter
```yaml
# .github/workflows/template-check.yml
name: Template Validation
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check for split template tags
        run: |
          ! grep -rPzo '\{\{\s*\n' --include="*.html" .
```

---

## Recovery Procedure

If files get corrupted:

### Step 1: Restore from Git
```bash
git restore path/to/file.html
```

### Step 2: Apply Fix with Python
```bash
python fix_templates.py
```

### Step 3: Verify
```bash
# Check for remaining split tags
grep -rPzo '\{\{\s*\n' --include="*.html" .

# Test server
python manage.py runserver
```

---

## Utility Script

Save as `fix_templates.py` in project root:

```python
#!/usr/bin/env python3
"""
Fix split Django template tags in HTML files
Usage: python fix_templates.py [file1.html file2.html ...]
"""
import re
import sys
from pathlib import Path

def fix_template_tags(filepath):
    """Fix split template tags in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count fixes
        original = content
        content = re.sub(r'\{\{\s*\r?\n\s+', '{{ ', content)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8', newline='\r\n') as f:
                f.write(content)
            print(f"✅ Fixed: {filepath}")
            return True
        else:
            print(f"✓ OK: {filepath}")
            return False
    except Exception as e:
        print(f"❌ Error in {filepath}: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python fix_templates.py file1.html file2.html ...")
        sys.exit(1)
    
    files = [Path(f) for f in sys.argv[1:]]
    fixed_count = sum(fix_template_tags(f) for f in files)
    
    print(f"\nFixed {fixed_count} file(s)")
```

---

## Testing Checklist

After fixing template files:

- [ ] Server starts without errors
- [ ] All pages load (no 500 errors)
- [ ] Form fields render as inputs (not `{{ form.* }}`)
- [ ] Special characters display correctly (₱, €, etc.)
- [ ] Hard refresh browser (Ctrl+Shift+R)
- [ ] Test form submission
- [ ] Check git diff for unintended changes

---

## Reference: This Issue

**Date**: 2026-02-05  
**Files Affected**: 
- `gfa_app/travel/templates/travel/form.html` (13 fields)
- `gfa_app/travel/templates/travel/dashboard.html` (2 fields)

**Symptoms**:
- Form fields showing `{{ form.full_name }}`
- Dashboard showing `{{ pal_display.val }}`

**Root Cause**: Code formatter wrapped long lines

**Solution**: Python script with UTF-8 encoding

**Commit**: `2b59540` - "fix(lipad): resolve template rendering issues"

---

**Last Updated**: 2026-02-05  
**Maintained By**: Development Team  
**Status**: Active Prevention Measures
