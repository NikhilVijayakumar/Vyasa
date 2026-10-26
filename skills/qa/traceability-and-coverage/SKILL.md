---
name: traceability-and-coverage
description: "Maps requirements to stories, acceptance criteria, tests, execution evidence, and defects; identifies coverage gaps."
---

# Skill: Traceability and Coverage Review
## Goal
Show whether requirements and acceptance criteria have appropriate tests and evidence.

## Procedure
1. Build links from source → requirement → story → acceptance criterion → test → defect/execution.
2. Identify requirements without tests, tests without requirement links, duplicate tests, and criteria with incomplete coverage.
3. Report coverage by feature and risk, not only by raw test count.
4. Distinguish designed tests from executed tests.
5. Distinguish code coverage from requirement coverage; do not treat them as interchangeable.
6. Explain exclusions and unresolved requirements.
7. Reconcile execution counts against source reports before publishing metrics.

## Output
Traceability matrix, coverage gaps, orphan tests, and prioritized remediation list.

## Guardrails
Do not manufacture coverage percentages or infer execution from the presence of test code.
