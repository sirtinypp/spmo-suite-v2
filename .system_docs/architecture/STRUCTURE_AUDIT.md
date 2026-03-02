# Structure Audit & Organization Report

**Target**: SPMO-SUITE Monorepo (GAMIT, SUPLAY, LIPAD)
**Date**: 2026-01-08

---

## 1. Dependency Check

| App | Status | Notes |
| :--- | :--- | :--- |
| **GAMIT** (`gamit_app`) | ✅ **PASS** | `django-import-export` is installed and used (`inventory/resources.py`). `pillow` is used. Imports align with `requirements.txt`. |
| **LIPAD** (`gfa_app`) | ✅ **PASS** | Dependencies appear clean. `pillow`, `whitenoise`, `gunicorn` present. |
| **SUPLAY** (`virtual_store`) | ✅ **PASS** | `xhtml2pdf` and `django-import-export` are installed and utilized. |

---

## 2. Folder Structure & Clutter Check

### 🔴 Root Level ("Messy")
- **File**: `requirements.txt` (Loose file).
    - *Issue*: Each app has its own `requirements.txt`. This root-level file is likely redundant or confusing.

### 🟡 GAMIT (`gamit_app`)
- **Missing**: No `templates/` folder at project root (located in `inventory/templates`).
- **Missing**: No `tests/` folder at project root (located in `inventory/tests.py`).

### 🟡 LIPAD (`gfa_app`)
- **Missing**: No `templates/` folder at project root (located in `travel/templates`).
- **Messy**: Found loose file `travel/login.html` mixed with Python files. Should be in `templates/`.
- **Missing**: No `tests/` folder at project root.

### 🔴 SUPLAY (`virtual_store`)
- **Messy**: `venv/` directory exists inside the source control area.
- **Messy**: `mydata.json` (Loose file). Should be in a `fixtures/` folder.
- **Missing**: No `templates/` folder at project root.
- **Missing**: No `tests/` folder at project root.

---

## 3. Docker Context Check
All `docker-compose.yml` paths match actual directory names.
- `spmo_website` -> `./spmo_website` ✅
- `gamit_app` -> `./gamit_app` ✅
- `gfa_app` -> `./gfa_app` ✅
- `virtual_store` -> `./virtual_store` ✅

---

## 4. Proposed Move Commands

The following commands are proposed to organize the designated "messy" items.

### SUPLAY Cleaning
1. **Move JSON Data**:
   ```powershell
   mkdir virtual_store\fixtures
   move virtual_store\mydata.json virtual_store\fixtures\
   ```
2. **Remove Environment Folder from Source**:
   *Note: Recommend adding `virtual_store/venv` to `.gitignore` found in root or deleting if unused.*
   ```powershell
   # Manual cleanup required for venv folder (Directory Deletion)
   ```

### LIPAD Cleaning
1. **Relocate Loose Template**:
   ```powershell
   move gfa_app\travel\login.html gfa_app\travel\templates\
   ```
   *(Note: Will require verifying template loading paths or creating a matching subdirectory like `travel/templates/travel/` depending on view logic)*

### Root Cleaning
1. **Consolidate Root Requirements**:
   ```powershell
   # If this file is not needed, delete it.
   del requirements.txt
   ```
