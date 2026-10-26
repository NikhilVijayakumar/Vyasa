---
name: backend-graphql-api-contract-review
description: >-
  Reviews GraphQL schema and resolver changes in the NestJS backend for stable client contracts,
  validation, authorization, pagination, error semantics, and Postman coverage.
  Use only when adding or changing backend GraphQL queries, mutations, inputs,
  outputs, or resolver behavior; do not use for frontend GraphQL client work.
metadata:
  scope: backend
---

# GraphQL API Contract Review

The backend API is GraphQL. Keep the contract aligned with approved OpenSpec behavior and existing client conventions; do not introduce REST endpoints unless an approved change explicitly requires them.

## Schema and behavior

- Review operation names, input/output types, nullability, enum values, defaults, and required fields as a public contract.
- Keep GraphQL DTOs in presentation and map them explicitly to application DTOs. Do not pass GraphQL classes or Prisma records into domain logic.
- Validate length, format, range, enum, relationship, and cross-field constraints on the server; GraphQL scalar types alone are not sufficient validation.
- Define clear behavior for omitted fields versus explicit `null`, especially in update mutations.
- Preserve stable error categories and messages for validation, not-found, conflict, unauthenticated, and forbidden outcomes. Avoid exposing stack traces or persistence implementation details.
- Apply authentication and permission guards to every protected operation and consider object-level access for each returned record.
- Use the shared pagination contract where applicable. Confirm page numbering, default/max page size, sort allowlist, filter semantics, and response metadata remain consistent.
- Keep resolver methods thin and ensure each operation maps to the intended use case exactly once.

## Compatibility and client artifacts

- Check whether an SDL change breaks existing Postman requests or frontend consumers; identify additive versus breaking changes.
- Update the tracked Postman collection when the API contract changes. Keep only shared base URL and token values in the local environment; request-specific test data belongs in the request.
- Include usable variables, auth setup, and assertions for observable outcomes where the collection already follows that pattern. Do not label examples as executed tests unless they were run.
- Verify `/graphql` remains the API endpoint and `/playground` remains a development-only GraphiQL client unless a documented decision changes them.
- Preserve CSRF and CORS behavior. A browser request should be fixed with the required content type/preflight headers, not by weakening server protections.

## Output

Report contract incompatibilities and missing authorization/validation as findings with resolver or DTO paths. Include affected operation names and caller impact. Do not regenerate or change unrelated schema fields.
