# PLANNING.md
**The Blueprint & Architecture Protocol**
**Goal: Lock the architecture before the first line of code. Focus on Rapid Development and Ease of Maintenance.**

## 0. The Planning Mandate
1. **Blueprint First:** No `src` files are created until the Blueprint is approved.
2. **Speed & Stability:** Prioritize stacks that offer high-level abstractions and low boilerplate.
3. **Maintainability:** If a stack is "easy to build" but "hard to maintain," it is rejected.

## 1. Tech Stack Analysis (The "Rapid-Response" Proposal)
For every project, the agent must provide a structured analysis:
- **Requirement Audit:** What is the core engine? (e.g., Data-heavy, Intelligence-first, or CRUD-focused).
- **The Proposal:** Suggest a stack (e.g., Next.js + Supabase, Django + HTMX, or Vite + Firebase).
- **Rationalization:** 
    - **Speed:** Why is this fast to build?
    - **Management:** How easy is the hosting/database to manage?
    - **Maintenance:** How easy is it for a future agent to understand?

## 2. The Data Foundation (Schema First)
- **Schema Design:** Define tables, relationships, and constraints before the UI.
- **ERD Visualization:** Brainstorm the "Entity Relationship" to ensure data integrity.
- **The Source of Truth:** Confirm where the data lives (Supabase, Local SQLite, etc.).

## 3. The Complexity Audit (Risk Assessment)
- **Identify Hotspots:** What is the "hardest" part of this app? 
- **Constraint Check:** Audit API quotas (Gemini, Maps) and potential scaling bottlenecks.
- **The Pre-Mortem:** Identify why the project might fail and mitigate it in the plan.

## 4. Scope Lock (MVP Boundaries)
- **The North Star:** Define the "Perfect MVP" in 3 bullet points.
- **The "Not-Now" List:** Explicitly list features to be deferred to prevent scope creep.
- **Aesthetic Vibe:** Define the UI standard (e.g., "Premium Dark Glass" or "System Standard").

**Protocol: The agent proposes the Blueprint; the user provides the "Go Signal."**
