# Interface and Data Contract: be-discover-one-root

- **OpenSpec Change ID:** `be-discover-one-root`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the Python interface that discovers repositories under one root and the shape of the run record. No MCP tool, CLI command, index table, or sync exchange is involved yet.

## 2. Scope

In: `vyasa.application.scanning.discovery.discover_repositories` and the types in `vyasa.domain.discovery`. Out: MCP, SQLite, Google Sheets, provider calls (not affected).

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `discover_repositories(root, options, now, new_id)` | Python function | Lists directories under `root`; opens only `.git` pointer files (at most 1 KiB each); writes nothing; runs nothing | `root: Path or str`, `options: DiscoveryOptions`, `now` and `new_id` callables (defaults: current UTC time, random hex) | `DiscoveryRun` | none; problems are in the record |

`DiscoveryOptions` (defaults): `max_depth = 6`, `exclusions = DISCOVERY_EXCLUSIONS`, `max_issues = 100`.

`DISCOVERY_EXCLUSIONS`: `.git`, `node_modules`, `.venv`, `venv`, `__pycache__`, `build`, `dist`, `target`, `.tox`, `.idea`, `.vscode`, `.cache`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`.

`Candidate`: `path` (`Path`), `outcome`, `kind` (`repository`, `submodule`, `linked_worktree`, or `None`), `reason` (string or `None`).

Outcomes: `eligible`, `excluded`, `inaccessible`, `malformed`, `skipped_by_policy`.

Reason codes: `root_not_found`, `root_not_a_directory`, `root_unreadable`, `unreadable_directory`, `unreadable_git_file`, `missing_head`, `invalid_git_file`, `git_link`, `symlink`, `max_depth`.

`DiscoveryRun`: `run_id`, `root`, `started_at`, `finished_at` (timezone-aware UTC), `status` (`complete`, `partial`, `failed`), `tool_version`, `options`, `counts` (all five outcomes, integers), `repositories` (eligible candidates sorted by path), `issues` (at most `max_issues` non-eligible candidates in walk order), `issues_omitted` (integer).

## 4. Error Model

| Condition | Error code | Response shape | Safe to show the user |
|---|---|---|---|
| Root missing | none | status `failed`, one issue `root_not_found` | Yes |
| Root not a directory | none | status `failed`, issue `root_not_a_directory` | Yes |
| Root cannot be listed | none | status `failed`, issue `root_unreadable` | Yes |
| Directory cannot be listed | none | issue `unreadable_directory`; status `partial` | Yes |
| Bad `.git` entry | none | issue `missing_head`, `invalid_git_file`, `unreadable_git_file`, or `git_link`; status `partial` | Yes |
| Link or depth skip | none | issue `symlink` or `max_depth`; status `partial` | Yes |

No exception is raised for a filesystem problem.

## 5. Trust Boundary

The root comes from validated configuration. Everything under it is untrusted repository content: directory names are compared, never evaluated, and no file is read except a `.git` pointer, parsed as text for one line. No program is run, including Git. Links and junctions are not followed, so nothing outside the root is listed. The record contains absolute local paths: it is local state and must not be returned to agents or synchronized without the path rules.

## 6. Data Model

| Entity | Field | Type | Required | Constraint or invariant |
|---|---|---|---|---|
| DiscoveryRun | `counts` | map outcome to int | Yes | `eligible` equals `len(repositories)`; the others count every candidate, including omitted issues |
| DiscoveryRun | `issues` | tuple | Yes | Length at most `max_issues`; `len(issues) + issues_omitted` equals the number of non-eligible, non-excluded candidates |
| DiscoveryRun | `status` | enum | Yes | `failed` only for a root problem; `partial` iff any of `inaccessible`, `malformed`, `skipped_by_policy` is above zero; otherwise `complete` |
| Candidate | `reason` | string | Yes unless eligible | One of the listed codes |

## 7. Migrations and Backward Compatibility

New. The refactor of the checkout walk (shared pruning) and the root check keeps their behavior; their existing tests guard it. Rollback: revert the change.

## 8. Traceability

| Requirement | Operation | Field or rule | Acceptance scenario |
|---|---|---|---|
| Recognize Git repositories | `discover_repositories` | `kind`, `eligible` | Repository with a Git directory; Repository at the root; Submodule; Linked worktree; Git directory elsewhere; Ordinary directories are not candidates |
| Nested repositories stay separate | `discover_repositories` | `repositories` | Repository inside a repository |
| Every candidate has one closed outcome | `discover_repositories` | `outcome`, `reason` | Git directory without HEAD; Malformed Git file; Unreadable Git file; Unreadable directory |
| Traversal boundaries | `discover_repositories` | `options` | Depth limit; Repository at the depth limit; Excluded directory; Git directory is not counted as excluded; Directory link not followed; Linked Git entry |
| Run status | `discover_repositories` | `status` | Complete run; Partial run; Failed run; Root is not a directory; Unreadable root |
| Run record | `discover_repositories` | all fields | Record contents; Issues are bounded but counted; Repeatable result; Independent of listing order |
| Nothing is executed or read beyond pointers | `discover_repositories` | none | Only pointer files are opened |

## 9. Contract Review

- [x] Every affected operation is listed with request, response, and errors.
- [x] The error model states which conditions produce which error.
- [x] The trust boundary is stated.
- [x] The data model states the invariants.
- [x] Migration and backward compatibility are stated.
- [x] Every requirement in scope is traced.
- [x] No unresolved contract questions.

**Status:** Draft
