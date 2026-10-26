---
name: backend-nestjs-code-quality
description: >-
  Reviews and improves TypeScript/NestJS backend code for correctness,
  maintainability, type safety, validation, error handling, and consistency
  with this repository's service/repository/DTO/mapper conventions. Use when
  implementing, refactoring, or reviewing backend code; do not use for
  frontend TypeScript or UI code.
metadata:
  scope: backend
---

# NestJS Backend Code Quality

Apply the repository's existing patterns and the approved specification. Prefer clear, small code over framework ceremony or generic abstractions.

## Check the change

- Keep resolver/controller methods thin and move use-case orchestration into application services.
- Keep domain types and application DTOs independent of Nest transport classes, GraphQL decorators, and Prisma-generated types.
- Use repository contracts for persistence. Keep Prisma reads, writes, and record mapping in infrastructure adapters.
- Validate all external inputs at the boundary and enforce domain invariants in the application/domain layer. Do not rely on TypeScript types to validate runtime GraphQL input.
- Handle `undefined`, explicit `null`, empty strings, normalization, and partial updates deliberately. Do not turn an omitted field into an unintended clear or overwrite.
- Translate expected uniqueness, foreign-key, not-found, conflict, and concurrency outcomes into stable application errors. Do not leak raw Prisma errors or internal details to GraphQL clients.
- Keep async behavior explicit. Await operations whose failure affects the request; do not fire-and-forget security, persistence, or notification work without an approved reliability design.
- Keep pagination/search/sort normalization centralized where the shared common implementation applies. Enforce supported sort fields, bounded page sizes, and stable defaults.
- Avoid duplicated validation/mapping logic, unexplained boolean flags, dead code, broad `any`, unsafe casts, and catch blocks that discard useful context.
- Preserve permission guards on protected GraphQL operations and ensure state-changing use cases cannot be reached through an unguarded resolver.
- Follow existing naming, formatting, lint, and TypeScript configuration. Do not suppress a lint/type error broadly to silence a local issue.

## Verification selection

Read `backend/package.json`, `backend/Makefile`, and the approved tasks to identify the configured checks. Run only checks authorized by the active task and applicable agent instructions. Report exact commands and results; distinguish warnings from errors and do not claim an unrun check passed.

## Output

For review, list only actionable findings tied to paths and lines. For implementation, explain the behavior changed, the affected boundary, and the checks actually performed. Keep unrelated cleanup out of the diff.
