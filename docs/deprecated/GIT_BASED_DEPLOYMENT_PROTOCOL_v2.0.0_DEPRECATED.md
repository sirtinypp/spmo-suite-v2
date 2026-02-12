# ⚠️ DEPRECATED: Git-Based Deployment Protocol v2.0.0

**Status:** 🔴 DEPRECATED  
**Deprecated Date:** 2026-02-12  
**Reason:** Superseded by Three-Tier Deployment Protocol

---

## 🚫 Do Not Use This Protocol

This protocol is **outdated** and no longer reflects the current SPMO Suite deployment architecture.

---

## ✅ Use This Instead

**New Protocol:** [Three-Tier Deployment Protocol](../knowledge_base/protocols/three_tier_deployment.md)

**Location:** `docs/knowledge_base/protocols/three_tier_deployment.md`

---

## 📋 Why Was This Deprecated?

### Missing Features

1. **No Dev Server:** This protocol only covered Local → Production (2-tier)
   - Current architecture: Local → Dev → Production (3-tier)

2. **No Branch Strategy:** Only mentioned `main` branch
   - Current strategy: `feature/*` → `develop` → `staging` → `main`

3. **No DEBUG Configuration:** Silent on environment-specific settings
   - Current: Explicit DEBUG=True/False per environment

4. **No Approval Gates:** No governance or approval process
   - Current: User approval required for production deployments

5. **No Dev Server Workflow:** Dev server (172.20.3.92) not mentioned
   - Current: Dev server is central to UAT and testing

---

## 📚 Migration Guide

If you were following this protocol, here's how to migrate:

### Old Workflow (2-Tier)
```bash
# Local
git push origin main

# Production
ssh prod-server
git pull origin main
docker compose up -d --build
```

### New Workflow (3-Tier)
```bash
# Local → Dev
git checkout develop
git merge feature/my-feature
git checkout staging
git merge develop
git push origin staging

# Deploy to Dev Server
ssh dev-server
git pull origin staging
docker compose restart

# After UAT → Production
git checkout main
git merge staging
git tag -a v2.x.x -m "Release notes"
git push origin main --tags

# Deploy to Production
ssh prod-server
git pull origin main
docker compose up -d --build
```

---

## 📖 Historical Reference

This protocol was created on **2026-02-06** and served as the deployment standard until the introduction of the dev server and three-tier architecture on **2026-02-12**.

**Key Contributions:**
- Established Git-based deployment (no SCP)
- Documented rollback procedures
- Emphasized container rebuilds
- Required static file collection

These principles are preserved in the new Three-Tier Deployment Protocol.

---

## 🔗 Related Documents

- ✅ [Three-Tier Deployment Protocol](../knowledge_base/protocols/three_tier_deployment.md) - **USE THIS**
- [Emergency Rollback Protocol](../knowledge_base/protocols/emergency_rollback_v1.3.0.md)
- [Testing & QA Protocol](../knowledge_base/protocols/testing_qa.md)
- [Environment Parity Protocol](../knowledge_base/protocols/environment_parity.md)

---

**Archived:** 2026-02-12  
**Replaced By:** Three-Tier Deployment Protocol v2.0
