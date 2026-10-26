---
name: playwright-testing
description: >-
  Builds and maintains browser-based end-to-end and acceptance tests covering
  complete user journeys through the running application. Use when automating
  workflows that span the UI and backend, when maintaining browser-test
  fixtures and test data, or when a specification scenario must become an
  executable journey. Component-level UI behavior belongs to react-testing.
---

# Playwright Testing (Browser Journeys)

Playwright (the project's selected browser-automation tool) verifies what a
user can actually do in the browser, frontend to backend. Substitute the
project's tool and conventions if different.

## What to test here

- Complete journeys that cross UI and server (sign-in, create/assign/submit
  flows, error paths visible to users).
- Permission-*visible* behavior: hidden controls, redirects, denied-state
  messages. Server-side permission enforcement is proven in
  `graphql-testing`, not re-tested exhaustively here.
- Scenarios the specification marks as acceptance criteria.

## Traces and fixtures

- **Requirement traceability:** tag or name every test with its specification
  ID (`FR-01.1`, `FUN-03`) so acceptance coverage maps back to requirements.
- **Auth reuse:** obtain a session once (for example via the login operation)
  and reuse saved storage state per role; do not re-authenticate inside every
  test when state can be reused safely.
- **Test data:** each test provisions its own uniquely identifiable data and
  asserts only on that data. Tests must be independently runnable and safe to
  run in parallel — no order dependence, no shared mutable fixtures.
- **Determinism:** prefer role/label/text selectors over CSS chains; never
  depend on animation timing; use explicit conditions (expect polls) over
  fixed sleeps.
- **Maintenance:** shared helpers live in fixtures/support files; keep
  journey tests declarative (business steps) and push selector detail into
  helpers.
- **Evidence:** configure traces/screenshots-on-failure before relying on the
  suite — failing runs must leave inspectable evidence for `test-debugging`.

## Boundaries

- Failure diagnosis belongs to `test-debugging` — when a run fails, follow
  that skill; do not ad-hoc patch assertions here.
- Single-component behavior (forms, hooks, validation display) belongs to
  `react-testing`; do not spin a full application to test one component.
- Strategy and layer placement belong to `test-strategy`.
- Gherkin `.feature` files remain specification text; this skill does not add
  a Gherkin runner.

## Rules

- Do not weaken or delete a journey check to make a change pass.
- Report which journeys ran, the command, and the observed result — including
  failures and skips. A green claim without an executed run is not evidence.
