# Design: be-profile-context

## 1. Overview

### Purpose
Give agents the evidence and the comparison through the existing read paths, and reuse the scan pipeline for unindexed repositories.

### Scope
A pure differences function, a context builder over `get_project`, an MCP tool, an in-memory index helper, an enrichment function, and a command.

### Design Principles
One bundle from one function. Compare only where the observation supports a claim. Reuse, do not duplicate, the scan. Write nothing. Fixed text only.

## 2. Context and Constraints

### Current State
`get_project` assembles identity, checkouts with `languages`, `composition`, `markers`, `frameworks`, the profile, and candidates. `scan_workspace` discovers, attaches results with the private `_with_languages`, and stores with `store_run`. `open_index` creates files and applies migrations. The CLI has only `scan`. The MCP server exposes four read tools.

### Constraints
- Technical constraints: Python 3.12+, standard library only (`sqlite3` in memory).
- Security and privacy constraints: no absolute path or file text in the bundle; no writes; fixed workflow text.
- Performance and reliability constraints: one walk of one repository; bounded as the normal scan.
- Compatibility and migration constraints: additive.
- Operational constraints: the command runs without a configuration file or index.

### Existing Decisions and Conventions
Observation freshness without query-time I/O, read-only access policy, partial results never imply absence, MCP omits local paths by default.

### Knowledge References
- `knowledge/decisions/profile-context-for-agents.md` — bundle, sources, differences.
- `knowledge/decisions/profile-schema-v2-full-template.md` — declared fields.
- `knowledge/decisions/observation-freshness-without-query-time-io.md` — stored data only for queries.
- `knowledge/decisions/partial-results-never-imply-absence.md` — absence rules.

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| Context bundle | `profile_context` extends `get_project` data | Contract tests through the query layer |
| MCP tool | `get_profile_context` in the server | MCP tests and the snapshot |
| Command | `live_context` and `cli.main` | CLI tests on real temporary repositories; before/after hash of repository and data directory |
| No absolute path or text | `include_paths=False`; fixed finding details | Serialization tests |
| Differences | `differences` pure function | Unit tests on dictionaries |
| No agent, no write | no process or file APIs used | Hash tests; review |
| Workflow | `WORKFLOW` constant | Equality test |

## 4. Architecture and Design

### Architectural Approach
`vyasa.application.profile_context` holds `differences`, `profile_context(connection, project_id)`, and `live_context(path)`. `profile_context` calls `get_project`, extends each checkout with `differences(checkout, declared)`, and adds `source` and `workflow`. `live_context` runs `discover_repositories(path)`, takes the candidate whose path equals the resolved path, attaches results with the public `enrich_run`, stores the run in an `open_memory_index()` connection with `store_run`, calls `profile_context` on the one project, sets `source.kind = live_scan`, nulls the project id, and closes the connection.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `vyasa.application.profile_context` | differences, bundle, live path, workflow, `NotAProject` | query, scan, discovery |
| `vyasa.application.indexing.scan` | `enrich_run` (public, was `_with_languages`) | scanning |
| `vyasa.adapters.sqlite.database` | `open_memory_index` | stdlib |
| `vyasa.adapters.cli.main` | `profile-context` command, exit codes | application |
| `vyasa.adapters.mcp.server` | `get_profile_context` tool | application |

### Interfaces and Contracts
See `api-contract.md`.

### Key Workflows
Tool: validate → `get_project` → differences per checkout → envelope. Command: resolve path → discover → enrich → store in memory → bundle → print JSON → close.

## 5. Data and State Management

Differences take the checkout's `languages`, `frameworks`, and `markers` dictionaries (as `get_project` returns them) and the declared values `{name: value}` taken from the profile's `declared` entries through the accessor. Rules: a language item matches a detected label case-insensitively over both statuses; "complete" means the observation's `status` is `complete`; the language vocabulary is the registry-independent set of shipped language and manifest labels; a framework item matches a registry key or name case-insensitively; version 1 `technologies` items are tried as language, then technology, else not comparable; ubiquitous technologies are never reported as undeclared; OpenSpec uses the `openspec_directory` marker; agent instruction paths are compared case-insensitively against the stored `agent_instructions` paths and, when more matches exist than stored, no absence is claimed. Findings are sorted by code, then subject. `detail` texts are a fixed table.

The in-memory index is `sqlite3.connect(":memory:", isolation_level=None)` with the same pragmas and migrations as `open_index`. The writer lock is taken inside it as usual and is discarded with the connection.

## 6. Error Handling and Resilience

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| Path missing or not a directory | exit 2 with a message | Caller corrects |
| Not a project root | exit 2 with a fixed message | Run in a repository root |
| Detection fails for the checkout | Failed observation; the bundle says not assessed | Rerun |
| Unexpected exception | exit 4, generic message, no repository text | Report |

## 7. Security and Privacy

Trust boundary as in the contract. The command opens no file for writing and creates no temporary file. The bundle excludes absolute paths and file text by construction (it is built from `get_project` without `include_paths` and from fixed texts). The workflow is a constant. No material privacy impact beyond the existing tools.

## 8. Quality Attributes

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Honesty | Absence only from complete observations | Rules gated on `status == complete` | Partial fixtures |
| Consistency | Live and stored bundles agree | One builder over the same pipeline | Comparison test |
| Safety | Nothing written, no agent | No write APIs | Hash tests |
| Determinism | Stable output | Sorted findings and fixed texts | Repeat-run test |

## 9. Testing and Verification Strategy

### Behavioral Verification
One test per scenario in the spec.

### Test Strategy
Unit tests for `differences` on dictionaries; contract tests for `profile_context` on a real temporary index; MCP tests for the tool and the snapshot; CLI tests on real temporary repositories with `git init`, hashing the repository and a data directory before and after.

### Testability
`profile_context` takes a clock; the command's streams and environment are injectable as in `scan`.

### Verification Evidence
`python -m pytest`, `python scripts/verify_workflows.py`; skips are reported.

## 10. Implementation and Migration Considerations

### Implementation Order
Differences, then the stored bundle and tool, then the in-memory index and live path, then the command.

### Migration and Rollout
None.

### Documentation and Operations
Update the README usage and `knowledge/log.md`.

## 11. Architecture Decision Checkpoint

- **New ADR required:** Yes — `knowledge/decisions/profile-context-for-agents.md`; see `adr.md`.

## 12. Risks, Trade-offs, and Open Questions

### Risks
Per-checkout differences against one shared profile can repeat across checkouts; accepted.

### Trade-offs
Reusing `get_project` keeps one shape but returns review candidates an agent may not need; they are small.

### Open Questions
None.

## 13. Traceability

Proposal, spec, and contract share the change ID `be-profile-context`; requirement package `docs/requirements/project-profile/`.

## 14. Design Readiness Review

- [x] Requirements are traced to design elements and checks.
- [x] Boundaries, failure handling, and the trust boundary are stated.
- [x] The architecture decision checkpoint is answered.
- [x] Risks and trade-offs are visible.

**Status:** Draft
