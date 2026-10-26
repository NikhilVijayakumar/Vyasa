---
type: Architecture
title: "MCP Interface: Search and Project Details Tools"
description: Contracts for search_projects and get_project.
tags: [mcp, interface, contracts]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/mcp-interface.md
    title: MCP Interface
---

# MCP Interface: Search and Project Details Tools

*Sections 7–8 of [MCP Interface](/architecture/mcp-interface.md).*

## 7. Tool 1 — `search_projects`

### 7.1 Purpose

Find projects across the available index using text search and structured filters.

Example user questions:

- "Which projects use CrewAI?"
- "Find the projects that use React and TypeScript."
- "Which projects have OpenSpec configured?"
- "Find projects related to documentation tooling."
- "Show projects that need documentation review."

### 7.2 Input Schema

| Parameter | Type | Required | Meaning |
|---|---|---:|---|
| `query` | string | No | Text to match against indexed project metadata |
| `technologies` | string array | No | Technology identifiers or supported names |
| `languages` | string array | No | Programming languages |
| `lifecycle_status` | string array | No | Requested lifecycle states |
| `tracking_level` | string array | No | Requested tracking levels |
| `documentation_status` | string | No | Filter by supported documentation state |
| `openspec_status` | string | No | Filter by supported OpenSpec state |
| `agent_instructions_present` | boolean | No | Filter by instruction-file detection |
| `tests_present` | boolean | No | Filter by test-indicator detection |
| `freshness` | string | No | Filter by freshness state |
| `sources` | string array | No | Restrict results to supported source categories |
| `limit` | integer | No | Page size; default 20, maximum 100 |
| `cursor` | string | No | Opaque pagination cursor |

The exact filter vocabularies must be defined in the public schema. Unknown filter values must produce a validation error rather than silently changing the search.

### 7.3 Search Semantics

- Multiple filters are combined using documented rules; the initial recommendation is AND between filter groups and OR within a multi-value filter.
- Text matching must be deterministic.
- Technology aliases should normalize to stable technology identifiers where supported.
- Search must use indexed information and must not scan every repository during a query.
- Ranking, if used, must be deterministic and documented.
- Results must indicate whether matching metadata is stale or incompletely assessed.

The query implementation must not infer that two projects are related merely because they share a keyword.

### 7.4 Response

Each result should include a compact summary:

```json
{
  "projects": [
    {
      "project_id": "proj_001",
      "display_name": "Example Project",
      "purpose": {
        "value": "Documentation compilation",
        "status": "declared"
      },
      "languages": [
        {
          "value": "Rust",
          "status": "observed"
        }
      ],
      "technologies": [],
      "lifecycle_status": "active",
      "details_status": "complete",
      "freshness": "current"
    }
  ],
  "page": {
    "limit": 20,
    "next_cursor": null,
    "has_more": false
  }
}
```

This example illustrates the logical contract. Empty collections, statuses, and optional fields must be represented consistently by the actual schema.

### 7.5 Search Limitations

Search results are summaries, not complete project records.

The client should call `get_project` for a detailed record or `get_project_context` for an evidence-backed briefing.

---

## 8. Tool 2 — `get_project`

### 8.1 Purpose

Retrieve the structured record for one known project.

### 8.2 Input Schema

| Parameter | Type | Required | Meaning |
|---|---|---:|---|
| `project_id` | string | Yes | Stable Vyasa project identifier |
| `include_repositories` | boolean | No | Include associated repository records |
| `include_technologies` | boolean | No | Include normalized technology observations |
| `include_documentation` | boolean | No | Include documentation and standards indicators |
| `include_evidence` | boolean | No | Include evidence references |
| `include_relationships` | boolean | No | Include known project relationships |

Optional flags default to false unless a different default is specified in the published schema. The base project fields must remain sufficient to identify the project and communicate its status.

### 8.3 Response Sections

A project record may include:

- Stable project ID.
- Display name.
- Declared purpose and other supported metadata.
- Lifecycle and tracking information, where available.
- Associated repositories.
- Technologies and languages.
- Documentation indicators.
- Recognized agent instruction files.
- Test indicators.
- Project details status.
- Source provenance.
- Last successful observation timestamps.
- Freshness and unresolved conflicts.

Local checkout paths must not be returned by default. If a future local-only option exposes them, it must be explicitly configured and clearly scoped to the local client.

### 8.4 Missing Project

An unknown project ID produces a `NOT_FOUND` error.

The tool must not silently return a different project with a similar name.
