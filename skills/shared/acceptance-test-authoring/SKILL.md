---
name: acceptance-test-authoring
description: >-
  Turns approved specifications and acceptance scenarios into executable or
  manually verifiable acceptance checks with traceability back to requirements.
  Use after specifications and tasks are approved, to author the acceptance
  verification for a change.
metadata:
  scope: shared
---

# Acceptance Test Authoring

The specification says what the system must do. This skill turns that into
checks that prove it does. It is distinct from `gherkin-authoring`, which
authors the scenarios themselves; this skill defines how they are verified.

## What to author

For each approved requirement or acceptance scenario, produce:

- an executable acceptance test where a suitable runner and step definitions
  exist, or
- a clearly written manual verification procedure with expected results, where
  automation is not practical.

Record which requirements are covered by automated checks, by manual checks, and
by neither.

## Rules

- Every acceptance check traces to a specific requirement or scenario.
- Assert observable outcomes, not implementation details.
- Cover the negative, validation, and error paths the specification defines,
  not just the happy path.
- Do not treat Gherkin text as executable unless the runner and step definitions
  exist.
- Do not weaken or delete an acceptance check to make implementation pass.

## Evidence

Report, per check: what it verifies, how it is run, and the observed result —
including failures, skips, and checks that could not run. A passing acceptance
claim without an executed (or explicitly manual) check is not evidence.
