# Interface and Data Contract: be-framework-detector

- **OpenSpec Change ID:** `be-framework-detector`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the registry data, the strict reader, the parsers and detector, the new index storage, the added `search_projects` parameter, the added `get_project` field, and their errors.

## 2. Scope

In: `technologies.json`, `load_registry`, `read_manifest`, the parsers, `detect_frameworks`, `scan_checkout`, `scan_workspace`, migration 0009, `search_projects`, `get_project`, and the MCP declarations. Out: sync exchanges and provider calls (not affected); no new tool.

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `load_registry(path)` | Python function | Reads one JSON file | `path: Path` | `TechnologyRegistry` | `RegistryError` naming the field |
| `read_manifest(root, name, limit)` | Python function | `lstat` and one bounded binary read of one root file; never follows a link | root, file name, byte limit | `ManifestRead(text, status, reason)` | none; failures are statuses |
| `parse_manifest(name, text)` | Python function (pure) | None | file name and text | `ParsedManifest(dependencies, skipped, workspace)` | `ManifestParseError(reason)` with `reason` in `syntax`, `encoding`, `structure`, `too_deep` |
| `detect_frameworks(root, files, stopped_by, registry, limit)` | Python function | reads supported root manifests via `read_manifest` | the walk's relative file paths | `FrameworkReport` | none |
| `scan_checkout(..., frameworks=None)` (changed) | Python function | as before plus the manifest reads | adds optional `frameworks: TechnologyRegistry` | `CheckoutScan` adds `frameworks: FrameworkReport \| None` (None when no registry given) | `ValueError` as before |
| `scan_workspace` (changed) | Python function | as before | unchanged | unchanged | a detection failure is a stored result, not an error |
| `search_projects` (changed) | MCP tool, read-only | Reads the index | adds `technology: list[str] \| str \| None` | unchanged items | `INVALID_INPUT` for an unknown key |
| `get_project` (changed) | MCP tool, read-only | Reads the index | unchanged | each checkout adds `frameworks` (below) | unchanged |

Supported root file names: `pyproject.toml`, `requirements*.txt` (any root file matching, case-insensitive), `package.json`, `Cargo.toml`, `go.mod`. Ecosystems: `python`, `javascript`, `rust`, `go`. Manifest statuses: `parsed`, `malformed`, `too_large`, `unreadable`. Reasons: `syntax`, `encoding`, `structure`, `too_deep` (malformed); `link`, `not_file`, `io` (unreadable); none for `parsed` and `too_large`. Scopes: `runtime`, `dev`, `optional`, `build`.

`frameworks` object of a checkout: `status` (`complete`, `partial`, `not_assessed`), `registry_version` (integer or `null`), `stopped_by`, `observed_at`, `ecosystems` (for each of the four: `{ecosystem, state, manifests, nested_not_parsed}` where `state` is `detected`, `not_detected` only when `complete`, or `unknown` when `partial` and no root manifest was seen; each manifest is `{path, status, reason, total_dependencies, skipped, workspace, dependencies: [{name, constraint, scope}]}` with at most 200 dependencies), and `technologies` (`[{key, name, category, scopes, manifests}]` sorted by key; `name` and `category` come from the current registry and are `null` when the key is no longer in it). A `not_assessed` checkout has empty `ecosystems` and `technologies`.

## 4. Error Model

| Condition | Error code | Response shape | Safe to show the user |
|---|---|---|---|
| Registry unreadable, not JSON, wrong shape, duplicate key, unknown ecosystem, or a dependency claimed twice | `RegistryError` | message names the file and field | Yes |
| `technology` not a string or list of strings, empty, or an unknown key | `INVALID_INPUT` | message names the value and lists allowed keys | Yes |
| A manifest cannot be read or parsed | none | per-manifest status and fixed reason | Yes; no file text |
| Detection raises for a checkout | none | failed observation, no registry version, no rows; run partial | Yes; the exception text is not stored |

Other errors are unchanged.

## 5. Trust Boundary

Repository files are untrusted. The reader opens only regular files at the checkout root, found in the walk's own list, never a link, reads at most 1 MiB in binary, and decodes strictly; parsers are standard-library `tomllib`, `json`, and small line parsers, none of which evaluate content; all parser exceptions become a fixed reason. No repository code is executed or imported and `setup.py` is never opened. Stored data are names, constraints, scopes, counts, statuses, and fixed codes — never file text and never an absolute path. Filter values are validated against the registry keys and bound as parameters. Frameworks are machine-local and are not part of any sync export.

## 6. Data Model

Registry (JSON, `src/vyasa/data/technologies.json`): `version` (integer at least 1); `technologies` (list of `{key, name, category, ecosystem, dependencies}`; `key` lower-case with no spaces; `dependencies` a non-empty list of names as they appear in that ecosystem; a dependency belongs to one entry per ecosystem); `ubiquitous` (list of keys that exist).

Migration 0009 adds:

| Entity | Field | Type | Required | Constraint or invariant |
|---|---|---|---|---|
| `language_observations` | `frameworks_version` | integer | No | At least 1; null means not assessed (older or failed) |
| `checkout_manifests` | `observation_id`, `path` | integer, text | Yes | Primary key; cascade on delete; `path` is a root file name |
| | `ecosystem` | text | Yes | One of the four |
| | `status`, `reason` | text | Yes, No | Status one of four; reason null exactly for `parsed` and `too_large` |
| | `total_dependencies`, `skipped` | integer | Yes | At least 0 |
| | `workspace` | integer | Yes | 0 or 1 |
| `checkout_dependencies` | `observation_id`, `path`, `name`, `scope` | | Yes | Primary key; at most 200 rows per manifest; cascade from the manifest |
| | `constraint_text` | text | No | As declared |
| `checkout_technologies` | `observation_id`, `key` | | Yes | Primary key; index on `key` |
| | `scopes`, `manifests` | text (JSON lists) | Yes | Sorted, non-empty |
| `checkout_nested_manifests` | `observation_id`, `ecosystem` | | Yes | Primary key |
| | `count` | integer | Yes | Positive |

Invariant: a failed observation has no `frameworks_version` and no rows. A manifest with status other than `parsed` has no dependencies and contributes no technology.

## 7. Migrations and Backward Compatibility

`0009_frameworks.sql` adds a nullable column and four tables; `PRAGMA user_version` becomes 9. Existing rows are untouched and read as `not_assessed`. `scan_checkout` called without a registry behaves as before. Rollback: revert the change; the extra column and tables are harmless to the previous version.

## 8. Traceability

| Requirement | Operation | Field or rule | Acceptance scenario |
|---|---|---|---|
| Strict reading | `read_manifest` | link, size, encoding | Regular root file; Symbolic link; Oversized file; Not UTF-8; Setup script is never read |
| Per-manifest status | `parse_manifest`, `detect_frameworks` | `status`, `reason` | Truncated TOML; Deeply nested JSON; Wrong structure; One bad file among good ones |
| Scoped capped dependencies | parsers | `scope`, `skipped`, cap | Python scopes; Poetry tables; JavaScript scopes; Rust scopes; Go direct and indirect; Requirements file scope; Requirements lines; Constraint kept; Names normalized; Cap; Workspace flag |
| Registry technologies | `detect_frameworks` | `technologies` | Known dependency; Scopes are united; Same technology from two manifests; Unknown dependency; Ecosystems do not mix |
| Ecosystem states | read model | `state` | Complete and empty; Partial walk; Malformed is detected |
| Nested manifests | `detect_frameworks` | `nested_not_parsed` | Monorepo |
| Stored on the observation | `scan_workspace` | the four tables | Stored with the observation; Retention; Older and failed; Detection failure is isolated |
| Registry validated | `load_registry` | shape | Valid registry; Malformed registry |
| Search by technology | `search_projects` | `technology` | One technology; Several keys; Case; Dev declaration; Any active; Missing; Malformed or not assessed; Combined; Unknown key |
| Details per checkout | `get_project` | `frameworks` | Per checkout; Ecosystem states; Partial; Not assessed; Evidence shown; No text and no absolute path; Missing keeps frameworks |
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
