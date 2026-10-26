---
name: database-integration-testing
description: >-
  Verifies SQLite persistence behavior: constraints, transactions, queries,
  and database-dependent business rules against a real disposable database
  file. Use when changing repositories, migrations, schema, or rules whose
  correctness lives in the database rather than in application code.
---

# Database Integration Testing

Test against a **real SQLite database** opened with the same connection
settings production uses (`PRAGMA foreign_keys`, journal mode, busy timeout) —
not a mock repository. Constraints, transaction semantics, and query behavior
are exactly what a mock gets wrong. Recommended: a fresh database file in a
temporary directory per test or per run (`tmp_path` with pytest); use
`:memory:` only when the behavior under test does not depend on file-level
locking, WAL, or reopening the database.

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

- MCP tool and integration contract shapes → `api-contract-testing`.
- The application-layer rules around a query → unit tests; here only when the
  rule *is* the SQL/constraint.
- Strategy → `test-strategy`; failure diagnosis (constraint violation
  messages, stuck transactions are prime evidence) → `test-debugging`.
- Do not test through a running MCP client; protocol round-trips belong to contract tests.

## Rules

- Treat a constraint violation or `database is locked` error observed while testing as evidence
  about the schema or code — diagnose it; never swallow it with retries.
- Tag tests with specification IDs (`FR-xx.y`, `FUN-xx`).
- Never weaken or delete a check (or a constraint) to make tests pass.

## Evidence

Report the database provisioning method, the command run, and observed
results — including constraint violations, transaction failures, and tests
that could not run because no database was available.
