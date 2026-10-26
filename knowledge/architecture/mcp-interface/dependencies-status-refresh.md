---
type: Architecture
title: "MCP Interface: Dependencies, Index Status, and Refresh Tools"
description: Contracts for get_project_dependencies, get_index_status, and the optional refresh_index.
tags: [mcp, interface, contracts]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/mcp-interface.md
    title: MCP Interface
---

# MCP Interface: Dependencies, Index Status, and Refresh Tools

*Sections 11–13 of [MCP Interface](/architecture/mcp-interface.md).*

## 11. Tool 5 — `get_project_dependencies`

### 11.1 Purpose

Retrieve dependency information for a project and identify dependencies that resolve to other indexed projects.

### 11.2 Input Schema

| Parameter | Type | Required | Meaning |
|---|---|---:|---|
| `project_id` | string | Yes | Project to inspect |
| `direction` | string | No | `outgoing`, `incoming`, or `both`; default `outgoing` |
| `dependency_kinds` | string array | No | Direct, development, optional, or other supported categories |
| `include_external` | boolean | No | Include declared dependencies that do not resolve to indexed projects |
| `include_evidence` | boolean | No | Include supporting manifest references |
| `limit` | integer | No | Maximum dependency records |
| `cursor` | string | No | Opaque pagination cursor |

### 11.3 Output Semantics

The response must distinguish:

1. Declared dependency.
2. Resolved internal project relationship.
3. Unresolved dependency.
4. External dependency.
5. Unsupported dependency source.
6. Incomplete dependency assessment.

An unresolved dependency is not automatically an error. It may refer to an external package, a private package unavailable to the index, or a project not yet discovered.

### 11.4 Scope

Phase 1 covers dependencies extracted from supported local manifests.

The interface must not claim to provide a complete transitive dependency graph unless the relevant dependency resolution process has actually been implemented and verified.

---

## 12. Tool 6 — `get_index_status`

### 12.1 Purpose

Tell an agent what Vyasa currently knows about the index, when the information was last checked, and whether there are coverage limitations.

### 12.2 Input Schema

| Parameter | Type | Required | Meaning |
|---|---|---:|---|
| `include_scan_history` | boolean | No | Include recent scan summaries |
| `include_source_status` | boolean | No | Include local, shared, and remote source availability |
| `history_limit` | integer | No | Maximum scan history entries |

### 12.3 Response

The response should include:

- Index schema version.
- Index creation and update timestamps.
- Last successful scan time.
- Last attempted scan time.
- Number of indexed projects.
- Number of indexed repositories.
- Counts of current, stale, incomplete, and inaccessible records, where known.
- Latest scan outcome.
- Enabled detectors and versions.
- Configured root count, without exposing absolute paths by default.
- Phase capabilities enabled.
- Source synchronization status, when applicable.
- Outstanding errors or warnings.

### 12.4 Important Distinction

The index status must distinguish:

- When a scan was attempted.
- When a scan completed successfully.
- When a particular project was last inspected.
- When the shared registry was last synchronized.
- When a remote provider was last queried.

One global timestamp must not imply that every project's metadata is equally fresh.

---

## 13. Tool 7 — `refresh_index`

### 13.1 Purpose

Explicitly request a refresh of Vyasa's local generated index.

This tool is operational rather than a routine query.

### 13.2 Availability

The tool should be disabled by default for clients that require strict query-only access. It may be enabled through local configuration.

The server must make its availability and configured scope clear.

### 13.3 Input Schema

| Parameter | Type | Required | Meaning |
|---|---|---:|---|
| `scope` | string | No | `all`, `stale`, or `project`; default `stale` |
| `project_id` | string | Conditional | Required when `scope` is `project` |
| `detectors` | string array | No | Optional subset of supported detectors |
| `force` | boolean | No | Request revalidation rather than cache reuse |

The final schema must reject incompatible combinations, such as `scope: "project"` without a project ID.

### 13.4 Behaviour

The tool may:

- Discover eligible repositories within configured roots.
- Reinspect relevant files.
- Run selected supported detectors.
- Update Vyasa's local generated index.
- Record scan history.
- Report errors and incomplete results.

The tool must not:

- Edit canonical profiles.
- Modify project documentation.
- Generate or overwrite drafts during an ordinary refresh.
- Run repository scripts or tests.
- Perform Git fetch, checkout, or pull operations.
- Synchronize Google Sheets unless a separate explicit operation is designed.
- Trigger remote provider discovery as an implicit side effect.

### 13.5 Response

A refresh result should include:

- Run ID.
- Requested scope.
- Run status.
- Start and completion timestamps, where available.
- Projects discovered, inspected, updated, skipped, and failed.
- Detector errors.
- Whether the index is complete for the requested scope.
- Any remaining stale observations.

### 13.6 Execution Model

A refresh may take longer than a normal query.

The implementation must determine whether the selected MCP transport and SDK support the required progress or cancellation behaviour. Until long-running operation support is verified, the scanner must use bounded scopes or return a clear operational error rather than pretending the scan completed.

Concurrent refreshes must be controlled according to the indexing and SQLite concurrency design.
