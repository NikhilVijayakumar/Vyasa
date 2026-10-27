# Interface and Data Contract: be-language-query

- **OpenSpec Change ID:** `be-language-query`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the new index tables, the added `search_projects` parameters, the added `get_project` field, and their errors.

## 2. Scope

In: migration 0006, `scan_workspace` enrichment, `search_projects`, `get_project`, and their MCP tool declarations. Out: sync exchanges and provider calls (not affected); no new tool.

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `search_projects` (changed) | MCP tool, read-only | Reads the index | adds `language: list[str] \| str \| None`, `language_status: str \| None` | each project adds `languages: list[str]` (union of matched labels' present checkouts) and `language_matches: list[{label, statuses}]` when `language` is given | `INVALID_INPUT` for an unknown label or status |
| `get_project` (changed) | MCP tool, read-only | Reads the index | unchanged | each checkout adds `languages` (below) | unchanged |
| `scan_workspace` (changed) | Python function | Walks eligible checkouts read-only, writes the index under the writer lock | unchanged; `detect` is an injectable callable | unchanged | a detection failure is a stored result, not an error |

`languages` object of a checkout: `status` (`complete`, `partial`, `failed`, `not_observed`), `stopped_by` (`depth`, `entries`, `time`, `unreadable`, or `null`), `observed_at` (ISO time or `null`), `types_version`, `items` (list of `{label, status, files}` where `status` is `files_detected` or `declared` and `files` is a count for `files_detected` and `null` for `declared`), sorted by label then status. A `not_observed` or `failed` checkout has an empty `items` and, for `failed`, a `reason` from a fixed set.

The allowed labels are the distinct values of the shipped `languages` and `manifests` maps. The allowed statuses are `files_detected` and `declared`. Tool descriptions list both.

## 4. Error Model

| Condition | Error code | Response shape | Safe to show the user |
|---|---|---|---|
| `language` not a string or list of strings | `INVALID_INPUT` | message names `language` | Yes |
| Unknown label | `INVALID_INPUT` | message names the value and lists allowed labels | Yes |
| Unknown or non-string `language_status` | `INVALID_INPUT` | message lists allowed statuses | Yes |
| Detection raises for a checkout | none | failed observation with `reason` `detection_error`; run partial | Yes; the exception text is not stored |

Other errors are unchanged.

## 5. Trust Boundary

Checkout contents remain untrusted and are only named, never opened. Labels come from trusted package data. Filter values are validated against fixed sets and bound as SQL parameters; no value is concatenated into SQL. No path appears in `languages`; checkout `path` stays behind `include_paths` as before. Languages are machine-local and are not part of any sync export.

## 6. Data Model

Migration 0006 adds:

| Entity | Field | Type | Required | Constraint or invariant |
|---|---|---|---|---|
| `language_observations` | `observation_id` | integer, primary key | Yes | Increases with time; the highest per checkout is current |
| | `checkout_id` | integer | Yes | References `checkouts` |
| | `run_id` | text | Yes | References `scan_runs` |
| | `observed_at` | text (ISO) | Yes | |
| | `status` | text | Yes | `complete`, `partial`, `failed` |
| | `stopped_by` | text | No | Set exactly when `partial` |
| | `types_version` | integer | Yes | The data version used |
| | `reason` | text | No | Set exactly when `failed`; one of a fixed set |
| `checkout_languages` | `observation_id` | integer | Yes | References `language_observations`, cascade on delete |
| | `label` | text | Yes | |
| | `status` | text | Yes | `files_detected` or `declared` |
| | `files` | integer | No | Positive for `files_detected`; null for `declared` |

Primary key of `checkout_languages` is (`observation_id`, `label`, `status`). An index on (`label`, `status`) serves the filter. Invariant: at most two observations per checkout; a `failed` observation has no language rows.

## 7. Migrations and Backward Compatibility

`0006_languages.sql` only creates tables and an index; `PRAGMA user_version` becomes 6 through the existing migration runner. Existing rows are untouched. A tool client that ignores unknown fields keeps working. Rollback: revert the change; the extra tables are harmless to the previous version.

## 8. Traceability

| Requirement | Operation | Field or rule | Acceptance scenario |
|---|---|---|---|
| Scan stores an observation | `scan_workspace` | `language_observations`, `checkout_languages` | Scan stores languages; Declared stored |
| Current and previous kept | store | at most two per checkout | Third scan; Unchanged tree |
| Partial rescan is current | store | `status`, `stopped_by` | Entry cap on rescan |
| Detection failure isolated | store | `status = failed`, `reason` | One checkout fails |
| Not reached keeps observation | store | no write | Checkout not reached |
| Migration | `open_index` | 0006 | Upgrade |
| Search by language and status | `search_projects` | `language`, `language_status` | Search by language; Several labels; Combined; Case; Declared only; Declared matches |
| Rejected values | `search_projects` | `INVALID_INPUT` | Typo; Bad status |
| Any present checkout | `search_projects` | checkout state | Two checkouts; Missing checkout |
| Partial matches positives | `search_projects` | observation status | Partial observation |
| Details per checkout | `get_project` | `languages` | Per checkout; Never observed; Missing keeps observation |
| Separate from profile | `get_project` | `profile` unchanged | Declared and detected differ |
| No filesystem access | both | read-only connection | Files changed since the scan |

## 9. Contract Review

- [x] Every affected operation is listed with request, response, and errors.
- [x] The error model states which conditions produce which error.
- [x] The trust boundary is stated.
- [x] The data model states the invariants.
- [x] Migration and backward compatibility are stated.
- [x] Every requirement in scope is traced.
- [x] No unresolved contract questions.

**Status:** Draft
