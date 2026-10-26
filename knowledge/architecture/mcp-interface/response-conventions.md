---
type: Architecture
title: "MCP Interface: Shared Response Conventions"
description: The response envelope, identifiers, missing values, evidence objects, observation status, and freshness.
tags: [mcp, interface, contracts]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/mcp-interface.md
    title: MCP Interface
---

# MCP Interface: Shared Response Conventions

*Sections 6 of [MCP Interface](/architecture/mcp-interface.md).*

## 6. Shared Response Conventions

### 6.1 General Structure

Each tool returns structured data appropriate to its purpose. A conceptual response envelope is:

```json
{
  "schema_version": "1",
  "data": {},
  "meta": {
    "generated_at": "2026-10-26T10:00:00Z",
    "index_version": 12,
    "freshness": "current"
  }
}
```

This is a conceptual envelope, not a requirement that every MCP result use an identical wrapper. The final implementation should follow the SDK's supported structured-content mechanism and retain a consistent logical shape.

Timestamps use ISO 8601 with an explicit timezone. Examples in this document are illustrative.

### 6.2 Stable Identifiers

Project and repository IDs are opaque stable identifiers.

Clients must not construct IDs from display names or local paths. IDs must remain stable across ordinary rescans and directory renames when the identity policy resolves the same logical entity.

### 6.3 Missing Values

The interface must distinguish an unknown value from an empty collection.

Examples:

- Unknown project purpose: status `unknown`, with no asserted purpose.
- No supported dependencies detected after complete inspection: an empty dependency collection with an appropriate assessment status.
- Dependencies not assessed: an explicit status indicating that assessment was incomplete or unavailable.

A missing JSON property must not be interpreted as proof that the value does not exist.

### 6.4 Evidence Objects

Where applicable, evidence should use a consistent shape:

```json
{
  "source_type": "repository_file",
  "source_ref": {
    "repository_id": "repo_123",
    "path": "pyproject.toml",
    "field": "project.dependencies"
  },
  "observed_at": "2026-10-26T09:55:00Z",
  "revision": "abc123",
  "detector": {
    "id": "python_manifest",
    "version": "1"
  }
}
```

The `revision` may be null when no reliable revision is available. Line ranges and fingerprints may be included when supported.

The server must not fabricate evidence fields that it cannot establish.

### 6.5 Observation Status

The interface should reuse the statuses defined in `scanning-and-evidence.md`:

- `observed`
- `declared`
- `not_detected`
- `unknown`
- `unsupported`
- `inaccessible`
- `stale`
- `conflicting`

The final Pydantic models must define allowed values and optional fields explicitly.

### 6.6 Freshness

At the index level, use a documented vocabulary such as:

- `current` — no known invalidation is pending for the requested information.
- `stale` — relevant indexed observations may no longer match their sources.
- `partial` — the latest relevant inspection was incomplete.
- `unknown` — freshness cannot be established.

These are proposed index-level states and are distinct from individual observation statuses.
