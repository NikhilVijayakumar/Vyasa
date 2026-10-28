# Design: be-get-project-dependencies

## 1. Overview

### Purpose
Answer "what does this project depend on, and what depends on it" from the index, with the package name each manifest declares as the only linking evidence.

### Scope
Capture the declared name in the existing parsers, store it, and add one read-only query and MCP tool. No new scan pass, no new file read.

### Design Principles
Evidence or nothing: an edge exists only when two manifests state it. Absence is never inferred from a partial, skipped, or older observation. Reuse the stored dependencies and the latest-observation rule that `get_project` already uses. No new dependency.

## 2. Context and Constraints

### Current State
Migration 0009 stores per-manifest rows (`checkout_manifests`) and direct dependencies (`checkout_dependencies`) on the observation of the same walk. Parsers return `ParsedManifest(dependencies, skipped, workspace)` and drop the package name. `projects.checkout_frameworks` reads the latest observation of a checkout.

### Constraints
Read-only tool; repository content untrusted; Python 3.12 standard library; results bounded; Windows and Linux.

### Existing Decisions and Conventions
Latest observation per checkout; honest statuses (`complete`, `partial`, `not_assessed`); opaque project ids; envelope `{schema_version, data, meta}`; structured errors; no local paths in results.

### Knowledge References
- `knowledge/decisions/internal-dependencies-by-declared-package-name.md` — the rule.
- `knowledge/decisions/framework-detection-from-manifests.md` — manifests, scopes, states.
- `knowledge/decisions/partial-results-never-imply-absence.md` — coverage wording.
- `knowledge/concepts/evidence-and-provenance.md` — each edge names its sources.

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| Declared names recorded | `declared_name` on `ParsedManifest`; parsers for pyproject, package.json, Cargo.toml, go.mod; stored with the manifest row | Unit tests on text per ecosystem; persistence test on a real database file |
| Dependencies with evidence | query layer function reading `checkout_dependencies` of active checkouts' latest observation | Contract tests on a seeded index |
| Internal only by exact name | one SQL join on `(ecosystem, normalized name)` against `checkout_manifests.declared_name`, excluding the project itself | Contract tests: internal, ambiguous, external, other ecosystem, normalization, missing checkout |
| Dependents | the same join in reverse, limit 101 to detect truncation, plus a count | Contract tests with 101 dependents |
| Coverage | derived from manifest rows, observation status, nested counts, and a count of other projects unchecked | Contract tests per coverage state |
| Read-only and declared | tool wrapper with read-only annotations; snapshot regenerated | MCP tests and the committed snapshot |

## 4. Architecture and Design

### Architectural Approach
Same layering as the existing tools: pure parsing in `domain`, scan storage in `application/indexing` and `adapters/sqlite`, queries in `application/query.py` over `adapters/sqlite/projects.py`, MCP declaration in `adapters/mcp/server.py`.

### Components and Responsibilities
- `domain/manifests.py`: each parser also returns a declared name; `_bounded` enforces text, length, and normalization (`normalize(ecosystem, name)`); an unparsed manifest has none.
- `domain/frameworks.py`: `ParsedManifest.declared_name` (default None, so existing callers are unchanged).
- `application/scanning/frameworks.py` and `application/indexing/store.py`: carry the name to the manifest row.
- `adapters/sqlite/migrations/0010_declared_names.sql`: nullable column and index.
- `adapters/sqlite/projects.py`: `project_dependencies(connection, project_id)` returning dependencies, dependents, and coverage inputs.
- `application/query.py`: `get_project_dependencies` validating the id and shaping the envelope.
- `adapters/mcp/server.py`: the tool declaration and description.

### Interfaces and Contracts
See `api-contract.md` §3.

### Key Workflows
Scan: parse manifest, keep the name, store it with the row in the observation's transaction. Query: resolve the project, load its active checkouts' latest observation, read its dependencies, resolve each against the declared names of other projects' latest observations, then run the reverse join for dependents.

## 5. Data and State Management

One nullable column and one index. The latest observation of each active checkout is the only data used on both sides; older observations and missing checkouts are ignored. No state is written by the tool. A rescan makes a new observation, so names appear without a separate backfill.

## 6. Error Handling and Resilience

Invalid or unknown id: structured errors as in `get_project`. A missing index: `INDEX_UNAVAILABLE`. A partial or not-assessed observation, an unparsed manifest, or missing names are coverage facts, not errors. If a target project has an observation without recorded names, it cannot be a target and is counted as unchecked rather than treated as having no such package.

## 7. Security and Privacy

The declared name is untrusted text: bounded to 214 characters, stored as data, bound as a SQL parameter, never used as a path or command, and returned only inside the structured result. The tool takes only an opaque id and returns no local path, file text, or credential. `code-review-security` and `mcp-contract-review` are run over the parsers, the query, and the declaration.

## 8. Quality Attributes

Deterministic ordering with explicit tie-breaks; bounded output (200 stored dependencies per manifest, at most 100 dependents); the join uses the new index. Maintainability: one query function and one tool. Observability: coverage states what is known.

## 9. Testing and Verification Strategy

### Behavioral Verification
Each specification scenario maps to a test: parser text tests for names; persistence tests on a real temporary SQLite file; contract tests on a seeded index; an MCP test and the regenerated snapshot; an executable check against a scanned fixture workspace.

### Test Strategy
Unit (parsers), integration (scan to index, migration from every earlier version via the existing chain test), contract (query), and MCP layer. No test touches the network.

### Testability
The query takes a connection, so tests use an in-memory or temporary index; parsers are pure.

### Verification Evidence
Commands and outcomes are recorded in `tasks.md`.

## 10. Implementation and Migration Considerations

### Implementation Order
Parsers and storage first (names recorded), then the query, then the MCP declaration, then documentation.

### Migration and Rollout
`0010_declared_names.sql` through the existing forward-only mechanism with its backup. Run `vyasa scan` to record names; until then coverage says so.

### Documentation and Operations
README MCP section and `docs/setup.md` list the tool and its coverage object.

## 11. Architecture Decision Checkpoint

- **New ADR required:** Yes — `knowledge/decisions/internal-dependencies-by-declared-package-name.md`; see `adr.md`.

## 12. Risks, Trade-offs, and Open Questions

### Risks
Name collisions produce ambiguous results by design. A very large portfolio could make dependents long; the cap and total handle it.

### Trade-offs
Root manifests only undercount monorepos but say so; exact-name matching misses renamed or vendored packages but never invents an edge.

### Open Questions
None. Pagination of dependents is deferred until needed.

## 13. Traceability

Proposal, specs, and contract share the change ID `be-get-project-dependencies`; requirement package `docs/requirements/project-query/` (FR-012).

## 14. Design Readiness Review

- [x] Requirements are traced to design elements and checks.
- [x] Boundaries, failure handling, and the trust boundary are stated.
- [x] The architecture decision checkpoint is answered.
- [x] Risks and trade-offs are visible.

**Status:** Draft
