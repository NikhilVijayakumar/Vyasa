# Interface and Data Contract: be-project-markers

- **OpenSpec Change ID:** `be-project-markers`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the marker rules data, the detector function, the walk's added fields, the new index storage, the added `search_projects` parameters, the added `get_project` field, and their errors.

## 2. Scope

In: `markers.json`, `load_marker_rules`, `markers_of`, `walk_checkout`, `scan_checkout`, `scan_workspace`, migration 0008, `search_projects`, `get_project`, and the MCP declarations. Out: sync exchanges and provider calls (not affected); no new tool.

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `load_marker_rules(path)` | Python function | Reads one JSON file | `path: Path` | `MarkerRules` | `MarkerRulesError` naming the field |
| `markers_of(files, directories, rules)` | Python function (pure) | None | relative POSIX paths | `MarkerReport` | none |
| `walk_checkout(...)` (changed) | Python function | Lists names under `root`; opens no file | unchanged | `WalkResult` adds `files` and `directories` (relative POSIX paths, sorted) | unchanged |
| `scan_checkout(..., rules=None)` (changed) | Python function | as before | adds optional `rules` | `CheckoutScan` adds `markers: MarkerReport \| None` (None when no rules given) | `ValueError` as before |
| `scan_workspace` (changed) | Python function | as before | unchanged | unchanged | a detection failure is a stored result, not an error |
| `search_projects` (changed) | MCP tool, read-only | Reads the index | adds `marker: list[str] \| str \| None`, `marker_state: str \| None` | unchanged items | `INVALID_INPUT` for an unknown name or state |
| `get_project` (changed) | MCP tool, read-only | Reads the index | unchanged | each checkout adds `markers` (below) | unchanged |

Marker names: `readme`, `docs`, `agent_instructions`, `openspec_directory`, `openspec_config`, `openspec_specs`, `openspec_changes`, `tests`. States for filtering: `detected` (default), `not_detected`.

`MarkerReport`: `hits` (tuple of `MarkerHit(marker, rule, path, scope)` sorted by marker, path), `rules_version`, `stopped_by`, `complete`.

`markers` object of a checkout: `status` (`complete`, `partial`, `not_assessed`), `rules_version` (integer or `null`), `stopped_by`, `observed_at`, and `items`: for every marker `{marker, state, total, rules, paths, more}`, where `state` is `detected`, `not_detected` (only when `complete`), or `unknown` (when `partial` and not found); `total`, `rules`, `paths` (list of `{path, scope}` with `scope` only for `agent_instructions`) and `more` (count of matches beyond the 20 stored) are set only when `detected`. A `not_assessed` checkout has an empty `items`.

## 4. Error Model

| Condition | Error code | Response shape | Safe to show the user |
|---|---|---|---|
| Rules data unreadable, not JSON, wrong shape, empty name, or name with a separator | `MarkerRulesError` | message names the file and field | Yes |
| `marker` not a string or list of strings, or an unknown name | `INVALID_INPUT` | message names the value and lists allowed names | Yes |
| `marker_state` not `detected` or `not_detected` | `INVALID_INPUT` | message lists allowed states | Yes |
| Detection raises for a checkout | none | failed observation, no rules version, no rows; run partial | Yes; the exception text is not stored |

Other errors are unchanged.

## 5. Trust Boundary

Checkout names are untrusted and are only compared with fixed rules, never opened, parsed, or executed. Stored paths are relative to the checkout, normalized to forward slashes, never absolute, and never contain `..`, because they come from the walk's own relative paths. Filter values are validated against fixed sets and bound as parameters. Markers are machine-local and are not part of any sync export.

## 6. Data Model

Marker rules (JSON, `src/vyasa/data/markers.json`): `version` (integer at least 1); `readme.names`; `docs.directories`; `agent_instructions.files`; `openspec.directory`, `openspec.config`, `openspec.specs`, `openspec.changes`; `tests.directories`, `tests.file_patterns`. Names are non-empty strings without a path separator; fixed names and directories compare case-insensitively; file patterns compare case-sensitively.

Migration 0008 adds:

| Entity | Field | Type | Required | Constraint or invariant |
|---|---|---|---|---|
| `language_observations` | `markers_version` | integer | No | At least 1; null means not assessed (older or failed) |
| `checkout_markers` | `observation_id` | integer | Yes | References `language_observations`, cascade on delete |
| | `marker` | text | Yes | One of the eight names |
| | `total` | integer | Yes | Positive |
| | `rules` | text (JSON list) | Yes | Sorted matching rule names |
| | `paths` | text (JSON list) | Yes | At most 20 `{path, scope?}` objects in stable order |

Primary key (`observation_id`, `marker`); index on `marker`. A `not_detected` or `unknown` marker has no row. Invariant: a failed observation has no `markers_version` and no rows.

## 7. Migrations and Backward Compatibility

`0008_project_markers.sql` adds a nullable column and a table; `PRAGMA user_version` becomes 8. Existing rows are untouched and read as `not_assessed`. `scan_checkout` called without rules behaves as before. `WalkResult` only gains fields. Rollback: revert the change; the extra column and table are harmless to the previous version.

## 8. Traceability

| Requirement | Operation | Field or rule | Acceptance scenario |
|---|---|---|---|
| Markers from names and directories | `markers_of` | rules | README at the root; README name case; Documentation directory; Content is not read |
| Location rules | `markers_of` | per-marker depth | README below the root; Nested agent file; Nested tests |
| Tests by directory and name | `markers_of` | `tests` rules | Directory and name; Not a test name |
| OpenSpec indicators separate | `markers_of` | four markers | Directory without config |
| Three states | storage and read model | `state` | Complete; Partial; Found despite a partial walk |
| Evidence relative and capped | store | `paths`, `total` | Cap; Relative only; Stable order |
| Stored on the observation | `scan_workspace` | `checkout_markers` | Stored with the observation; Retention |
| Older and failed not assessed | store | `markers_version` | Upgrade; Failed observation |
| Rules are validated data | `load_marker_rules` | rules shape | Valid rules; Malformed rules |
| Walk reports paths | `walk_checkout` | `files`, `directories` | Paths and directories; Counts unchanged |
| Detection failure isolated | `scan_workspace` | failed observation | One checkout fails |
| Search by marker | `search_projects` | `marker`, `marker_state` | Detected; Not detected; Partial; Not assessed; Several; Any active; Missing; Combined; Unknown |
| Details per checkout | `get_project` | `markers` | Per checkout; Not assessed; Partial; Evidence shown; Missing keeps markers |
| Read-only | both | read-only connection | Files changed since the scan |

## 9. Contract Review

- [x] Every affected operation is listed with request, response, and errors.
- [x] The error model states which conditions produce which error.
- [x] The trust boundary is stated.
- [x] The data model states the invariants.
- [x] Migration and backward compatibility are stated.
- [x] Every requirement in scope is traced.
- [x] No unresolved contract questions.

**Status:** Draft
