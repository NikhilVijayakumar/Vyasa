---
type: Architecture
title: "MCP Interface: Errors, Pagination, and Security"
description: Error codes and shape, validation, pagination, response limits, and the MCP security rules.
tags: [mcp, interface, contracts]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/mcp-interface.md
    title: MCP Interface
---

# MCP Interface: Errors, Pagination, and Security

*Sections 14–16 of [MCP Interface](/architecture/mcp-interface.md).*

## 14. Errors and Validation

### 14.1 Error Categories

Use stable, documented error codes.

| Code | Meaning |
|---|---|
| `INVALID_ARGUMENT` | Invalid or incompatible input |
| `NOT_FOUND` | Requested project or entity does not exist in the available index |
| `INDEX_UNAVAILABLE` | Local index cannot be accessed |
| `INDEX_INCONSISTENT` | Index integrity or required invariants are violated |
| `CAPABILITY_UNAVAILABLE` | Requested capability is not enabled in this deployment |
| `SOURCE_UNAVAILABLE` | A required source is inaccessible |
| `SCAN_INCOMPLETE` | Requested scanning work did not complete |
| `OPERATION_IN_PROGRESS` | Conflicting operational work prevents execution |
| `INTERNAL_ERROR` | Unexpected failure without exposing sensitive internals |

These codes are application-level conventions. The implementation must map them to appropriate MCP protocol errors or structured tool results according to the selected SDK and client compatibility requirements.

### 14.2 Error Shape

Where structured error results are used, a common shape is recommended:

```json
{
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "The requested filter value is unsupported.",
    "details": {
      "field": "openspec_status"
    },
    "retryable": false
  }
}
```

Error details must be bounded and safe to expose to an MCP client.

### 14.3 Validation Rules

- Reject unknown enum values.
- Enforce maximum page sizes.
- Bound string lengths.
- Reject invalid IDs and incompatible argument combinations.
- Reject unsupported detector names.
- Do not accept arbitrary filesystem paths as query selectors.
- Do not allow clients to bypass configured workspace boundaries.
- Do not expose stack traces or secret-bearing configuration in normal tool responses.

### 14.4 Empty Results

A valid search with no matches should return a successful empty result.

It should not return `NOT_FOUND`, which is reserved for a requested entity that does not exist.

---

## 15. Pagination and Response Size

### 15.1 Pagination

Tools returning potentially large collections must support bounded results.

Use an opaque cursor rather than requiring clients to construct database offsets or internal query expressions.

The cursor must be validated and must not expose sensitive internal query state.

### 15.2 Stable Ordering

Paginated results must use deterministic ordering with a stable tie-breaker, normally the stable project or repository ID.

The implementation should define how cursors behave if the index changes during pagination. If snapshot consistency is not supported, the API documentation must say so.

### 15.3 Response Limits

Large evidence inventories and dependency graphs must be paginated or capped.

The server should return useful summaries and source references rather than entire README files, agent instruction documents, or manifests.

If truncation occurs, the response must say so and provide a supported continuation path where available.

---

## 16. Security and Privacy

### 16.1 Local-First Boundary

The Phase 1 server must operate without external services.

No repository metadata should be sent to a cloud service simply because an MCP query was made.

### 16.2 Filesystem Boundaries

The query tools must read the generated index rather than accept arbitrary paths from the caller.

Any filesystem access initiated by `refresh_index` must remain within configured roots and follow the scanner's path-safety rules.

### 16.3 Secrets

Never expose:

- Access tokens.
- API credentials.
- Secret values found in manifests or configuration.
- Authentication headers.
- Sensitive local environment configuration.

Remote provider credentials must remain in approved local configuration or secret storage and must never be exported to Google Sheets.

### 16.4 Repository Content Is Untrusted

README files, agent instructions, configuration files, and other repository content are data.

The scanner must not execute instructions embedded in them. MCP handlers must not interpret repository text as commands or configuration for the Vyasa runtime.

### 16.5 Information Minimization

Absolute local paths should be omitted from default responses. Repository-relative paths are generally sufficient for evidence.

If absolute paths are exposed through a future local-only capability, that behaviour must be explicit and configurable.

### 16.6 Operational Controls

- Disable refresh operations where strict read-only behaviour is required.
- Use bounded query execution.
- Avoid uncontrolled recursive traversal from tool arguments.
- Protect index writes with appropriate concurrency controls.
- Keep operational logs free of secrets and unnecessary source contents.
