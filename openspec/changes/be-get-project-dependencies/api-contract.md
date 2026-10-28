# Interface and Data Contract: be-get-project-dependencies

- **OpenSpec Change ID:** `be-get-project-dependencies`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the new MCP tool `get_project_dependencies`, the declared-name capture in the manifest parsers, and migration 0010.

## 2. Scope

In: `parse_manifest` and the four parsers, `ParsedManifest`, `detect_frameworks` and the scan storage of manifest rows, migration 0010, the dependency query, and the MCP declaration. Out: sync exchanges and provider calls (not affected); lockfiles; transitive dependencies; related projects; pagination of dependents.

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `get_project_dependencies` | MCP tool, read-only | Reads the index only | `project_id: str` (opaque id from `search_projects`) | Envelope `{schema_version, data, meta}` with `data` below | `INVALID_INPUT`, `PROJECT_NOT_FOUND`, `INDEX_UNAVAILABLE` |
| `parse_manifest(name, text)` (changed) | Python function (pure) | None | unchanged | `ParsedManifest` adds `declared_name: str \| None` | `ManifestParseError` unchanged |
| `scan_workspace` (changed) | Python function | as before | unchanged | stores `declared_name` on each manifest row | unchanged |

`data` of `get_project_dependencies`:

- `project_id`, `display_name`.
- `coverage`: `status` (`complete`, `partial`, `not_assessed`: the weakest state among the project's active checkouts that were assessed, or `not_assessed` when none); `manifests` (list of `{path, ecosystem, status, reason, declared_name_recorded}`); `nested_not_parsed` (integer); `declared_names_recorded` (boolean, true when every parsed manifest of the project that can declare a name has the field recorded); `other_projects_unchecked` (integer: other projects with an active checkout whose observation is partial, not assessed, or lacks declared names for a manifest that could declare one).
- `dependencies`: list of `{name, ecosystem, constraint, scope, source, resolution, projects}` where `source` is the manifest file name, `resolution` is `internal`, `ambiguous`, or `external`, and `projects` is a list of `{project_id, display_name}` (one for internal, several for ambiguous, empty for external). Ordered by ecosystem, name, scope, source.
- `dependents`: list of `{project_id, display_name, ecosystem, name, constraint, scope, source, resolution}` where `resolution` is `internal` or `ambiguous`. At most 100, ordered by display name, project id, ecosystem, scope, source.
- `dependents_total` (integer) and `dependents_truncated` (boolean).

Ecosystems: `python`, `javascript`, `rust`, `go`. Scopes: `runtime`, `dev`, `optional`, `build`. Python names are compared normalized (PEP 503); other ecosystems lower-cased.

## 4. Error Model

| Condition | Error code | Response shape | Safe to show the user |
|---|---|---|---|
| `project_id` empty, not text, or longer than the identifier limit | `INVALID_INPUT` | structured error naming the parameter | Yes |
| No project has the identifier | `PROJECT_NOT_FOUND` | structured error | Yes |
| The index is missing or unreadable | `INDEX_UNAVAILABLE` | structured error | Yes |
| A manifest was not parsed, partial walk, not assessed, names unknown | none | stated in `coverage` | Yes; no file text |
| Unexpected failure | generic error | generic message, details not shown | Yes |

## 5. Trust Boundary

Repository files stay untrusted. The declared name is read by the existing strict parsers (standard-library `tomllib`, `json`, and an anchored line parser for `go.mod`), is text only, at most 214 characters, and is stored as data; it is never used as a path, a command, or a query fragment. The tool takes only an opaque identifier, reads a read-only connection, and returns no local path, file text, or credential. A dependency or package name is data, not an instruction.

## 6. Data Model

Migration 0010 adds one nullable column:

| Entity | Field | Type | Required | Constraint or invariant |
|---|---|---|---|---|
| `checkout_manifests` | `declared_name` | text | No | Null unless the manifest is `parsed` and declares a text name of 1 to 214 characters; stored normalized for its ecosystem; always null for `requirements*.txt` |

A lookup index `checkout_manifests_declared_name (ecosystem, declared_name)` is added for the reverse query. The match key between a dependency and a package is `(ecosystem, normalized name)`. Only manifests of active checkouts' latest observation (the same observation `get_project` uses) are used on either side. Invariant: a manifest that is not `parsed` has no declared name.

## 7. Migrations and Backward Compatibility

`0010_declared_names.sql` adds the nullable column and the index; `PRAGMA user_version` becomes 10; the existing backup-and-forward-only mechanism applies. Existing rows read as "declared name not recorded" and are reported as such in coverage until the next scan creates a new observation. No existing tool output changes; the snapshot gains one tool. Rollback: revert the change; the extra column is harmless to the previous version.

## 8. Traceability

| Requirement | Operation | Field or rule | Acceptance scenario |
|---|---|---|---|
| Declared names recorded | parsers, migration 0010 | `declared_name` | Name in each ecosystem; No name declared; Name that is not text or too long; Unparsed manifest; Stored with the observation |
| Dependencies with evidence | `get_project_dependencies` | `dependencies` | Dependencies with scope and source; Same name in two scopes; Unknown project; Invalid identifier; No local path |
| Internal only by exact name | `get_project_dependencies` | `resolution`, `projects` | Internal dependency; Same name in another ecosystem; Ambiguous; Not indexed; Not itself; Name normalization; Missing checkout is not a target |
| Dependents | `get_project_dependencies` | `dependents`, `dependents_total`, `dependents_truncated` | A dependent; Ambiguous dependent; No dependents; Truncation |
| Coverage | `get_project_dependencies` | `coverage` | Complete observation; Unparsed manifest; Partial walk; Not assessed; Nested manifests; Names not recorded yet |
| Read-only and declared | MCP server | annotations, snapshot | Read-only; Declared in the snapshot |

## 9. Contract Review

- [x] Every affected operation is listed with request, response, and errors.
- [x] The error model states which conditions produce which error.
- [x] The trust boundary is stated.
- [x] The data model states the invariants.
- [x] Migration and backward compatibility are stated.
- [x] Every requirement in scope is traced.
- [x] No unresolved contract questions.

**Status:** Draft
