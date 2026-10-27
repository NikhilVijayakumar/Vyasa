# Design: be-file-composition-counts

## 1. Overview

### Purpose
Implement the file composition core so FR-021 can be verified, without waiting for the detector framework or discovery.

### Scope
A new `src/vyasa` package with a domain model, an application function, a filesystem walk adapter, a packaged data file, and tests.

### Design Principles
Dependencies point toward the domain (`structure.md` §6). Standard library only. Partial results are results, never exceptions. Create only the packages used.

## 2. Context and Constraints

### Current State
The repository has no source tree. The proposed layout is in `knowledge/architecture/system-architecture/structure.md`.

### Constraints
- Technical constraints: Python 3.12+, `pytest`, no runtime dependency.
- Security and privacy constraints: names only, no file opened, no path returned, no symlink followed.
- Performance and reliability constraints: depth 20, 50,000 entries, 60 seconds, all parameters (see the file composition decision).
- Compatibility and migration constraints: none.
- Operational constraints: the walk is synchronous and single-threaded.

### Existing Decisions and Conventions
Scan limits and symlink defaults, partial results never imply absence, and the new file composition decision.

### Knowledge References
- `knowledge/architecture/scanning-and-evidence/detector-inventory.md` — §9.13 behavior.
- `knowledge/decisions/file-composition-data-and-limits.md` — data and caps.
- `knowledge/decisions/scan-limits-and-symlink-defaults.md` — depth, time, symlinks.
- `knowledge/decisions/partial-results-never-imply-absence.md` — partial semantics.
- `knowledge/architecture/system-architecture/structure.md` — layout and dependency direction.

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| Counts classify by extension and agree | `classify(name, types)` and the tally in `compose` | Unit tests on a temp tree |
| Documentation-only indicator | `FileComposition.documentation_only` derived in the constructor path | Unit tests |
| Bounded walk with a partial marker | `walk_checkout` in the adapter | Unit tests with small limits and an injected clock |
| Symlinks and exclusions | `walk_checkout` prunes and never follows | Symlink fixture; skipped with a recorded reason where the platform cannot create symlinks |
| Evidence | `FileComposition.evidence` | Unit tests |
| Validated versioned file-type data | `load_file_types` | Unit tests on temp JSON files |

## 4. Architecture and Design

### Architectural Approach
`compose` (application) asks the adapter for file names and a stop reason, classifies each name through the domain `FileTypes`, and builds a `FileComposition`. The adapter knows nothing about categories; the domain knows nothing about the filesystem.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `vyasa.domain.file_composition` | `FileTypes`, `WalkLimits`, `FileComposition`, `classify` | stdlib |
| `vyasa.adapters.filesystem.checkout_walk` | `walk_checkout(root, limits, exclusions, clock)` yielding names and a stop reason | stdlib `os` |
| `vyasa.application.scanning.file_composition` | `compose`, `load_file_types` | the two above |
| `vyasa/data/file_types.json` | Versioned extension lists | none |

### Interfaces and Contracts
See `api-contract.md`.

### Key Workflows
`compose` → `walk_checkout` yields each file name in a directory pass and returns the stop reason → `classify` each name → tally → build the result with the derived indicator and evidence.

## 5. Data and State Management

No stored state. The data file is read once per process.

The walk uses `os.walk(topdown=True, followlinks=False)`. Each visited directory and file counts as one entry. On Windows `os.walk` still descends into a junction (probed 2026-10-27: a file behind a junction was listed), so every subdirectory is also pruned when `os.path.islink` or `os.path.isjunction` is true. The root is never pruned, even if it is itself a link or named like an exclusion. Directory names are compared by `casefold` against the exclusion set and pruned before descent. Names are sorted at each level so a partial result is repeatable. Depth is the number of path parts below `root`; a directory deeper than `max_depth` is not entered and marks the walk `depth`. `stopped_by` keeps the first cause observed. `onerror` marks `unreadable`. The clock is checked per directory.

## 6. Error Handling and Resilience

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| Unreadable directory | Partial, `unreadable` | Fix permissions and rescan |
| Bound reached | Partial, bound named | Raise the limit or accept the lower bound |
| Bad data file | `FileTypeDataError` | Fix the data |
| Root missing | `ValueError` | Caller error |

## 7. Security and Privacy

Trust boundary as in the contract. Nothing outside `root` is listed because symlinks are not followed. A name is read as a string and never interpreted. No path is returned. No material security or privacy impact beyond that.

## 8. Quality Attributes

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Determinism | Same tree and data give the same result | Counts are order-independent sums | Shuffled-order test |
| Testability | No sleeping, no real clock | Injected clock | Time-limit test |
| Bounded cost | Depth, entries, time | Checked in the walk | Limit tests |

## 9. Testing and Verification Strategy

### Behavioral Verification
One test per scenario in `specs/file-composition/spec.md`.

### Test Strategy
Unit tests with `pytest` and `tmp_path` fixtures (domain and loader), and adapter tests against real temporary trees. Symlink and junction fixtures are created for real (both were creatable on the target machine on 2026-10-27) and skipped with a stated reason where the platform refuses. No integration or persistence layer exists.

### Testability
Small limits are passed as parameters. The clock is a callable. The symlink test creates a symlink and skips with a stated reason if the platform refuses.

### Verification Evidence
`pytest` output and `python3 scripts/verify_workflows.py`; skips are reported, not hidden.

## 10. Implementation and Migration Considerations

### Implementation Order
Scaffolding (setuptools build backend, `pytest` with `pythonpath = src`), then data loader, then classification and counts, then the walk and bounds, then symlinks and exclusions.

### Migration and Rollout
None.

### Documentation and Operations
Update `README.md` with how to run the tests.

## 11. Architecture Decision Checkpoint

- **New ADR required:** Yes — recorded as `knowledge/decisions/file-composition-data-and-limits.md`; see `adr.md`.
