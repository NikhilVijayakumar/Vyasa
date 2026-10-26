---
name: backend-nestjs-architecture-review
description: >-
  Reviews NestJS backend changes in this repository for modular-monolith
  boundaries, pragmatic DDD layering, dependency direction, and transaction
  ownership. Use only for backend modules, cross-module workflows, persistence
  boundaries, or backend architecture; do not apply it to frontend architecture.
metadata:
  scope: backend
---

# NestJS DDD Architecture Review

Review architecture against the repository's documented backend conventions and approved OpenSpec artifacts. This skill is specific to the Staffing NestJS modular monolith; keep the review proportional to the change and do not add layers or abstractions merely to satisfy a pattern.

## Before reviewing

1. Follow the document-first OpenSpec lifecycle and read the relevant proposal, specifications, design, ADR, and tasks.
2. Read `backend/README.md`, the affected module, and nearby modules before suggesting a pattern.
3. Check current `openspec/specs/tech-01-backend-platform-baseline/spec.md` and `docs/backend-implementation-coverage.md` before assuming a capability exists.

## Boundaries to check

- A module owns its domain rules, application use cases, repository contracts, and persistence adapters.
- Keep the dependency direction `presentation → application → domain`; infrastructure implements domain repository ports and is wired through Nest modules.
- GraphQL input/output classes and mappers belong in presentation. Application DTOs must not depend on GraphQL or Prisma-generated types.
- Prisma queries and records stay inside infrastructure persistence adapters. Map database records to domain entities rather than leaking Prisma models to services or resolvers.
- Resolvers remain thin: authenticate/authorize, map inputs, invoke a use case, map its result, and translate boundary errors only when required.
- Repository interfaces should express the feature's actual reads and transactional operations. Avoid generic base repositories and cross-feature repositories without a demonstrated shared need.
- Put multi-record transactions in the persistence adapter that owns those records. Keep business policy in the application/domain layer and preserve atomic invariants under concurrent requests.
- Shared concerns such as pagination belong in `common/` only when multiple modules use the same behavior.
- Keep a modular monolith. Do not introduce services, queues, or distributed transactions unless requirements and an ADR justify them.
- The current platform has no tenant boundary. Do not add tenant abstractions or tenant filters unless the approved requirements change.

## Review questions

- Does each dependency point toward a stable inner-layer contract?
- Does one module reach into another module's Prisma tables or infrastructure directly?
- Are policy decisions hidden in resolvers or persistence code?
- Does the change preserve existing permission checks and session/data invariants?
- Are transactions scoped to the records and repository that own the invariant?
- Does an abstraction improve a current change or only anticipate hypothetical future systems?
- Are module providers and exports limited to the contracts actually consumed outside the module?

## Output

Report findings with file paths and severity. Separate confirmed boundary violations from design questions. State what was reviewed and which architectural concerns were out of scope. Do not rewrite implementation unless asked.
