# Change Proposal: be-mcp-server

## Why

The index and query layer exist, but no coding agent can reach them. Vyasa needs a local stdio MCP server that exposes the query functions as read-only tools with structured errors and a committed tool contract, so an agent can discover and query indexed projects (phase 1 completion criterion).

## What Changes

- **mcp-server**: a new capability. A stdio-only MCP server (`vyasa-mcp`) registering `search_projects`, `get_project`, and `get_index_status`; each call opens the index read-only; errors are structured results with the documented codes; the tool list is pinned by a committed snapshot; the SDK is an optional extra.

## 1. Problem and Motivation

### Current Situation

`vyasa.application.query` answers three questions as plain functions. There is no server, entry point, or MCP dependency.

### Problem

An agent cannot call Vyasa. FR-013 requires a documented, validated, bounded, stable MCP interface.

### Evidence

- Verified: official `mcp` 2.3.0 installs into the project `.venv` (system Python is externally managed); the 2.x API is `mcp.server.mcpserver.MCPServer` with an in-memory `Client`.
- Verified: a tool may return `CallToolResult` with `structured_content` and `is_error`; SDK type validation failures come back as tool errors with text only.
- Verified: the owner approved adding the SDK as an optional extra and installing it (2026-10-27) and asked to proceed on the recommended directions of the mcp-server grill log; they remain recommendations.

## 2. Desired Outcome

### Goals

- [ ] A stdio server that lists and serves three read tools.
- [ ] Structured results in the shared envelope; structured errors with codes.
- [ ] Read-only access and no local paths in any result.
- [ ] A committed tool snapshot and a stdio smoke test.

### Team Focus

MCP tool contracts, trust boundary (agent input is untrusted), read-only enforcement, stdout discipline, and the optional-extra packaging.

### Success Criteria

- [ ] A real subprocess started with `python -m vyasa.adapters.mcp` answers `tools/list` and a tool call over stdio.
- [ ] Changing a tool's schema fails the snapshot test until the snapshot is regenerated.
- [ ] The core imports and its tests pass with the `mcp` package absent.
- [ ] No tool accepts a path, and results hold none.

## 3. Scope

### In Scope

- `vyasa.adapters.mcp` (server, entry point), `[mcp]` extra, `vyasa-mcp` script.
- Three tools; error mapping; snapshot; smoke and in-process tests.

### Out of Scope

- `get_project_context`, `find_related_projects`, `get_project_dependencies` (no data yet); they are not registered, so none returns invented data.
- Any refresh or scan tool, HTTP/SSE transports, resources and prompts, authentication.
- A configuration setting for paths: results never include paths for now.
- Client configuration documentation beyond a README note.

### Constraints

Local stdio only; stdout carries protocol only; Python 3.12+; `mcp>=2,<3`.

## 4. Stakeholders and Impact

- **Primary stakeholders:** coding agents; the owner.
- **Affected components or capabilities:** new `vyasa.adapters.mcp`; `pyproject.toml`; reads `vyasa.application.query`.
- **Dependencies:** `be-project-query-basics` (merged); the `mcp` extra.
- **Compatibility considerations:** new surface; tool names follow `knowledge/architecture/mcp-interface.md`.

## 5. Proposed Direction

`build_server(index_file)` returns an `MCPServer` whose tools open a read-only connection per call, call the query function, and return `CallToolResult` with the envelope as `structured_content` and a JSON text copy. `IndexStoreError` becomes `is_error=True` with `{"error": {"code", "message"}}`. The index file comes from `index_path()` (`VYASA_HOME`). Considered: returning plain dicts (no structured content for errors) and a long-lived connection (stale reads, shared state).

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | stdio server lists three tools | discoverable | Must |
| REQ-002 | Results are structured, read-only | envelope, no writes | Must |
| REQ-003 | Failures are structured | codes, no protocol errors | Must |
| REQ-004 | No paths in or out | trust boundary | Must |
| REQ-005 | Contract pinned | snapshot test | Must |
| REQ-006 | SDK optional | core works without it | Must |

## 7. Risks and Open Questions

### Risks

| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| SDK 2.x API shifts | Breakage on upgrade | Pin `mcp>=2,<3`; snapshot and smoke tests |
| SDK argument-type errors lack codes | Agent sees text only | Documented; domain validation covers values and ranges |
| Missing index file | Every call errors | `INDEX_UNAVAILABLE` with a clear message |

### Assumptions

- Recommended mcp-server directions (stdio only, structured errors, paths omitted) are accepted.

### Open Questions

- [ ] Whether argument-type errors should be mapped to `INVALID_INPUT` by loosening tool parameter types.

## 8. Acceptance Summary

- [ ] Every spec scenario has a test.
- [ ] `pytest` (with and without the extra), `verify_workflows.py`, `verify_knowledge.py`, `openspec validate` pass.

## 9. Traceability

- **OpenSpec Change ID:** `be-mcp-server`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-mcp-server`
- **Requirement package:** `docs/requirements/mcp-server/requirement.md`
- **Knowledge references:**
  - `knowledge/architecture/mcp-interface.md` — tools, envelope, errors
  - `knowledge/decisions/stdio-only-mcp-transport.md` — stdio only
  - `knowledge/decisions/mcp-local-paths-omitted-by-default.md` — paths omitted
  - `knowledge/decisions/optional-extras-for-integrations.md` — SDK as an extra
  - `knowledge/decisions/explicit-tools-disabled-by-default.md` — no refresh tool
- **Related issues or references:** None
- **Related existing specifications:** `openspec/specs/project-query`, `openspec/specs/local-index`
- **Related ADRs:** `knowledge/decisions/stdio-only-mcp-transport.md`

## 10. Readiness Review

- [x] The problem and motivation are clear.
- [x] Goals and success criteria are observable.
- [x] Scope and non-goals are explicit.
- [x] Important stakeholders, constraints, and dependencies are identified.
- [x] Assumptions and unresolved questions are visible.
- [x] The proposing team is identified and its focus and skills applied.
- [x] The proposal is consistent with existing specifications and project conventions.
- [x] Significant ambiguities have been challenged and resolved, or explicitly recorded.
- [x] The change has a stable OpenSpec ID and follows the project's Git discipline.

**Status:** Ready for specification and design
