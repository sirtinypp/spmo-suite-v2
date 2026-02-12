# Testing & Quality Assurance Protocol
**SPMO Suite - QA Standards**  
**Version**: 1.0  
**Effective Date**: 2026-02-12

---

## 🎯 Purpose

Define testing requirements and quality assurance standards for the SPMO Suite across all deployment tiers.

---

## 🧪 Testing Tiers

### Tier 1: Local Development Testing

**Responsibility**: Developer  
**Timing**: Before committing code  
**Blocking**: No (but recommended)

**Requirements**:
- ✅ Code runs without errors
- ✅ Changed functionality manually tested
- ✅ No console errors in browser
- ✅ No hardcoded credentials
- ✅ Follows coding standards

**Tools**:
- Browser DevTools
- Django development server
- Local database

---

### Tier 2: Dev Server Testing (UAT)

**Responsibility**: User + Stakeholders  
**Timing**: After dev server deployment  
**Blocking**: Yes (for production deployment)

**Requirements**:
- ✅ All critical user flows tested
- ✅ Cross-browser testing (Chrome, Firefox, Edge)
- ✅ Mobile responsiveness verified
- ✅ Forms validation tested
- ✅ Authentication/authorization tested
- ✅ Database operations verified
- ✅ No critical bugs found

**Test Environments**:
- sspmo-dev.up.edu.ph (and app subdomains)
- Test database with sanitized data

**UAT Checklist Template**:
```markdown
## UAT Report - [Feature Name]
**Date**: YYYY-MM-DD
**Tester**: [Name]
**Environment**: Dev Server

### Test Cases
- [ ] User can login successfully
- [ ] User can [perform action]
- [ ] Data saves correctly
- [ ] Error messages display properly
- [ ] Mobile view works correctly

### Browsers Tested
- [ ] Chrome
- [ ] Firefox
- [ ] Edge

### Issues Found
- [List any bugs or issues]

### Recommendation
- [ ] Approve for production
- [ ] Needs fixes before production
```

---

### Tier 3: Production Smoke Testing

**Responsibility**: Developer + SysOps  
**Timing**: Immediately after production deployment  
**Blocking**: No (but critical for monitoring)

**Requirements**:
- ✅ All apps accessible (HTTP 200)
- ✅ Login functionality works
- ✅ Critical user flows verified
- ✅ No errors in logs (first 30 minutes)
- ✅ Database connectivity confirmed

**Smoke Test Script**:
```bash
#!/bin/bash
# Production smoke tests

echo "Testing SPMO Hub..."
curl -I https://sspmo.up.edu.ph | grep "200 OK"

echo "Testing GAMIT..."
curl -I https://gamit-sspmo.up.edu.ph | grep "200 OK"

echo "Testing LIPAD..."
curl -I https://lipad-sspmo.up.edu.ph | grep "200 OK"

echo "Testing SUPLAY..."
curl -I https://suplay-sspmo.up.edu.ph | grep "200 OK"

echo "Checking container status..."
docker-compose ps

echo "Checking recent logs for errors..."
docker-compose logs --tail=50 | grep -i error
```

---

## 🐛 Bug Severity Classification

| Severity | Description | Response Time | Workflow |
|:---------|:------------|:--------------|:---------|
| **P0 - Critical** | Service outage, data loss | Immediate | Hotfix |
| **P1 - High** | Major functionality broken | < 4 hours | Hotfix |
| **P2 - Medium** | Minor functionality broken | < 24 hours | Next release |
| **P3 - Low** | Cosmetic, typos | Next sprint | Backlog |

---

## ✅ Acceptance Criteria

### Feature Acceptance
A feature is considered "done" when:
1. Code is committed and merged to develop
2. Deployed to dev server
3. UAT completed successfully
4. No P0/P1 bugs found
5. Documentation updated (if applicable)

### Production Readiness
A release is ready for production when:
1. All features have passed UAT
2. No P0/P1 bugs outstanding
3. Database migrations tested on dev server
4. Rollback plan documented
5. User approval obtained

---

## 📝 Test Documentation

### Required Documentation
- UAT reports (stored in `docs/testing/uat/`)
- Bug reports (stored in `docs/testing/bugs/`)
- Test data specifications (stored in `docs/testing/data/`)

### Bug Report Template
```markdown
## Bug Report - [Short Description]
**Date**: YYYY-MM-DD
**Reporter**: [Name]
**Environment**: [Local/Dev/Production]
**Severity**: [P0/P1/P2/P3]

### Description
[Clear description of the bug]

### Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happens]

### Screenshots
[If applicable]

### Additional Context
- Browser: [Chrome/Firefox/Edge]
- User role: [Admin/Staff/etc]
- Affected apps: [Hub/GAMIT/LIPAD/SUPLAY]
```

---

## 🔄 Continuous Improvement

- Review test failures monthly
- Update test cases based on production issues
- Maintain test data quality on dev server
- Gather feedback from UAT participants

---

**Approved By**: User (ajbasa)  
**Next Review**: 2026-05-12
