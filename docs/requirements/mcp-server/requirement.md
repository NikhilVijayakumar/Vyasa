# Requirement: MCP Server and Tool Contracts

- **Package:** `docs/requirements/mcp-server/`
- **Status:** Grilled — recommended answers await your confirmation
- **Roadmap phase:** P1
- **Owns:** FR-013, NFR-021, NFR-038, NFR-039
- **Grill log:** [grill-log.md](grill-log.md)
- **Diagrams:** [diagrams.md](diagrams.md)
- **Features:** [fr-013-mcp-interface.feature](features/fr-013-mcp-interface.feature)

## Knowledge References

Checked with the `knowledge-first` skill before writing.

- `knowledge/architecture/mcp-interface.md` — tool contracts, response envelope, error codes (§14), limits (§15)
- `knowledge/architecture/system-architecture.md` — MCP Adapter and entry points
- `knowledge/architecture/c4-system-views.md` — container and component views
- `knowledge/architecture/security-and-privacy.md` — MCP trust boundary and context returned to agents

## Intent

Coding agents reach Vyasa through a documented MCP interface that is read-only, validated, bounded, and stable. The contract, not the implementation, is what clients depend on, so it is versioned and tested as a contract.

## Scope

- **Included:**
  - Six read tools and the optional refresh tool decision.
  - Input validation, response shape, size caps, and error mapping.
  - Stdio transport and logging discipline.
  - Schema snapshot and versioning.
- **Excluded:**
  - Query semantics (project-query).
  - Network transports and authentication.
  - Sync and provider tools.
- **Deferred:**
  - HTTP transport, which would need authentication and a new threat model.
  - MCP resources and prompts.

## Requirements

### FR-013 — MCP Interface (P1)

Vyasa MUST expose its supported Phase 1 capabilities through a documented MCP interface.

#### Required tools

- `search_projects`
- `get_project`
- `get_project_context`
- `find_related_projects`
- `get_project_dependencies`
- `get_index_status`

An optional refresh tool may be provided to update the generated local index.

## Expected Behaviour

Observable behaviour is specified as Gherkin scenarios in `features/`. Scenarios tagged `@proposed` come from grill recommendations and become normative when the recommendation is confirmed.

- Clients can discover tools and their schemas (`fr-013` S1).
- Valid input gives the documented output; invalid input gives a structured error (S2, S3).
- Ordinary tools never modify repositories or maintained metadata (S6).

## Constraints

- Local stdio only; no network listener (NFD-007, SP-009).
- No tool accepts a filesystem path (SEC-026 onward).
- stdout carries protocol only; logs go to stderr and files.
- All repository-derived text is untrusted data (NFR-020).

## Acceptance Expectations

- Phase 1 criteria 5, 6 and 10 in `phase-acceptance-criteria.md`.
- A committed JSON snapshot of the tool list; changing it needs a version note.
- A stdio smoke test starts the server and lists the tools.

## Open Decisions

Accepted as open until you confirm the recommended direction in the grill log.

| Decision | Recommended direction | Grill |
|---|---|---|
| optional refresh | No agent-callable refresh in version 1; refresh is a CLI command, with an opt-in tool setting. | Q2 |
| NFD-007 | Stdio transport only. | Q3 |
| local paths | Local paths are omitted by default and can be enabled in configuration. | Q7 |
| errors | Tool failures use structured results with the documented codes, not protocol errors. | Q4 |

## Delivery

Proposed OpenSpec changes, each a set of vertical slices (`knowledge/practices/vertical-slices.md`):

- `be-mcp-skeleton`: stdio server that lists the tools and returns a status.
- `be-mcp-validation-and-errors`: Pydantic input models, error mapping, size cap.
- `be-mcp-contract-snapshot`: schema snapshot and contract tests.
- `be-mcp-readonly-connection`: read-only database connections for all tools.
