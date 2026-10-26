---
name: graphql-testing
description: >-
  Tests GraphQL operations and the NestJS server layer: queries, mutations,
  input validation, response and error shapes, resolver/provider unit behavior,
  and authorization enforced at the server boundary. Use when changing any
  resolvers, services, guards, inputs, or API contract behavior. Database
  persistence specifics belong to database-integration-testing; browser
  journeys to playwright-testing.
---

# GraphQL and Server Testing

Verify the API contract and server behavior directly, without a browser.
Recommended approach: NestJS testing utilities (`Test.createTestingModule`)
with the project's test runner; substitute the project's stack if different.

## Contract rules

- **HTTP 200 is not success.** GraphQL responds 200 with an `errors` array on
  failure. Every operation test asserts the response *body*: expected data
  present, `errors` absent (or matching the expected error code/path).
- Test both poles for every operation: success shape **and** failure shape —
  validation errors, auth denials, not-found, and business-rule rejections the
  specification defines.
- Assert response shape against the schema/contract: required fields present,
  types correct, no unintended leakage of fields.
- Errors must carry the specified message/code without leaking internal detail
  (stack traces, SQL, existence of records the caller may not know about).

## Authorization (server boundary)

- Prove forbidden operations are rejected by the **server** with the caller
  bypassing the UI entirely: unauthenticated, wrong-role, and out-of-scope
  resource access must each fail at the resolver/guard layer.
- Parameterize over roles: same operation, each role, expected allow/deny per
  specification (for example `fun-03` data-scope rules).
- UI hiding of controls is not authorization; it belongs to
  `playwright-testing`/`react-testing` as display behavior only.

## Unit level (NestJS providers)

- Services/guards/resolvers: test business rules with collaborators mocked at
  their boundaries; one behavior per test.
- Do not mock the unit under test; do not assert private implementation.

## Boundaries

- Persistence, constraints, transactions → `database-integration-testing`
  (here, treat repositories as collaborators unless the test exists to verify
  the query itself).
- End-to-end journeys → `playwright-testing`.
- Strategy, requirement-ID tagging, `errors[]` principle → `test-strategy`.
- Failure diagnosis → `test-debugging`.

## Rules

- Tag tests with specification IDs (`FR-xx.y`, `FUN-xx`).
- Never weaken or delete a check to make implementation pass.

## Evidence

Report the runner command per test group and the observed results, including
authorization negatives that failed to deny — a denial that did not occur is a
security finding, record it as such.
