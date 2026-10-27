# Interface and Data Contract: be-file-composition-counts

- **OpenSpec Change ID:** `be-file-composition-counts`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the Python interface of the file composition core: the function, its inputs and result, its failures, and the file-type data format. No MCP tool, CLI command, index table, or sync exchange is involved.

## 2. Scope

In: `vyasa.application.scanning.file_composition.compose`, the `FileTypes` loader, and the result and limit types. Out: MCP tools, SQLite, Google Sheets, provider calls (not affected).

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `compose(root, types, limits, exclusions)` | Python function | Lists directories and file names under `root`; opens no file; writes nothing | `root: Path`, `types: FileTypes`, `limits: WalkLimits`, `exclusions: frozenset[str]` | `FileComposition` | `ValueError` when `root` is not a directory |
| `load_file_types(path)` | Python function | Reads one JSON file | `path: Path` | `FileTypes` | `FileTypeDataError` naming the field or extension |

`WalkLimits` fields (defaults): `max_depth = 20`, `max_entries = 50_000`, `max_seconds = 60.0`. A `clock` callable may be injected for tests.

`FileComposition` fields: `code`, `documentation`, `other` (non-negative integers), `total` (their sum, a property), `complete` (bool, a property), `stopped_by` (`None`, `"depth"`, `"entries"`, `"time"`, or `"unreadable"`), `documentation_only` (`True`, `False`, or `None` for unknown), `evidence`.

`evidence` fields: `types_version` (int), `exclusions` (sorted tuple of names), `limits` (the `WalkLimits` used). The completeness marker is `complete` and `stopped_by` on the result.

`DEFAULT_EXCLUSIONS` is exported: `.git`, `node_modules`, `.venv`, `venv`, `__pycache__`, `target`, `build`, `dist`. Names compare case-insensitively. `stopped_by` records the first cause observed; an unreadable directory does not stop the walk, a bound does.

## 4. Error Model

| Condition | Error code | Response shape | Safe to show the user |
|---|---|---|---|
| `root` missing or not a directory | `ValueError` | message names the path | Yes |
| Data file unreadable or not JSON | `FileTypeDataError` | message names the file | Yes |
| Missing or non-integer `version` | `FileTypeDataError` | message names `version` | Yes |
| Extension without a leading dot or not a string | `FileTypeDataError` | message names the list and value | Yes |
| Extension in both lists | `FileTypeDataError` | message names the extension | Yes |
| Bound reached or directory unreadable during the walk | none | a `FileComposition` with `complete = False` | Yes |

A walk problem is a result, not an exception: partial counts are reported, never raised.

## 5. Trust Boundary

`root` and the checkout contents are untrusted: names are classified and counted, never executed, parsed, or opened. Directory symlinks and Windows junctions are not followed, so nothing outside `root` is read. The file-type data is trusted package data validated on load. Only counts and the exclusion set leave the function; no path is returned.

## 6. Data Model

File-type data (JSON):

| Entity | Field | Type | Required | Constraint or invariant |
|---|---|---|---|---|
| FileTypes | `version` | integer | Yes | At least 1 |
| FileTypes | `code_extensions` | list of strings | Yes | Each starts with `.`; stored lower-case |
| FileTypes | `documentation_extensions` | list of strings | Yes | Each starts with `.`; disjoint from `code_extensions` |

Invariants of `FileComposition`: `total = code + documentation + other`; `documentation_only` is `None` exactly when `complete` is false; `stopped_by` is `None` exactly when `complete` is true.

## 7. Migrations and Backward Compatibility

New code; nothing to migrate. A change to the data file raises `version`, which later marks stored observations stale. Rollback: revert the change.

## 8. Traceability

| Requirement | Operation | Field or rule | Acceptance scenario |
|---|---|---|---|
| Counts classify by extension and agree | `compose` | `code`, `documentation`, `other`, `total` | Mixed checkout; Extension case ignored; Unknown type is other; Content is not read |
| Documentation-only indicator | `compose` | `documentation_only` | Documentation only; Documentation and code; Empty checkout |
| Bounded walk with a partial marker | `compose` | `complete`, `stopped_by` | Entry cap; Depth; Time; Unreadable directory; Limits not exceeded |
| Symlinks and exclusions | `compose` | `exclusions` | Symlink escape; Excluded directory |
| Evidence | `compose` | `evidence` | Evidence present; Deterministic order |
| Validated versioned file-type data | `load_file_types` | `version`, lists | Valid data; Overlapping lists; Malformed data |

## 9. Contract Review

- [x] Every affected operation is listed with request, response, and errors.
- [x] The error model states which conditions produce which error.
- [x] The trust boundary is stated.
- [x] The data model states the invariants.
- [x] Migration and backward compatibility are stated.
- [x] Every requirement in scope is traced.
- [x] No unresolved contract questions.

**Status:** Draft
