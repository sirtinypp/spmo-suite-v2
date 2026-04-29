# SECURITY.md
**The 8 Gates of Universal Hardening & VAPT**
**Goal: Framework-agnostic protection against theft, destruction, and exhaustion.**

## Gate 1: Credential Hygiene (Zero-Secret Policy)
- **Rule:** Code must be public-ready at all times.
- **Requirement:** Mandatory `.env` usage for API keys, DB strings, and secret tokens.
- **VAPT Check:** Pre-execution grep for high-entropy strings (secrets) in source code.

## Gate 2: Access Control (Closed by Default)
- **Rule:** If a route isn't explicitly open, it is blocked.
- **Requirement:** Every module must implement Role-Based Access Control (RBAC). No "Staff-only" routes without an active session check.
- **VAPT Check:** Attempt to access protected endpoints via Incognito/CURL without a cookie.

## Gate 3: Input Sanitization (Anti-Injection)
- **Rule:** All user input is toxic until proven otherwise.
- **Requirement:** Mandatory schema validation (Zod, Django Forms, etc.). Never use raw SQL queries or trust raw HTML.
- **VAPT Check:** Inject "Malicious Payloads" (`<script>`, `' OR 1=1 --`) into forms and verify they are escaped.

## Gate 4: Dependency Integrity (Supply Chain)
- **Rule:** Trust no package.
- **Requirement:** Pin versions (no `^` or `latest` in production). Run `npm audit` or `pip-audit` regularly.
- **VAPT Check:** Review `package-lock.json` or `requirements.txt` for high-severity CVEs before every deployment.

## Gate 5: Data Privacy (Minimalist APIs)
- **Rule:** Only send what is required for the UI.
- **Requirement:** APIs must return filtered Data Transfer Objects (DTOs), never raw database rows.
- **VAPT Check:** Inspect Network responses for sensitive internal fields (hashed passwords, internal IDs, emails).

## Gate 6: Resilience (Anti-DDoS & Availability)
- **Rule:** Protect the server's life.
- **Requirement:** Implement Global Rate Limiting (`429 Too Many Requests`) and set hard timeouts (30s) on all requests. Limit `POST` body sizes (e.g., 5MB).
- **VAPT Check:** "Hammer Test"—hit a non-cached route 50 times in 1 second. Verify the app throttles the requester.

## Gate 7: Transparency (Error & Audit Integrity)
- **Rule:** Mask failures; log mutations.
- **Requirement:** **Generic Errors only.** No stack traces or file paths in production. Every "Write" action must log `User_ID`, `Action`, and `Timestamp`.
- **VAPT Check:** Trigger a `500 error` and verify it shows a clean UI with no system details.

## Gate 8: Recovery (The Lifeboat)
- **Rule:** Prepare for total destruction.
- **Requirement:** Mandatory daily automated database snapshots + "Hard Delete" policy for sensitive user data.
- **VAPT Check:** Verify backup files exist and are stored in a separate cloud/physical location.

**Protocol: If any Gate is open, the app is NOT ready for production.**
