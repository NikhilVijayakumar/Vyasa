# Interface and Data Contract: be-language-detector

- **OpenSpec Change ID:** `be-language-detector`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the Python interface of the language detector: the function, its result, its failures, and the added file-type data fields. No MCP tool, CLI command, index table, or sync exchange is involved.

## 2. Scope

In: `vyasa.application.scanning.languages.detect_languages`, the `LanguageReport` result types, and the extended `FileTypes` loader. Out: MCP tools, SQLite, Google Sheets, provider calls (not affected).

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `detect_languages(root, types, limits, exclusions, clock)` | Python function | Lists directory and file names under `root`; opens no file; writes nothing | as `compose` | `LanguageReport` | `ValueError` when `root` is not a directory |
| `load_file_types(path)` | Python function | Reads one JSON file | `path: Path` | `FileTypes` (now with `languages`, `manifests`) | `FileTypeDataError` naming the field or extension |

`LanguageReport` fields: `files_detected` (tuple of `(label, count)` sorted by label, counts positive), `declared` (sorted tuple of labels), `stopped_by` (`None`, `"depth"`, `"entries"`, `"time"`, `"unreadable"`), `complete` (property), `evidence` (the `Evidence` type of `compose`), and `is_absent(label)` (`True` when complete and the label is in neither result; `False` when found; `None` when partial and not found).

`FileTypes` gains `languages: Mapping[str, str]` and `manifests: Mapping[str, str]`, both empty for version 1 data.

## 4. Error Model

| Condition | Error code | Response shape | Safe to show the user |
|---|---|---|---|
| `root` missing or not a directory | `ValueError` | message names the path | Yes |
| Data unreadable, not JSON, bad `version` | `FileTypeDataError` | message names the file or field | Yes |
| `languages` or `manifests` not an object, or a label empty or not a string | `FileTypeDataError` | message names the map and key | Yes |
| `languages` keys differ from `code_extensions` | `FileTypeDataError` | message names the extension | Yes |
| Bound reached or directory unreadable | none | a `LanguageReport` with `complete = False` | Yes |

A walk problem is a result, not an exception.

## 5. Trust Boundary

`root` and the checkout contents are untrusted: names are matched against the tables, never executed, parsed, or opened. Directory symlinks and junctions are not followed. The data file is trusted package data validated on load. Only labels, counts, and the exclusion set leave the function; no path is returned.

## 6. Data Model

File-type data (JSON), version 2 adds:

| Entity | Field | Type | Required | Constraint or invariant |
|---|---|---|---|---|
| FileTypes | `languages` | object, extension to label | No (version 1) | Keys start with `.`, lower-case, and equal `code_extensions`; labels non-empty strings |
| FileTypes | `manifests` | object, file name to label | No (version 1) | Names stored lower-case, no path separator; labels non-empty strings |

Invariants of `LanguageReport`: the sum of `files_detected` counts equals the code count of `compose` for the same input; `stopped_by` is `None` exactly when `complete`.

## 7. Migrations and Backward Compatibility

`file_types.json` moves to version 2; version 1 data still loads and yields no languages. `compose` ignores the new fields and is unchanged. Nothing is stored. Rollback: revert the change.

## 8. Traceability

| Requirement | Operation | Field or rule | Acceptance scenario |
|---|---|---|---|
| Files detected by extension | `detect_languages` | `files_detected` | Extensions give counts; Extension case ignored; Shared extension; Unknown ignored; Content not read |
| Histogram agrees | `detect_languages` | sum invariant | Sum equals code count; Partial sum |
| Declared by manifest presence | `detect_languages` | `declared` | Manifest without sources; Nested; Unrecognized |
| Statuses stay separate | `detect_languages` | both fields | Found both ways |
| Partial reports absence unknown | `detect_languages` | `is_absent` | Entry cap; Complete |
| Evidence | `detect_languages` | `evidence` | Evidence present; Deterministic order |
| Validated language data | `load_file_types` | `languages`, `manifests` | Valid; Version 1; Disagree; Malformed |

## 9. Contract Review

- [x] Every affected operation is listed with request, response, and errors.
- [x] The error model states which conditions produce which error.
- [x] The trust boundary is stated.
- [x] The data model states the invariants.
- [x] Migration and backward compatibility are stated.
- [x] Every requirement in scope is traced.
- [x] No unresolved contract questions.

**Status:** Draft
