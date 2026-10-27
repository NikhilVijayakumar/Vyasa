# Interface and Data Contract: be-project-query-basics

- **OpenSpec Change ID:** `be-project-query-basics`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the three query functions, their inputs and outputs, the envelope, and the errors. They are the logical contract the MCP tools of the same names will expose; the transport is a later change.

## 2. Scope

In: `vyasa.application.query`. Out: MCP, CLI, Sheets, provider calls (not affected); `get_project_context`, `find_related_projects`, `get_project_dependencies`.

## 3. Interface Surface

All functions take a read-only `sqlite3.Connection` and a clock, and never write.

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `search_projects(connection, *, query=None, state=None, provider=None, identity_status=None, limit=20, cursor=None, include_paths=False, now=None)` | Python function | Read | see below | envelope; `data` = `{"projects": [...], "page": {"limit", "next_cursor", "has_more"}}` | `INVALID_INPUT`, `INVALID_CURSOR` |
| `get_project(connection, project_id, *, include_paths=False, now=None)` | Python function | Read | project id | envelope; `data` = project record | `INVALID_INPUT`, `PROJECT_NOT_FOUND` |
| `get_index_status(connection, *, now=None)` | Python function | Read | none | envelope; `data` = status | none |

Inputs: `query` string, 1 to 200 characters; `state`, `provider`, `identity_status` each a list of allowed values (a single string is accepted as one value); `limit` integer 1 to 100; `cursor` string; `include_paths` boolean; `project_id` non-empty string.

Allowed values: `state`: `active`, `missing`, `inaccessible`. `identity_status`: `resolved`, `provisional`, `ambiguous`. `provider`: `github`, `bitbucket`, `gitlab`, `other`, `local`, `none` (a checkout with no stored provider counts as `none`).

Search result item: `project_id`, `display_name`, `state`, `identity_status`, `providers` (sorted, distinct), `has_open_candidates` (boolean), `matched` (sorted list of `display_name` and/or `remote_identity`; empty when no query).

Project record: `project_id`, `display_name`, `state`, `identity` (`status`, `source`, `aliases` sorted), `checkouts` (list ordered by first seen then id: `state`, `kind`, `markers`, `git`, `remote` (`provider` or `"none"`, `host`, `identity`, `status`), `first_seen_at`, `last_seen_at`, `path` only with `include_paths`), `review_candidates` (`kind`, `rule`, `confidence`, `criteria`, `review_status`), `created_at`, `updated_at`, `last_seen_at`.

Status: `freshness`, `schema_version`, `latest_run` (`status`, `finished_at`, `counts`) or `null`, `projects` (`total`, `active`, `missing`, `inaccessible`), `open_candidates`.

Envelope: `{"schema_version": "1", "data": ..., "meta": {"generated_at", "index_version", "freshness"}}`; times ISO 8601 UTC.

## 4. Error Model

| Condition | Error code | Response shape | Safe to show the user |
|---|---|---|---|
| Bad type, range, or unknown filter value | `INVALID_INPUT` | `IndexStoreError(code, message)`; message names the field and allowed values | Yes |
| Cursor not issued by the system | `INVALID_CURSOR` | same | Yes |
| Unknown project id | `PROJECT_NOT_FOUND` | same | Yes |

The MCP layer will map these to structured tool results.

## 5. Trust Boundary

Inputs are untrusted (they come from an agent): validated, bounded, and bound as parameters; `LIKE` wildcards in `query` are escaped. Results contain repository-derived text (display names, remote identities, markers); consumers treat it as data. Absolute paths and scanned roots are omitted unless `include_paths` is true, which the MCP layer will set only from local configuration, never from tool input.

## 6. Data Model

No schema change. Reads `projects`, `checkouts`, `project_aliases`, `review_flags`, `review_decisions`, `scan_runs`.

Cursor: base64url of the JSON `[lower(display_name), project_id]` of the last item.

## 7. Migration and Compatibility

None. Additive surface.

## 8. Traceability

| Requirement | Operation |
|---|---|
| Search is deterministic and bounded | `search_projects` |
| Search matches text and filters | `search_projects` |
| Project details carry identity and review state | `get_project` |
| Index status reports reliability | `get_index_status` |
| Queries are read-only and omit local paths | all |

## 9. Open Contract Questions

- [ ] Final MCP tool schema names for the filters once detectors add more.
