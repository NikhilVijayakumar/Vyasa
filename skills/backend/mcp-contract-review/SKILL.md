---
name: mcp-contract-review
description: >-
  Reviews Vyasa MCP tool contracts: read-only query tools, validated and
  bounded inputs, no hidden side effects, stable error codes and response
  shapes. Use whenever an MCP tool, its parameters, its Pydantic models, or
  its response or error shape is added or changed.
---

# MCP Contract Review

Source of truth: `knowledge/architecture/mcp-interface.md`. This skill is the
checklist; the document wins on any conflict. For security-specific review
of the server (transport, injection, data exposure), also run
`mcp-server-review`.

## Checklist

1. **Read-only.** No tool creates, edits, or deletes project-owned metadata
   or repository files. An explicit refresh may update only Vyasa's own index
   and scan history (§2.2).
2. **No hidden expensive work.** A query never triggers a scan, a Sheets
   sync, or a remote API call. Queries report index freshness instead (§2.5,
   §6.6).
3. **Validated input.** Every parameter has a Pydantic type, allowed values,
   and bounds. Unknown or incompatible input returns `INVALID_ARGUMENT`.
4. **Bounded output.** Every list has a `limit` with a documented default
   and maximum (e.g. default 20, max 100) and pagination where needed (§15.3).
5. **Unknown vs empty.** Responses distinguish an unknown value from an empty
   collection; a missing property never means "does not exist" (§6.3).
6. **Evidence-aware.** Values carry source and evidence where available, and
   say whether they were declared, detected, synced, provider-reported, or
   unresolved (§2.3, §6.4).
7. **Stable errors.** Only the documented codes: `INVALID_ARGUMENT`,
   `NOT_FOUND`, `INDEX_UNAVAILABLE`, `INDEX_INCONSISTENT`,
   `CAPABILITY_UNAVAILABLE`, `SOURCE_UNAVAILABLE`, `SCAN_INCOMPLETE`,
   `OPERATION_IN_PROGRESS`, `INTERNAL_ERROR`. Messages never expose stack
   traces, credentials, or local paths the caller should not see (§14).
8. **Stable identifiers.** IDs are opaque; never derived from names or paths
   (§6.2).
9. **Compatible evolution.** Add optional fields rather than change existing
   ones; bump `schema_version` on any breaking change and record it in the
   change's `api-contract.md` (§2.4).
10. **Phase-gated.** A tool for a later phase returns
    `CAPABILITY_UNAVAILABLE` until that phase is enabled (§4.3).

## Verification

Each tool has contract tests for: valid input, each validation failure,
limit maximum, unknown vs empty, and every error code it can return. See
`api-contract-testing`.

## Output

One line per checklist item: pass / fail / not applicable, with `file:line`
and the fix for each failure.
