---
name: backend-nestjs-test-verification
description: >-
  Plans and verifies NestJS/GraphQL/Prisma backend changes using the repository's
  configured test, lint, type-check, migration, and Docker workflows. Use when
  an approved backend task requests implementation verification or defines
  backend checks; do not apply it to frontend test planning.
metadata:
  scope: backend
---

# NestJS Backend Test and Verification

Use this skill with `test-driven-development`, the OpenSpec tasks, and the active task's authorization. Do not add or run tests when higher-priority instructions or the user have not authorized testing; record the limitation and continue with allowed checks.

## Before choosing checks

- Read `backend/package.json`, `backend/Makefile`, `backend/README.md`, `docker-compose.yml`, the relevant tests, and the approved task list.
- Identify whether a check is a unit, integration, GraphQL contract, migration, seed, or runtime smoke check. Do not treat one as evidence for another.
- Keep database integration tests on a dedicated database. Follow the documented test database naming guard and never point destructive fixtures at the application or production database.
- Do not use `npx` or another network-dependent tool when a configured local executable is available.

## Test selection

- Unit-test domain and application rules, boundary validation, state transitions, and error mapping.
- Integration-test Prisma repositories and constraints against PostgreSQL, including competing transactions for invariants.
- Exercise GraphQL operations through Nest's test context or the configured API test harness; assert result shape, authorization, validation, and error semantics.
- Test email rendering for both HTML and plain text, escaping, links, and expiry; use MailHog for local delivery smoke checks when specifically requested and available.
- For migrations, validate Prisma schema, apply migrations to a disposable database, and confirm expected constraints and seed repeatability.
- Cover important regressions such as refresh-token replay, OTP single use/rate limits, invitation confirmation, manager preservation, master-data overlap, and null-versus-omitted updates when relevant to the diff.

## Verification discipline

- Follow Red–Green–Refactor when authorized and practical. Tests should assert observable behavior rather than private implementation details.
- Run only checks called for by the approved tasks or user instruction. Use exact configured commands; do not invent project scripts.
- Report exact command/result, test count if available, skipped tests and reasons, unavailable services, and any checks not run.
- Never claim that a migration, database import, email delivery, or HTTP/GraphQL behavior passed based only on source inspection or type-checking.
- Do not weaken or skip assertions simply to obtain a green result.

## Output

Provide a concise verification record grouped by test/check type and call out remaining unverified behavior. A successful lint or type-check does not establish functional correctness.
