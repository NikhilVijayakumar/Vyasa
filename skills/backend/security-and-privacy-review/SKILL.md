---
name: security-and-privacy-review
description: "Reviews authorized QA checks for access control, file uploads, sessions, secrets, and sensitive-data exposure."
---

# Skill: Security and Privacy QA Review
## Goal
Identify security/privacy test needs for a platform that may handle employee, project, client, and opportunity information.

## Procedure
1. Confirm approved roles, permission matrix, authentication method, data classification, and environment.
2. Review access control for viewing, editing, uploading, exporting, and administering data.
3. Test direct URL/API access and role changes where authorized and in scope.
4. Review file upload handling, validation, storage, error exposure, and malware scanning requirements if defined.
5. Check secrets, logs, screenshots, exports, and test reports for sensitive-data leakage.
6. Consider session expiry, logout, and authentication failures according to the approved design.
7. Record each check, evidence, and limitation; request security-owner review for unresolved risks.

## Output
Security QA checklist, findings, evidence, and questions for the security owner.

## Guardrails
This skill is not a penetration-testing authorization. Do not attack systems or use production data without explicit authorization. Do not assume compliance or authentication requirements.
