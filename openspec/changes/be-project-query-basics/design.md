# Design: be-project-query-basics

## 1. Overview

### Purpose
Give the MCP layer, and any other caller, one tested place that answers portfolio questions from the index.

### Scope
Three read functions and their shared helpers. No transport, no scanning.

### Design Principles
Read-only by construction. Validate everything from the caller. Same input, same output. Core logic knows nothing about MCP.

## 2. Context and Constraints

### Current State
Adapter functions return raw rows and are unbounded.

### Constraints
- Technical: Python 3.12+, `sqlite3`; no MCP SDK or Pydantic in this change.
- Security and privacy: paths omitted by default; parameterized SQL; escaped `LIKE`.
- Performance: one query per page plus small per-project lookups, bounded by the limit.

### Existing Decisions and Conventions
Local paths omitted by default; stdio-only transport; stored identity with aliases.

### Knowledge References
- `knowledge/architecture/mcp-interface/response-conventions.md`
- `knowledge/architecture/mcp-interface/search-and-details.md`
- `knowledge/decisions/mcp-local-paths-omitted-by-default.md`

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| Search is deterministic and bounded | keyset pagination on (lower(name), id) | 45-project paging test, repeat test |
| Search matches text and filters | `_where` builder | Parametrized filter tests |
| Project details carry identity and review state | `get_project` | Fixture projects |
| Index status reports reliability | `get_index_status` | Empty and after-run tests |
| Queries are read-only and omit local paths | read-only connection, `include_paths` | Write attempt, key scan of results |

## 4. Architecture and Design

### Architectural Approach
`_validate` normalizes inputs and raises `INVALID_INPUT`. `_where` builds a fixed SQL skeleton and a parameter list: clauses are chosen from fixed strings, values are bound, and `LIKE` input is escaped with `ESCAPE '\\'`. The search fetches `limit + 1` rows ordered by `(lower(display_name), project_id)` after the cursor; the extra row sets `has_more`. Per-project extras (providers, candidates) are read for the page only. `_envelope` adds `meta` using `store.freshness`.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `vyasa.application.query` | validation, SQL, envelope, cursor | `vyasa.adapters.sqlite.review`, `vyasa.application.indexing.store.freshness`, domain |
| `vyasa.domain.index` | new error codes, allowed values | none |

### Interfaces and Contracts
See `api-contract.md`.

### Key Workflows
Validate → query a page → enrich → envelope.

## 5. Data and State Management

No state. The clock is injected.

## 6. Error Handling and Resilience

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| Invalid input | `INVALID_INPUT` before any query | Fix input |
| Tampered cursor | `INVALID_CURSOR` | Restart paging |
| Index changes between pages | Keyset paging stays consistent for unchanged rows | Documented |

## 7. Security and Privacy

Contract §5. A test scans every returned string for the checkout path and scanned root.

## 8. Quality Attributes

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Determinism | Stable order | Total order with id tie-break | Paging and repeat tests |
| Safety | Never write | Read-only connection | Write attempt test |

## 9. Testing and Verification Strategy

### Behavioral Verification
One test per scenario.

### Test Strategy
Persistence-backed tests: build an index with `store_run`, then query through a read-only connection.

### Testability
Clock and `include_paths` injected.

### Verification Evidence
`pytest` output; a query run against the real workspace index.

## 10. Implementation and Migration Considerations

### Implementation Order
Envelope and validation, search, details, status.

### Migration and Rollout
None.

### Documentation and Operations
Log entry only if a decision changes.

## 11. Architecture Decision Checkpoint

- **New ADR required:** No — `knowledge/decisions/mcp-local-paths-omitted-by-default.md` applies; see `adr.md`.
