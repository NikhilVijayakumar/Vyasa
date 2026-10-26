---
name: test-strategy
description: >-
  Defines the test strategy for a change: test layers and boundaries, what each
  layer owns, coverage expectations, and tooling decisions. Use when planning
  verification for an OpenSpec change, when writing specifications or tasks that
  mention testing, or when deciding where a new check belongs.
---

# Test Strategy

Decide *where a check belongs before writing it*. This skill is
technology-agnostic: substitute the project's language, runners, and conventions
for the generic terms below.

## The layers

| Layer | Owns | Must not own |
|---|---|---|
| Unit | Business rules, pure logic, small provider behavior | HTTP, database, browser |
| Component | Focused UI behavior of one component/hook/form | Full journeys, server calls beyond stubs |
| Integration / contract | Server operations against real collaborators (API surface, persistence) | UI rendering |
| End-to-end | Complete user journeys through the running application | Exhaustive edge-case matrices |

Prefer the lowest layer that can observable-fail for the behavior under test.
A check that belongs one layer down is usually slower, flakier, and harder to
diagnose.

## Rules

- Every automated check traces to a specification requirement or scenario ID
  (for example `FR-01.1`, `FUN-03`, `QA-004`). Tag or name the test with that ID
  so acceptance coverage can be reported per requirement.
- **Authorization is verified at the server boundary**, not only in the UI:
  negative tests must prove a forbidden operation is rejected by the server
  even when UI affordances are bypassed. UI tests only verify permission-visible
  behavior (hidden controls, redirects).
- **A successful HTTP status is not a successful API operation.** For
  GraphQL-style endpoints, HTTP 200 can carry an `errors` payload; assert on the
  response body's errors, not the status code alone.
- Cover the negative, validation, and error paths the specification defines,
  not only the happy path.
- State tools as recommendations or project-selected defaults. Never claim a
  runner, fixture, or environment exists until it is verified in the project.
- Not every change needs every layer. Choose layers in proportion to the
  change's risk and record that choice in the tasks artifact.

## Tooling decisions

When a change requires new test tooling, decide and record: runner, how test
data is provisioned and cleaned, how the environment is started, and which
layer owns each new check. These decisions belong in the change's design/tasks,
not silently in code.

## Evidence

Report which layers were exercised, the exact command per layer, and the
observed result — including failures, skips, and layers that could not run.
A strategy document without executed checks is a plan, not verification.
