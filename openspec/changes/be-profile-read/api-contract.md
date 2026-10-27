# Interface and Data Contract: be-profile-read

- **OpenSpec Change ID:** `be-profile-read`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the profile schema, the reader, the stored shape, and the `get_project` addition.

## 2. Scope

In: `vyasa.domain.profile`, `vyasa.adapters.filesystem.profile_file`, `Candidate.profile`, migration `0005`, the profile section of `get_project`. Out: MCP tool list (unchanged; `get_project` output grows), Sheets, provider calls (not affected).

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `validate_profile(data)` | Python function | None; pure | parsed TOML mapping | `ProfileResult(status, fields, problems)` | none |
| `read_profile(directory)` | Python function | Reads `<directory>/.vyasa/project-profile.toml`, at most 64 KiB + 1 byte | project directory | `ProfileResult` | none; problems are statuses |
| `discover_repositories(...)` | Python function | as before, plus the profile read | unchanged | candidates carry `profile` | none |
| `get_project(...)` | Python function / MCP tool | Read | unchanged | record gains `profile` | unchanged |

Schema version 1 (file `.vyasa/project-profile.toml`):

| Field | Type | Rule |
|---|---|---|
| `schema_version` | integer | required, must be 1 |
| `name` | string | 1 to 100 characters |
| `purpose` | string | 1 to 500 characters |
| `lifecycle` | string | `active`, `maintenance`, `experimental`, `deprecated`, `archived` |
| `domain`, `tags`, `technologies` | list of strings | at most 20 items, each 1 to 64 characters, duplicates removed |
| `owners` | list of strings | at most 20 items, each 1 to 100 characters |
| `related_projects` | array of tables | at most 20; each has `identity` (1 to 200 characters) and `relation` (`depends_on`, `used_by`, `related`) |
| `documentation.entry_point` | string | 1 to 200 characters, relative, no `..`, no drive letter, no leading separator |

Status values: `valid`, `invalid` (some field problem, valid fields kept), `unsupported` (missing or other `schema_version`; nothing kept), `unreadable` (link, oversize, not a regular file, not TOML, I/O error), `absent`.

`get_project` addition: `profile` = `{"status", "source": ".vyasa/project-profile.toml", "declared": {field: {"value", "status": "declared"}}, "problems": [{"field", "reason"}]}`; `declared` omits fields that were not given or not valid.

## 4. Error Model

No error codes; every problem is a profile status plus problems. The scan never fails because of a profile.

## 5. Trust Boundary

The profile is untrusted repository text. It is size-capped, parsed by `tomllib` (no code execution), validated per field, stripped of control characters, length-capped, and stored and returned as typed data. It is never interpreted as instructions; the MCP server instructions already say results are data. Problem messages are fixed strings that do not echo file content beyond the field name. The file is never written, copied, or followed through a link.

Machine-local data: the stored profile rows (they are repository-derived but belong to this index).

## 6. Data Model

`checkout_profiles`: `checkout_id` INTEGER PRIMARY KEY, FK to `checkouts`; `status` (`valid`, `invalid`, `unsupported`, `unreadable`, `absent`); `fields` JSON object (valid fields only); `problems` JSON array of `{field, reason}`; `read_at` TEXT; `run_id` TEXT FK.

Invariants: one row per checkout; replaced on every scan that reaches the checkout; `fields` holds only validated values; no row is deleted.

## 7. Migration and Compatibility

`0005_checkout_profiles.sql` creates the table; existing checkouts have no row and read as `absent` until rescanned. Backup precedes it (runner). `Candidate.profile` defaults to `None`, stored as `absent`.

## 8. Traceability

| Requirement | Operation / table |
|---|---|
| The profile is read safely | `read_profile` |
| Fields are validated one by one | `validate_profile` |
| Declared values keep their source | `checkout_profiles` |
| Project details show the profile | `get_project` |

## 9. Open Contract Questions

- [ ] Relation vocabulary growth for `related_projects`.
