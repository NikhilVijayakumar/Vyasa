# Design: be-framework-detector

## 1. Overview

### Purpose
Read supported root manifests safely during the scan, map them to technologies, store the result on the checkout observation, and expose it through the existing read-only queries.

### Scope
A strict reader, pure parsers, a registry, detection in the scan, a migration, storage, query changes, and the MCP declaration.

### Design Principles
Untrusted content is data, never code. Pure parsers behind one safe reader. One walk. Reuse the observation and query patterns. Derive absence from completeness. A bad file is a status.

## 2. Context and Constraints

### Current State
`scan_checkout` walks once and returns counts, languages, and markers; `projects._store_languages` inserts the observation with its rows and prunes to two; `search_projects` builds fixed SQL joined to the current observation; `get_project` reads per-checkout objects. The profile and ignore file readers are the only existing file reads.

### Constraints
- Technical constraints: Python 3.12+, standard library only (`tomllib`, `json`, `re`, `fnmatch`), SQLite.
- Security and privacy constraints: root regular files only, never a link, 1 MiB, strict UTF-8, nothing executed, no text or absolute path stored, values bound.
- Performance and reliability constraints: at most five kinds of root file, 1 MiB each; the walk's limits; dependencies capped at 200 per manifest.
- Compatibility and migration constraints: additive; existing behavior kept.
- Operational constraints: single-writer lock; queries use a read-only connection.

### Existing Decisions and Conventions
Scan limits and symlink defaults, checkout walk observation, partial results never imply absence, technology registry as versioned data, MCP omits local paths by default.

### Knowledge References
- `knowledge/decisions/framework-detection-from-manifests.md` — reading, scopes, states.
- `knowledge/decisions/technology-registry-as-data.md` — registry.
- `knowledge/decisions/scan-limits-and-symlink-defaults.md` — limits and links.
- `knowledge/decisions/partial-results-never-imply-absence.md` — partial semantics.
- `knowledge/architecture/scanning-and-evidence/detector-inventory.md` — §9.4.

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| Strict reading | `manifest_reader.read_manifest` | Adapter tests on real temp files: link, size, encoding, directory |
| Per-manifest status | `parse_manifest` raising `ManifestParseError`; `detect_frameworks` catching | Unit tests with hostile text; deep nesting test |
| Scoped capped dependencies | one parser function per format | Unit tests per ecosystem on text, no filesystem |
| Registry technologies | `technologies_of(manifests, registry)` | Unit tests |
| Ecosystem states | derived on read from `frameworks_version`, status, rows | Persistence and contract tests |
| Nested and workspace | file list scan in `detect_frameworks`; flag from the parser | Unit tests |
| Stored on the observation | `_store_frameworks` in the same transaction | Persistence tests on a real database file |
| Registry validated | `load_registry` | Unit tests on temp JSON |
| Search and details | clauses and `projects.checkout_frameworks` | Contract tests and the MCP snapshot |

## 4. Architecture and Design

### Architectural Approach
After the walk, `scan_checkout` passes the walk's relative file paths to `detect_frameworks`. Root files whose name matches a supported pattern are read through `read_manifest`; the text goes to `parse_manifest`, which returns scoped dependencies or raises `ManifestParseError` with a fixed reason. Supported names below the root are only counted. Dependencies are matched against the registry per ecosystem. The report rides on the `LanguageOutcome` and `_store_languages` inserts it with the observation.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `vyasa.adapters.filesystem.manifest_reader` | `read_manifest`: `lstat`, size, bounded binary read, strict decode | stdlib |
| `vyasa.domain.frameworks` | `Dependency`, `ManifestResult`, `TechnologyFound`, `FrameworkReport`, `TechnologyRegistry`, errors, constants | stdlib |
| `vyasa.domain.manifests` | `parse_manifest` and the five format parsers; name normalization | stdlib |
| `vyasa.application.scanning.frameworks` | `load_registry`, `default_registry`, `detect_frameworks`, `technologies_of` | domain, adapter |
| `vyasa/data/technologies.json` | versioned registry | none |
| `vyasa.application.scanning.checkout_scan` | calls `detect_frameworks` when a registry is given | above |
| `vyasa.domain.languages` | `CheckoutScan.frameworks`, `LanguageOutcome.frameworks` | domain |
| `vyasa.adapters.sqlite.projects` | `_store_frameworks`, `checkout_frameworks` read model, filter helper | sqlite |
| `vyasa/adapters/sqlite/migrations/0009_frameworks.sql` | column and tables | none |
| `vyasa.application.query`, `vyasa.adapters.mcp.server` | parameter, validation, details, descriptions | adapters |

### Interfaces and Contracts
See `api-contract.md`.

### Key Workflows
Scan: walk → `detect_frameworks` (read, parse, map; each manifest isolated) → `upsert` + `_store_languages` inserts the observation, rows, and frameworks → prune to two. Query: validate → SQL over the current observation of active checkouts → items; details derive each ecosystem state from the stored rows and the observation.

## 5. Data and State Management

The reader does `os.lstat`; a symlink gives `unreadable/link`, anything not a regular file `unreadable/not_file`, a size over the limit `too_large`; otherwise it opens in binary mode and reads `limit + 1` bytes (a file that grew after `lstat` is also `too_large`), decodes with `utf-8-sig` strictly, and maps `OSError` to `unreadable/io`. Parsers: `tomllib.loads` for TOML; `json.loads` for JSON with `RecursionError` mapped to `too_deep`; `ValueError`/`tomllib.TOMLDecodeError` to `syntax`; a wrong top-level or field type to `structure`. `requirements*.txt` and `go.mod` are line parsers using fixed anchored regular expressions on bounded lines. Names: Python names normalize per PEP 503 and the constraint is the remainder after extras, before any `;` marker. Registry matching uses the normalized (Python) or lower-cased (others) name. Technologies unite scopes and manifests by key. Ecosystem state with no manifest row is `not_detected` when the current observation is complete with a registry version, `unknown` when partial with one; `not_assessed` for the whole checkout when the version is null.

The filter SQL is an EXISTS over active checkouts joined to the current observation and `checkout_technologies` with `key IN (...)`.

## 6. Error Handling and Resilience

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| Unreadable, oversized, linked, or non-UTF-8 manifest | Per-manifest status; other manifests still read | Fix the repository and rescan |
| Parser exception of any type | `malformed` with a fixed reason | none needed |
| Detection raises outside a manifest | Failed observation, no version, run partial | Fix and rescan |
| Bad registry data | `RegistryError` at load | Fix the data |
| Bad filter value | `INVALID_INPUT` | Caller corrects |

## 7. Security and Privacy

Trust boundary as in the contract. The reader is the only code that opens repository files for this detector and it enforces the rules once; parsers receive text only. Parser failures never echo content. No path other than a root file name is stored. No material privacy impact beyond the existing index.

## 8. Quality Attributes

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Safety | Untrusted input never executed or trusted | Strict reader, stdlib parsers, fixed reasons | Hostile fixtures |
| Honesty | Absence only from a complete assessment | State derived from status and version | Partial and not-assessed tests |
| Determinism | Same files and registry give the same result | Sorted manifests, dependencies, technologies | Shuffled-order test |
| Isolation | One bad file does not hide others | Per-manifest handling | Mixed-fixture test |
| Cost | Bounded reads | 1 MiB × five root file kinds, 200 dependencies per manifest | Cap tests |

## 9. Testing and Verification Strategy

### Behavioral Verification
One test per scenario in both spec files.

### Test Strategy
Unit tests for parsers, registry, and technology mapping (no filesystem); adapter tests for the reader on real temp files (including a real symlink, skipped with a stated reason where the platform refuses); detection tests on real temp trees; persistence tests against a real temporary SQLite file; contract tests through `queries` and the MCP snapshot (`tests/snapshots/mcp_tools.json`).

### Testability
The reader's byte limit, `discover`, `detect`, and the clock are injectable; the registry is plain data.

### Verification Evidence
`python -m pytest`, `python scripts/verify_workflows.py`; skips are reported.

## 10. Implementation and Migration Considerations

### Implementation Order
Registry and parsers, then the reader, then detection and nested counts, then migration and storage, then the filter, then details, then the MCP declaration.

### Migration and Rollout
Additive migration on open; existing observations read `not_assessed` until the next scan.

### Documentation and Operations
Update the tool descriptions and `knowledge/log.md`.

## 11. Architecture Decision Checkpoint

- **New ADR required:** Yes — `knowledge/decisions/framework-detection-from-manifests.md`; see `adr.md`.

## 12. Risks, Trade-offs, and Open Questions

### Risks
A pathological but small file could be slow to parse; the 1 MiB bound and the stdlib parsers keep this bounded, and the scan already has a per-project time limit.

### Trade-offs
Root-only manifests undercount monorepos but say so; a registry of about forty entries misses many frameworks but never invents one.

### Open Questions
None.

## 13. Traceability

Proposal, specs, and contract share the change ID `be-framework-detector`; requirement package `docs/requirements/framework-detection/`.

## 14. Design Readiness Review

- [x] Requirements are traced to design elements and checks.
- [x] Boundaries, failure handling, and the trust boundary are stated.
- [x] The architecture decision checkpoint is answered.
- [x] Risks and trade-offs are visible.

**Status:** Draft
