# Interface and Data Contract: be-local-index

- **OpenSpec Change ID:** `be-local-index`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the Python interface that opens and migrates the index, stores a discovery run, and reports freshness, and the first schema. No MCP tool, CLI command, or sync exchange is involved yet.

## 2. Scope

In: `vyasa.adapters.sqlite` (open, migrate, lock, repository functions), `vyasa.application.indexing` (store a run), `vyasa.domain.index` (states, error codes, freshness). Out: MCP, CLI, Google Sheets, provider calls (not affected); discovery is unchanged.

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `open_index(path, *, read_only=False, now)` | Python function | Creates the data directory and file unless `read_only`; migrates unless `read_only` | database path | `sqlite3.Connection` configured per §5 | `INDEX_SCHEMA_TOO_NEW`, `INDEX_MIGRATION_FAILED`, `INDEX_UNAVAILABLE` |
| `index_path(environ=None, ...)` | Python function | None; pure | as `data_directory` | `<data directory>/index.sqlite3` | none |
| `store_run(connection, run, *, owner, now)` | Python function | Writes the index; one writer | a `DiscoveryRun` | `StoredRun` (run id, status, counts of added, updated, unchanged, missing, inaccessible) | `OPERATION_IN_PROGRESS`; any storage error after marking the run `interrupted` |
| `list_projects(connection, state=None)` | Python function | Read | optional state | rows ordered by path | none |
| `freshness(connection, now, window=24h)` | Python function | Read; no writes | connection, clock | `current`, `stale`, `partial`, or `unknown` | none |

`StoredRun` counts: `added`, `updated`, `unchanged`, `missing`, `inaccessible`, `restored`.

## 4. Error Model

| Condition | Error code | Response shape | Safe to show the user |
|---|---|---|---|
| Database version above the code's | `INDEX_SCHEMA_TOO_NEW` | `IndexStoreError(code, message)`; file untouched | Yes (versions only) |
| A migration raised | `INDEX_MIGRATION_FAILED` | same; migration id named; rolled back | Yes |
| Directory or file cannot be created or opened | `INDEX_UNAVAILABLE` | same; names the data directory | Yes (local to the person) |
| Live lock held by another writer | `OPERATION_IN_PROGRESS` | same; no owner detail beyond "another refresh is running" | Yes |
| Failure while storing a project | the original exception | run marked `interrupted`; lock released | Not shown raw |

## 5. Trust Boundary

Inputs are the trusted `DiscoveryRun` produced by Vyasa's own discovery and a trusted database path from configuration. Repository content reaches the index only through that run (paths, marker names, the already normalized remote); every SQL value is bound as a parameter, never formatted into a statement. Nothing under a workspace root is opened by this change. The index lives outside every scanned repository.

Machine-local: every table in this change (absolute paths, runs). Nothing here is synchronized.

## 6. Data Model

Timestamps are UTC ISO 8601 text. Enumerations carry `CHECK` constraints.

`projects`

| Field | Type | Notes |
|---|---|---|
| `project_id` | TEXT PRIMARY KEY | opaque, created once (uuid4 hex), never recomputed |
| `display_name` | TEXT NOT NULL | directory name; not unique |
| `state` | TEXT NOT NULL | `active`, `missing`, `inaccessible` |
| `created_at`, `updated_at`, `last_seen_at` | TEXT NOT NULL | |

`checkouts`

| Field | Type | Notes |
|---|---|---|
| `checkout_id` | INTEGER PRIMARY KEY | |
| `project_id` | TEXT NOT NULL | FK to `projects`, no cascade delete |
| `path` | TEXT NOT NULL | absolute, as discovered |
| `path_key` | TEXT NOT NULL UNIQUE | `os.path.normcase` of `path`; the match key |
| `root` | TEXT NOT NULL | the scanned root that found it |
| `kind` | TEXT | repository, submodule, linked_worktree, project |
| `markers` | TEXT NOT NULL | JSON array of names |
| `git` | TEXT | `.` or a child folder name |
| `remote_provider`, `remote_host`, `remote_identity` | TEXT | credential-free; NULL when none |
| `remote_status` | TEXT | origin, only, ambiguous, none, unavailable |
| `state` | TEXT NOT NULL | same values as the project |
| `first_seen_at`, `last_seen_at` | TEXT NOT NULL | |
| `last_run_id` | TEXT | FK to `scan_runs` |

`scan_runs`: `run_id` TEXT PK, `root` TEXT, `status` (`running`, `completed`, `partial`, `failed`, `interrupted`), `tool_version`, `started_at`, `finished_at` (NULL while running), `counts` JSON.

`index_lock`: single row (`id` = 1 enforced), `owner` TEXT, `run_id` TEXT, `heartbeat_at` TEXT. Absent when no run holds it.

Invariants: one checkout per `path_key`; every checkout has a project; no row is deleted by a scan; a `partial` or `failed` run never sets `missing`; `project_id` never changes; `PRAGMA user_version` equals the highest applied migration.

Discovery's `complete` is stored as `completed`, matching the unified run-status vocabulary.

## 7. Migration and Compatibility

First schema: migration `0001_initial.sql`, version 1. Later changes append numbered files; none edits an applied one. A backup (`index.sqlite3.bak-v<old>`) is made with the SQLite backup API before any pending migration on an existing file. No MCP client, sheet, or earlier index exists, so there is nothing to keep compatible; identity and observations arrive as additive migrations.

## 8. Traceability

| Requirement | Operation / table |
|---|---|
| The database is created safely | `open_index`, `index_path` |
| Migrations are forward-only | `open_index`, `schema` version, `INDEX_*` errors |
| Discovered projects are stored | `store_run`, `projects`, `checkouts` |
| Rescans do not duplicate | `checkouts.path_key` |
| A vanished project is marked | `store_run`, `state` columns |
| Runs have a visible lifecycle | `scan_runs` |
| One writer at a time | `index_lock`, `OPERATION_IN_PROGRESS` |
| Freshness is reported | `freshness` |
| The index works offline | all |

## 9. Open Contract Questions

- [ ] Whether `store_run` should also accept a run from several roots at once. This change stores one root per call; each root is a separate run.
