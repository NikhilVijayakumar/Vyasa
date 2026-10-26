---
name: react-testing
description: >-
  Tests React components, hooks, forms, and UI state with the project's
  component-test runner (Vitest + React Testing Library by default). Use when
  adding or changing component behavior, form validation display, hooks, or
  UI state transitions that can be verified without a running server or
  browser journey.
---

# React Component Testing

Verify what one component renders and how it responds to interaction — without
booting the application. Recommended default: Vitest + React Testing Library;
adopt the project's actual runner and conventions if different.

## What to test here

- Rendering per state/prop variant, including empty, loading, error, and
  permission-hidden states.
- User interaction: input changes, submits, keyboard flows, emitted callbacks.
- Form validation display and error messaging.
- Custom hooks (via a harness component or hook-testing utility).
- Accessible structure visible in the DOM (roles, names, labels) — deep
  accessibility scanning belongs to `accessibility-testing`.

## Rules

- **Query and assert what users see:** role/label/text queries first; avoid
  internal state, implementation details, and CSS class assertions.
- **Mock at the boundary:** stub network/data providers at the component's
  edge; do not mock the component's own internals. Server behavior is verified
  in `graphql-testing`/`database-integration-testing`.
- Render the single component under test — not the whole page tree. If a test
  needs the whole application, it belongs to `playwright-testing`.
- One behavior per test; assert the observable outcome, not the render count.
- Tag tests with their specification ID (`FR-xx.y` / `FUN-xx`) for coverage
  reporting.
- Never weaken or delete a check to make implementation pass
  (`test-driven-development` applies: Red–Green–Refactor).

## Boundaries

- Full user journeys and real-browser behavior → `playwright-testing`.
- Server/GraphQL/authorization logic → `graphql-testing`.
- Strategy and layer placement → `test-strategy`.
- Failure diagnosis → `test-debugging`.

## Evidence

Report the runner command, the tests written, and the observed result —
including failures and skips. A test count is not evidence; an executed result is.
