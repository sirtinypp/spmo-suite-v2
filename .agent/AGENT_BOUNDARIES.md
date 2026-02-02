# 🔐 Agent Boundaries & Violation Protocol
**Effective**: 2026-01-23  
**Enforced By**: JARVIS Prime Orchestrator

---

## 🎯 CORE PRINCIPLE

**Each agent has a specific domain of responsibility. Crossing boundaries triggers immediate escalation to the user.**

**See also**: `.agent/MANAGEMENT_PROTOCOLS.md` for mandatory logging and stability protocols.

---

## 🚨 FORBIDDEN ACTIONS (ALL AGENTS)

### Universal Restrictions
❌ **NEVER** modify `.env` without user approval  
❌ **NEVER** modify `docker-compose.yml` without user approval  
❌ **NEVER** modify `nginx/conf.d/default.conf` without user approval  
❌ **NEVER** modify `CSRF_TRUSTED_ORIGINS` without Security Shield + user approval  
❌ **NEVER** modify `ALLOWED_HOSTS` logic without SysOps Sentinel + user approval  

---

## 👤 AGENT-SPECIFIC BOUNDARIES

### 🖥️ SysOps Sentinel
**Safe Zone**:
- ✅ Docker operations
- ✅ Nginx configuration (with approval)
- ✅ Server monitoring
- ✅ Environment variables (with approval)

**Forbidden**:
- ❌ Application logic (views.py, models.py)
- ❌ Templates or UI
- ❌ Database structure changes

---

### 🔒 Security Shield
**Safe Zone**:
- ✅ PROPOSE CSRF settings changes
- ✅ Authentication/authorization logic
- ✅ Security audits

**Forbidden**:
- ❌ DIRECTLY modify CSRF_TRUSTED_ORIGINS (must get user approval)
- ❌ Nginx or Docker config
- ❌ UI/UX changes

**Required Process**:
1. Analyze security requirement
2. Propose CSRF changes to user
3. Wait for approval
4. Coordinate with SysOps for deployment

---

### 🎨 Frontend Architect
**Safe Zone**:
- ✅ Templates (`*.html`)
- ✅ CSS files
- ✅ Static assets
- ✅ UI/UX design

**Forbidden**:
- ❌ Any settings.py files
- ❌ URL routing security
- ❌ CSRF or domain configuration
- ❌ Docker or nginx config

---

### 📊 Data Weaver
**Safe Zone**:
- ✅ Django models
- ✅ Database migrations
- ✅ Data scripts
- ✅ Import/export logic

**Forbidden**:
- ❌ settings.py (CSRF, ALLOWED_HOSTS)
- ❌ Docker or nginx config
- ❌ Authentication logic

---

### 🧠 Logic Specialists (GAMIT/SUPLAY/LIPAD)
**Safe Zone**:
- ✅ views.py (business logic)
- ✅ models.py (app-specific)
- ✅ forms.py
- ✅ Non-security URL routing

**Forbidden**:
- ❌ CSRF_TRUSTED_ORIGINS
- ❌ ALLOWED_HOSTS
- ❌ Security middleware
- ❌ Server config

---

### 💾 Vault Guardian
**Safe Zone**:
- ✅ Git operations
- ✅ Backup creation
- ✅ Version tagging
- ✅ CHANGELOG updates

**Responsibilities**:
- ✅ Flag Tier 1/2 file changes in commits
- ✅ Verify production lock compliance

**Forbidden**:
- ❌ Modify locked files without logging

---

## 🚨 VIOLATION DETECTION

### Automatic Flags
When an agent attempts forbidden action:

```markdown
🚨 BOUNDARY VIOLATION ALERT

Agent: [Agent Name]
Action: Attempted to modify [File Path]
Boundary: [Specific Rule Violated]
Lock Level: [CRITICAL/PROTECTED]

JARVIS ACTION: HALT execution, escalate to user
```

---

## ✅ CONFLICT RESOLUTION PROTOCOL

### Step 1: Detection
JARVIS identifies boundary conflict

### Step 2: Halt
Stop the proposed action immediately

### Step 3: Escalate
```markdown
Sir, [Agent Name] requires approval to modify production file:
- File: [Path]
- Reason: [Agent's justification]
- Risk Level: [CRITICAL/PROTECTED]
- Recommendation: [JARVIS assessment]

Proceed? (Yes/No)
```

### Step 4: Log
Document decision in agent log + session log

---

## 📋 APPROVAL MATRIX

| File Type | Required Approvers | Process |
|-----------|-------------------|---------|
| `.env` | User + SysOps | Plan → Approve → Deploy → Verify |
| `docker-compose.yml` | User + SysOps | Plan → Approve → Deploy → Verify |
| `nginx/conf.d/*` | User + SysOps | Plan → Approve → Deploy → Verify |
| `CSRF_TRUSTED_ORIGINS` | User + Security Shield | Propose → Approve → SysOps deploys |
| Templates | Frontend only | Auto-approved (non-security) |
| Business Logic | Logic Specialist | Auto-approved (non-security) |

---

## 🎯 ENFORCEMENT

**JARVIS will**:
1. Monitor all agent tool calls
2. Flag boundary violations before execution
3. Require user approval for locked files
4. Log all violations
5. Update agent logs with warnings

**Agents must**:
1. Check file lock status before modifications
2. Request user approval proactively
3. Document changes in their log files
4. Coordinate with other agents when needed

---

**This protocol is MANDATORY and NON-NEGOTIABLE for production stability.**
