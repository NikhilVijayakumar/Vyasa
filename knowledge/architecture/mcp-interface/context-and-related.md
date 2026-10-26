---
type: Architecture
title: "MCP Interface: Project Context and Related Projects Tools"
description: Contracts for get_project_context and find_related_projects.
tags: [mcp, interface, contracts]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/mcp-interface.md
    title: MCP Interface
---

# MCP Interface: Project Context and Related Projects Tools

*Sections 9–10 of [MCP Interface](/architecture/mcp-interface.md).*

## 9. Tool 3 — `get_project_context`

### 9.1 Purpose

Provide a compact, structured briefing that an agent can use while working in another repository.

This tool is the primary cross-project knowledge interface.

### 9.2 Input Schema

| Parameter | Type | Required | Meaning |
|---|---|---:|---|
| `project_id` | string | Yes | Stable Vyasa project identifier |
| `sections` | string array | No | Requested context sections |
| `max_evidence_items` | integer | No | Maximum evidence references per section |
| `max_related_projects` | integer | No | Maximum related projects to include |
| `include_stale` | boolean | No | Include stale observations with warnings |

Supported section identifiers should include:

- `overview`
- `repositories`
- `technologies`
- `architecture`
- `documentation`
- `standards`
- `agent_instructions`
- `tests`
- `dependencies`
- `relationships`
- `evidence`
- `freshness`

The implementation must document which sections are available in each phase.

### 9.3 Context Construction

Context construction is deterministic.

It assembles supported observations and declarations into a useful structure. It does not use an LLM to invent a narrative or infer undocumented architecture.

For example, if a repository contains a Kotlin Gradle manifest, that evidence may support a Kotlin/build-tool observation. It does not establish the project's architectural pattern unless a supported source explicitly declares that pattern.

### 9.4 Response

```json
{
  "project": {
    "project_id": "proj_001",
    "display_name": "Example Project"
  },
  "overview": {
    "purpose": {
      "value": "Documentation compilation",
      "status": "declared",
      "evidence": []
    }
  },
  "technologies": [],
  "documentation": {
    "readme": {
      "status": "observed",
      "present": true,
      "evidence": []
    },
    "openspec": {
      "status": "unknown",
      "present": null,
      "evidence": []
    }
  },
  "relationships": [],
  "warnings": [],
  "freshness": {
    "status": "current",
    "last_successful_scan": "2026-10-26T09:55:00Z"
  }
}
```

This is illustrative. The real response must use consistent field schemas and avoid asserting `present: false` when inspection was incomplete.

### 9.5 Context Safety

- Include only information needed for the requested sections.
- Bound the response size.
- Do not return credentials or secret values.
- Do not return entire instruction files by default.
- Use evidence references so the calling agent can inspect relevant sources through its authorized repository tools.
- Mark stale and conflicting information explicitly.

---

## 10. Tool 4 — `find_related_projects`

### 10.1 Purpose

Discover other projects that may provide reusable code, architecture, tooling, or documentation.

### 10.2 Input Schema

| Parameter | Type | Required | Meaning |
|---|---|---:|---|
| `project_id` | string | Yes | Project to compare against |
| `relationship_types` | string array | No | Relationship types to include |
| `technologies` | string array | No | Filter or focus matching on technologies |
| `include_candidates` | boolean | No | Include unconfirmed relationship candidates |
| `limit` | integer | No | Maximum results, default 10, maximum 100 |
| `cursor` | string | No | Opaque pagination cursor |

Supported relationship types may include:

- `depends_on`
- `uses_library`
- `shared_technology`
- `related_project`
- `same_logical_project`
- `potential_duplicate`

These types have different meanings and must not be treated as interchangeable.

### 10.3 Relationship Evidence

Each result should provide:

- Related project ID and display name.
- Relationship type.
- Relationship status: confirmed, candidate, rejected, or unknown.
- Deterministic matching rule or reason.
- Supporting evidence references.
- Relevant freshness information.

### 10.4 Deterministic Matching

The initial implementation may use rules such as:

- A declared dependency resolves to another indexed project through a known package or repository identity.
- Two projects explicitly identify the same logical project.
- Two projects declare the same normalized technology.
- Two repositories have sufficiently strong identity evidence suggesting a duplicate.

Shared technology alone should produce a weak relationship candidate, not a claim that one project can directly reuse the other's implementation.

### 10.5 Ranking

If results are ranked, the ranking algorithm must be deterministic and documented.

The system must not invent confidence percentages. If a numeric score is introduced later, its scale and interpretation must be defined and tested.
