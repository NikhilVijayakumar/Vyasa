---
name: api-contract-testing
description: "Creates API contract checks from approved API schemas and contracts; identifies contract gaps without inventing endpoints."
---

# Skill: API Contract Testing
## Goal
Check that API requests and responses conform to approved API contracts and preserve integration expectations.

## Procedure
1. Use an approved OpenAPI/schema or explicit contract as the source of truth.
2. Verify methods, paths, authentication requirements, request fields, types, required/optional fields, response schemas, status codes, and documented error formats.
3. Test valid, invalid, boundary, missing-field, unexpected-field, and unauthorized requests where defined by the contract.
4. Check compatibility between consumer expectations and provider responses.
5. Validate pagination, filtering, sorting, idempotency, and versioning only when they are part of the contract.
6. Keep secrets out of logs and test reports.
7. Link failures to contract lines/version and capture sanitized request/response evidence.
8. Distinguish a missing/ambiguous contract from a confirmed implementation defect.

## Output
Contract test inventory, automated checks where supported, compatibility findings, and contract gaps.

## Guardrails
Do not invent endpoints, payloads, status codes, or authentication mechanisms. If no API contract exists, recommend creating/approving one before asserting conformance.
