---
name: test-execution-review
description: "Summarizes actual test execution honestly, including passes, failures, blockers, not-run tests, evidence, and limitations."
---

# Skill: Test Execution Review and Reporting
## Goal
Produce honest, reproducible execution summaries for the prototype and MVP.

## Procedure
1. Confirm test plan/version, environment, build, test data, and exact commands.
2. Collect raw results from the actual test runner or approved evidence.
3. Use only PASS, FAIL, BLOCKED, NOT RUN, NOT APPLICABLE (or mapped project equivalents).
4. Reconcile totals and list exclusions/retries; avoid double-counting retries as separate tests unless the report convention says so.
5. Link failures to defects or classify them as spec, environment, data, or automation issues.
6. Summarize coverage, key risks, blocked/not-run scope, and known limitations.
7. State clearly whether results are for a prototype demonstration or an MVP release gate.
8. Recommend next steps without claiming release approval.

## Output
Execution report with scope, environment/build, summary counts, failures/blockers, evidence links, known gaps, and recommendation.

## Guardrails
Never report unexecuted tests as passed. Never invent counts, screenshots, logs, defects, or sign-off.
