---
name: database-integration-testing
description: >-
  Verifies PostgreSQL persistence behavior: constraints, transactions, queries,
  and database-dependent business rules against a real disposable database
  instance. Use when changing repositories, migrations, schema, or rules whose
  correctness lives in the database rather than in application code.
---

# Database Integration Testing

Test against a **real PostgreSQL instance**, not an in-memory imitation —
constraints, transaction semantics, and query behavior are exactly what an
emulator gets wrong. Recommended: a disposable database per run (containerized
or compose-provisioned); substitute the project's database tooling if different.

## What to test here

- Schema constraints: NOT NULL, unique, foreign key, check, and exclusion
  behavior as specified.
- Transaction semantics: rollback on failure, isolation effects the rules
  depend on, commit visibility.
- Repository/query correctness: filters, ordering, pagination, aggregates the
  business rules rely on.
- Migrations: apply cleanly on an empty database and upgrade an existing one
  as the project's migration policy requires.
- Database-dependent business rules (for example uniqueness or ordering rules
  enforced in SQL).

## Setup and teardown (deterministic)

- Provision an isolated database (or schema) per run; never point tests at a
  shared dev/prod database.
- Reset to a known state between tests (truncate or recreate); every test
  creates the rows it needs and asserts only on those rows.
- Seed data must be explicit and minimal — no hidden reliance on leftover
  state.
- Tear down deterministically; a leaked database or port must not break the
  next run.

## Boundaries

- API contract shapes and authorization → `graphql-testing`.
- The application-layer rules around a query → `graphql-testing` unit tests;
  here only when the rule *is* the SQL/constraint.
- Strategy → `test-strategy`; failure diagnosis (constraint violation
  messages, stuck transactions are prime evidence) → `test-debugging`.
- Do not test through the browser; UI journeys are `playwright-testing`.

## Rules

- Treat a constraint violation or deadlock observed while testing as evidence
  about the schema or code — diagnose it; never swallow it with retries.
- Tag tests with specification IDs (`FR-xx.y`, `FUN-xx`).
- Never weaken or delete a check (or a constraint) to make tests pass.

## Evidence

Report the database provisioning method, the command run, and observed
results — including constraint violations, transaction failures, and tests
that could not run because no database was available.
