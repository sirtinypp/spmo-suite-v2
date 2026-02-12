# SPMO Suite Deployment Protocol
**Official Deployment Standard**  
**Version:** 3.0  
**Effective Date:** 2026-02-12  
**Status:** ✅ ACTIVE

---

## 🎯 Primary Protocol

**Use This:** [Three-Tier Deployment Protocol](knowledge_base/protocols/three_tier_deployment.md)

**Location:** `docs/knowledge_base/protocols/three_tier_deployment.md`

---

## 📋 Quick Summary

The SPMO Suite uses a **three-tier deployment architecture**:

```
Local Development → Dev/Test Server → Production Server
   (develop)           (staging)           (main)
```

### Environment Details

| Environment | Server | Branch | Domain | DEBUG |
|:------------|:-------|:-------|:-------|:------|
| **Local** | Your machine | `develop` | localhost | True |
| **Dev/Test** | 172.20.3.92 | `staging` | *-dev.up.edu.ph | True |
| **Production** | 172.20.3.91 | `main` | *.up.edu.ph | False |

---

## 🚀 Quick Deployment Commands

### Deploy to Dev Server
```bash
git checkout staging
git merge develop
git push origin staging

ssh -p 9913 ajbasa@172.20.3.92
cd ~/spmo_suite
git pull origin staging
docker compose restart
```

### Deploy to Production
```bash
git checkout main
git merge staging
git tag -a v2.x.x -m "Release notes"
git push origin main --tags

ssh -p 9913 ajbasa@172.20.3.91
cd ~/spmo_suite
git pull origin main
docker compose up -d --build
```

---

## 📚 Related Protocols

### Core Protocols
- ✅ **[Three-Tier Deployment](knowledge_base/protocols/three_tier_deployment.md)** - Primary deployment workflow
- [Testing & QA](knowledge_base/protocols/testing_qa.md) - Testing requirements per tier
- [Environment Parity](knowledge_base/protocols/environment_parity.md) - Maintaining consistency

### Emergency Procedures
- [Emergency Rollback v1.3.0](knowledge_base/protocols/emergency_rollback_v1.3.0.md) - Quick rollback commands
- [Production Lock](../knowledge_base/protocols/production_lock.md) - File lock system

### Governance
- [Version Control](../knowledge_base/protocols/version_control.md) - Commit standards
- [Agent Decision-Making](../knowledge_base/protocols/agent_decision_delegation.md) - Approval gates

---

## 🔄 Approval Requirements

| Action | Dev Server | Production |
|:-------|:-----------|:-----------|
| **Code Deployment** | No approval | ✅ User approval |
| **Database Changes** | No approval | ✅ User approval |
| **Config Changes** | Notification | ✅ User approval |
| **Hotfix** | No approval | ✅ Expedited approval |

---

## ⚠️ Deprecated Protocols

The following protocols are **deprecated** and should not be used:

- ❌ [GIT_BASED_DEPLOYMENT_PROTOCOL v2.0.0](deprecated/GIT_BASED_DEPLOYMENT_PROTOCOL_v2.0.0_DEPRECATED.md) - Replaced by Three-Tier Protocol

---

## 📖 For More Details

See the complete [Three-Tier Deployment Protocol](knowledge_base/protocols/three_tier_deployment.md) for:
- Detailed workflows for each deployment type
- Branch protection rules
- Rollback procedures
- Testing requirements
- Security standards
- Monitoring guidelines

---

**Last Updated:** 2026-02-12  
**Next Review:** 2026-05-12  
**Maintained By:** SPMO Development Team
