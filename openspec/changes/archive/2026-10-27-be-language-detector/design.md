# Design: be-language-detector

## 1. Overview

### Purpose
Implement FR-023 as a library core on the existing bounded walk, so languages can be verified before persistence and MCP exist for them.

### Scope
A new domain module, a new application module, an extended loader, and an extended data file with tests.

### Design Principles
Reuse the walk and the evidence type. One data file. Partial results are results, never exceptions. Dependencies point toward the domain.

## 2. Context and Constraints

### Current State
`compose` walks once with `walk_checkout` and classifies names with `FileTypes.classify` (`src/vyasa/application/scanning/file_composition.py`, `src/vyasa/domain/file_composition.py`). `load_file_types` validates version 1 data. The query and persistence layers do not use composition yet.

### Constraints
- Technical constraints: Python 3.12+, standard library only.
- Security and privacy constraints: names only, no file opened, no path returned, no symlink followed.
- Performance and reliability constraints: the same limits as `compose` (depth 20, 50,000 entries, 60 seconds).
- Compatibility and migration constraints: version 1 data still loads; `compose` unchanged.
- Operational constraints: synchronous and single-threaded.

### Existing Decisions and Conventions
Scan limits and symlink defaults, partial results never imply absence, file composition data and limits.

### Knowledge References
- `knowledge/architecture/scanning-and-evidence/detector-inventory.md` — §9.3 behavior.
- `knowledge/decisions/language-evidence-statuses.md` — two statuses, fixed table.
- `knowledge/decisions/file-composition-data-and-limits.md` — shared data and walk.
- `knowledge/decisions/partial-results-never-imply-absence.md` — partial semantics.

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| Files detected by extension | `languages_of(names, types)` in the domain | Unit tests on names, no filesystem |
| Histogram agrees with the code count | Same walk call and same `extension` function as `compose` | Test comparing both on one temp tree, including a capped tree |
| Declared by manifest presence | Lower-cased name lookup in `types.manifests` | Unit tests |
| Statuses stay separate | Two fields on `LanguageReport` | Unit tests |
| Partial reports absence unknown | `LanguageReport.is_absent` | Unit tests with a small entry cap |
| Evidence | Reuse `Evidence` | Unit tests; shuffled-order test |
| Validated language data | `load_file_types` extension | Unit tests on temp JSON |

## 4. Architecture and Design

### Architectural Approach
`detect_languages` (application) calls `walk_checkout` once, passes the names to the pure `languages_of`, and builds a `LanguageReport`. It repeats the setup of `compose` (ignore file, exclusions) rather than refactoring `compose`.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `vyasa.domain.languages` | `LanguageReport`, `languages_of(names, types)` | `vyasa.domain.file_composition` |
| `vyasa.domain.file_composition` | `FileTypes` gains `languages` and `manifests` (default empty) | stdlib |
| `vyasa.application.scanning.languages` | `detect_languages` | walk adapter, domain |
| `vyasa.application.scanning.file_composition` | `load_file_types` validates the new maps | domain |
| `vyasa/data/file_types.json` | Version 2: `languages`, `manifests` | none |

### Interfaces and Contracts
See `api-contract.md`.

### Key Workflows
`detect_languages` → `walk_checkout` returns names and a stop reason → `languages_of` counts labels by extension and collects declared labels by manifest name → build the report with evidence.

## 5. Data and State Management

No stored state. `languages_of` counts a name only when its extension is a key of `types.languages`; the loader guarantees those keys equal `code_extensions`, so the counts equal the code count. Manifest names are matched on `name.casefold()`. Both result tuples are sorted.

## 6. Error Handling and Resilience

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| Unreadable directory or bound | Partial report, bound named | Fix permissions or raise the limit |
| Bad data file | `FileTypeDataError` | Fix the data |
| Root missing | `ValueError` | Caller error |

## 7. Security and Privacy

Trust boundary as in the contract. A name is read as a string and compared; nothing is opened. No path is returned. No material security or privacy impact beyond the existing walk.

## 8. Quality Attributes

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Determinism | Same tree and data give the same result | Order-independent counts, sorted output | Shuffled-order test |
| Integrity | Histogram sums to the code count | Loader invariant plus shared walk | Comparison test |
| Bounded cost | Depth, entries, time | Inherited from the walk | Entry-cap test |

## 9. Testing and Verification Strategy

### Behavioral Verification
One test per scenario in `specs/language-detection/spec.md`.

### Test Strategy
Unit tests with `pytest`: pure `languages_of` and loader tests need no filesystem; `detect_languages` tests use `tmp_path` trees and small limits. No integration or persistence layer is involved.

### Testability
Limits are parameters; the clock is injected.

### Verification Evidence
`pytest` output and `python scripts/verify_workflows.py`; skips are reported.

## 10. Implementation and Migration Considerations

### Implementation Order
Data and loader, then `languages_of` and the report, then `detect_languages` with partial behavior, then the evidence and determinism checks.

### Migration and Rollout
Data file moves to version 2; nothing else.

### Documentation and Operations
Update `knowledge/architecture/scanning-and-evidence/detector-inventory.md` §9.3 to state the two statuses if behavior diverged; add a dated entry to `knowledge/log.md`.

## 11. Architecture Decision Checkpoint

- **New ADR required:** Yes — `knowledge/decisions/language-evidence-statuses.md`; see `adr.md`.

## 12. Risks, Trade-offs, and Open Questions

### Risks
The `code_extensions` and `languages` lists can drift; the loader rejects it.

### Trade-offs
Duplicating the extension keys in two lists costs a validation rule; the alternative of deriving `code_extensions` from `languages` would break version 1 data. Revisit when version 1 support is dropped.

### Open Questions
None.

## 13. Traceability

Proposal, specs, and contract share the change ID `be-language-detector`; requirement package `docs/requirements/language-detection/`.

## 14. Design Readiness Review

- [x] Requirements are traced to design elements and checks.
- [x] Boundaries, failure handling, and the trust boundary are stated.
- [x] The architecture decision checkpoint is answered.
- [x] Risks and trade-offs are visible.

**Status:** Draft
