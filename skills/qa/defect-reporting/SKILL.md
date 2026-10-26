---
name: defect-reporting
description: "Creates reproducible, evidence-based defect reports with expected and actual behaviour and sanitized evidence."
---

# Skill: Defect Reporting
## Goal
Create actionable, evidence-based defects that developers can reproduce and prioritize.

## Required fields
Title, defect ID if assigned by the tracking system, environment/build, feature, requirement link, preconditions, steps, expected result, actual result, reproducibility, severity/priority rationale, evidence, and status.

## Procedure
1. Confirm the issue against an approved requirement or clearly label it as a usability concern/spec gap.
2. Reproduce and record exact steps and data, using synthetic or sanitized data.
3. Write a concise title describing the observable failure.
4. Separate actual facts from suspected cause.
5. Assess impact and severity using the team's approved scale; if no scale exists, propose one for approval rather than inventing official labels.
6. Attach sanitized screenshots/logs/traces where available.
7. Check for duplicates and link related requirements/tests.
8. Verify the fix against the original steps and regression scope.

## Output
Defect report and retest evidence.

## Guardrails
Do not fabricate defect IDs, severity policy, evidence, or root cause. Do not include secrets or personal data.
