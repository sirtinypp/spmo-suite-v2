# Pre-Deployment Simulation Protocol (PDSP)

## Principle
*Zero-Accident Policy.* No logic change or template modification is pushed to the active environment (`views.py`, `.html` templates, etc.) without first undergoing a simulated dry-run to verify semantic correctness and Django parser compatibility.

## Three-Phase Execution

### Phase 1: Analyze & Assess 
1. **Identify Target Files**: What files are being modified? (e.g., `views.py`, `dashboard.html`).
2. **Identify Risk Factors**: Does this involve strict parsers (Django `{% if %}` tags), complex ORM queries, or multi-app dependencies?
3. **Map the exact change**: Write out the *exact* string replacement before touching the file.

### Phase 2: Simulate & Verify
1. **Create the Sandbox**: Create a temporary Python script (`/tmp/simulate_feature.py`) or a temporary Django Template Sandbox file in the `gamit_app` directory.
2. **Execute the Logic**: Run the logic through Django's actual engine using the command line (`docker exec app_gamit python simulate.py`).
3. **Assert Success**: 
    - Does it throw a `TemplateSyntaxError`?
    - Does the ORM query return the expected count?
    - Is the output string exactly what the frontend expects?

### Phase 3: Execute & Monitor
1. **Apply to Production/Dev**: Only after the simulation script returns `Exit Code 0` with the correct output, apply the exact, verified code snippet to the real files using standard tools.
2. **Live Verification**: Run `manage.py check` or hit the endpoint via `curl` to ensure the live environment accepted the verified code.

---
*By strictly adhering to this protocol, we eliminate "accidental" syntax errors and ensure 100% stability during refactoring phases.*
