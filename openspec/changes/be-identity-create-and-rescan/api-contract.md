# Interface and Data Contract: be-identity-create-and-rescan

- **OpenSpec Change ID:** `be-identity-create-and-rescan`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the identity fields, tables, and matching rules added to the index. No MCP tool, CLI command, or sync exchange is involved yet.

## 2. Scope

In: migration `0002`, `vyasa.adapters.sqlite.projects` (matching), `vyasa.domain.index` (identity constants). Out: MCP, CLI, Sheets, provider calls (not affected); `store_run`'s signature is unchanged.

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `store_run(...)` | Python function | Writes the index | unchanged | `StoredRun`; counts gain `attached` (a new checkout on an existing project) and `conflicts` | as before |
| `list_projects(...)` | Python function | Read | unchanged | rows gain `identity_status` and `identity_source` | none |
| `list_aliases(connection, project_id)` | Python function | Read | project id | alias values in first-seen order | none |
| `list_events(connection, project_id)` | Python function | Read | project id | events in order | none |

Counts: `added` = new project, `attached` = new checkout on an existing project, `restored`, `updated`, `unchanged`, `missing`, `inaccessible`, `conflicts`.

## 4. Error Model

No new error codes. Conflicting evidence is data (an event), not an error.

## 5. Trust Boundary

Inputs are the trusted candidate fields already produced by discovery; the remote identity is already credential-free. All SQL is parameterized. Aliases and events hold no absolute path and no URL, so they are safe to synchronize later. Checkout paths stay in `checkouts`, machine-local.

## 6. Data Model

`projects` gains:

| Field | Type | Notes |
|---|---|---|
| `identity_status` | TEXT NOT NULL | `resolved`, `provisional` (default `provisional`); `ambiguous` is reserved for the ambiguity change |
| `identity_source` | TEXT NOT NULL | `remote`, `path` (default `path`) |

`project_aliases`: `alias_kind` TEXT (`remote`), `alias_value` TEXT, `project_id` FK, `first_seen_at`; PRIMARY KEY (`alias_kind`, `alias_value`).

`identity_events`: `event_id` INTEGER PK, `project_id` FK, `kind` (`created`, `alias_added`, `identity_conflict`), `detail` JSON text, `run_id` FK, `at`.

Invariants: an alias belongs to exactly one project; `project_id` never changes; no row is deleted; a `resolved` project has at least one alias; `projects.state` is derived: `active` if any checkout is active, else `inaccessible` if any is, else `missing`.

Matching: alias (if the candidate has `remote.identity`), then `path_key`. Alias hit and path miss: new checkout on the alias's project. Path hit and alias miss: add the alias to the path's project. Both hit, same project: update. Both hit, different projects: event only.

## 7. Migration and Compatibility

`0002_identity.sql`, schema 1 to 2, backed up first by the existing runner. Backfill: aliases from `checkouts.remote_identity` (earliest checkout wins), `resolved/remote` for projects that received one. Nothing is deleted. Callers of `store_run` and `list_projects` keep working; rows only gain columns.

## 8. Traceability

| Requirement | Operation / table |
|---|---|
| Identity is created once | `store_run`, `projects.identity_*`, `project_aliases` |
| Found by alias, then path | matching in `projects.upsert` |
| Later evidence becomes an alias | `project_aliases`, `identity_events` |
| Conflicting evidence is preserved | `identity_conflict` event |
| Identity changes are recorded | `identity_events` |
| Existing indexes are migrated | `0002_identity.sql` |

## 9. Open Contract Questions

- [ ] Whether `ambiguous` should be set by this change for the conflict case. Chosen: no; the event is the record, and the status is set by the ambiguity change.
