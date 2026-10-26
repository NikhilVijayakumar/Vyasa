---
name: test-maintenance
description: "Maintains test reliability, reduces flakiness, and protects existing coverage as the prototype evolves."
---

# Skill: Test Maintenance and Flakiness Control
## Goal
Keep the suite trustworthy as the prototype evolves toward MVP.

## Procedure
1. Review failures and flakiness trends; distinguish product failures from unstable tests.
2. Update tests only when approved requirements or product behaviour have changed.
3. Keep requirement links, names, test data, and documentation synchronized.
4. Remove obsolete tests only with a reason and traceability review.
5. Improve locator stability, fixtures, setup/teardown, isolation, and deterministic assertions.
6. Track quarantine/skip decisions with owner, reason, date, and expiry/review point.
7. Run targeted and regression tests after maintenance changes.
8. Report coverage lost or altered by test changes.

## Output
Maintenance change summary, flakiness analysis, obsolete-test decisions, and regression evidence.

## Guardrails
Never silently weaken assertions, remove coverage, or permanently quarantine failures without accountable review.
