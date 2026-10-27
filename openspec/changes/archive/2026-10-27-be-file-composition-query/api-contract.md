# Interface and Data Contract: be-file-composition-query

- **OpenSpec Change ID:** `be-file-composition-query`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the shared scan function, the added observation columns, the added `search_projects` parameter, the added `get_project` field, and their errors.

## 2. Scope

In: `scan_checkout`, `scan_workspace`, migration 0007, `search_projects`, `get_project`, and the MCP declarations. Out: sync exchanges and provider calls (not affected); no new tool.

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `scan_checkout(root, types, limits, exclusions, clock)` | Python function | Lists names under `root` once; opens no file; writes nothing | as `compose` | `CheckoutScan(composition, languages)` | `ValueError` when `root` is not a directory |
| `compose`, `detect_languages` | Python functions | as before | as before | as before (views of `scan_checkout`) | as before |
| `scan_workspace` (changed) | Python function | Walks eligible checkouts read-only; writes the index under the writer lock | the injectable `detect` callable now returns a `CheckoutScan` | unchanged | a detection failure is a stored result, not an error |
| `search_projects` (changed) | MCP tool, read-only | Reads the index | adds `documentation_only: bool \| None` | unchanged items | `INVALID_INPUT` when not a boolean |
| `get_project` (changed) | MCP tool, read-only | Reads the index | unchanged | each checkout adds `composition` (below) | unchanged |

`composition` object of a checkout: `status` (`complete`, `partial`, `not_counted`), `stopped_by` (`depth`, `entries`, `time`, `unreadable`, or `null`), `observed_at` (ISO time or `null`), `code`, `documentation`, `other`, `total` (integers, all `null` when `not_counted`), and `documentation_only` (`true`, `false`, or `null`). `documentation_only` is `null` unless `status` is `complete`; when complete it is `documentation > 0 and code == 0`.

## 4. Error Model

| Condition | Error code | Response shape | Safe to show the user |
|---|---|---|---|
| `documentation_only` is not a boolean | `INVALID_INPUT` | message names `documentation_only` | Yes |
| Detection raises for a checkout | none | failed observation, counts empty; run partial | Yes |

Other errors are unchanged.

## 5. Trust Boundary

Checkout contents remain untrusted and are only named, never opened. The filter value is a validated boolean bound as a parameter; no value is concatenated into SQL. No path appears in `composition`. Counts are machine-local and are not part of any sync export.

## 6. Data Model

Migration 0007 adds to `language_observations`:

| Entity | Field | Type | Required | Constraint or invariant |
|---|---|---|---|---|
| `language_observations` | `code_files` | integer | No | At least 0 |
| | `documentation_files` | integer | No | At least 0 |
| | `other_files` | integer | No | At least 0 |

The three columns are all null or all set; a `failed` observation has all null; an observation made before this migration has all null. Invariants of the read model: `total = code + documentation + other`; the sum of the observation's `files_detected` counts equals `code_files` when the counts are set.

## 7. Migrations and Backward Compatibility

`0007_composition_counts.sql` only adds nullable columns; `PRAGMA user_version` becomes 7 through the existing runner. Existing rows are untouched and read as `not_counted`. `compose` and `detect_languages` keep their signatures and results. Rollback: revert the change; the extra columns are harmless to the previous version.

## 8. Traceability

| Requirement | Operation | Field or rule | Acceptance scenario |
|---|---|---|---|
| One walk feeds counts and languages | `scan_checkout` | sum invariant | Languages sum to the code count; Walk happens once; Public functions unchanged |
| Counts stored on the observation | `scan_workspace` | `code_files`, `documentation_files`, `other_files` | Counts stored; Partial walk; Retention |
| Failed and older have no counts | store | null columns | Failed observation; Upgrade keeps old observations |
| Search filter | `search_projects` | `documentation_only` | Documentation-only projects; Projects with code; Partial; Not counted; Any active; Missing; Combined; Not a boolean |
| Details per checkout | `get_project` | `composition` | Counts per checkout; Counts agree; Not counted is not zero; Partial shows its bound; Indicator follows the counts; Missing keeps counts |
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
