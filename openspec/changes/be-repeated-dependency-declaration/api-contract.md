# Interface and Data Contract: be-repeated-dependency-declaration

- **OpenSpec Change ID:** `be-repeated-dependency-declaration`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/framework-detection/spec.md`
- **Related design:** `design.md`

## 1. Purpose

Keep the stored dependency rows consistent with the primary key migration 0009 already declares, so a manifest that repeats a declaration can be indexed instead of aborting the scan. No MCP tool, CLI command, or error code changes.

## 2. Scope

Affected: the write of `checkout_dependencies` during a scan, through `vyasa scan`.
Excluded: the eight MCP tools, the CLI surface, the schema version, the sync format, and every read path.

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `vyasa scan` | CLI | Configured workspace roots and the data directory | `config.toml` roots, repository files | Per-root summary and exit code; dependency rows written | Unchanged: `2` configuration, `3` lock held, `4` index problem, `1` partial or failed |
| `get_project`, `get_project_dependencies` | MCP tool | Read-only index access | `project_id` | Dependencies read from `checkout_dependencies`; shape unchanged | Unchanged: `INVALID_INPUT`, `PROJECT_NOT_FOUND`, `INDEX_UNAVAILABLE` |

Reading a project whose manifest repeats a declaration returns the kept rows only: one row per name and scope, with the first declaration's constraint.

## 4. Error Model

No new error code and no change to existing ones. The condition that used to escape as an unhandled `sqlite3.IntegrityError` and killed the scan is now handled by keeping one row.

| Condition | Error code | Response shape | Safe to show the user |
|---|---|---|---|
| A manifest repeats a name and scope | None; the repeat is not stored | Scan continues, exit code unchanged | Yes |
| A dependency violates a table constraint (scope, foreign key) | None of this contract's; the exception still propagates as today | Unchanged | No; it is an internal defect signal |
| Index missing or unreadable | `INDEX_UNAVAILABLE` | `{"error": {"code", "message"}}` | Yes |

## 5. Trust Boundary

Repository content stays untrusted: manifest text is parsed as data, never executed, and the stored row holds only the name, the constraint text as written, and a scope from a fixed vocabulary. The change reads nothing new, opens no path outside the configured roots, and adds no network or credential use. Rows remain machine-local in `index.sqlite3`; nothing is synchronized.

## 6. Data Model

| Entity | Field | Type | Required | Constraint or invariant |
|---|---|---|---|---|
| `checkout_dependencies` | `observation_id`, `path` | INTEGER, TEXT | Yes | Foreign key to `checkout_manifests`, cascade on delete |
| `checkout_dependencies` | `name` | TEXT | Yes | Non-empty, at most 214 characters, normalized for its ecosystem |
| `checkout_dependencies` | `constraint_text` | TEXT | No | As written, at most 256 characters, never a URL |
| `checkout_dependencies` | `scope` | TEXT | Yes | One of `runtime`, `dev`, `optional`, `build` |

Integrity rules the persistence layer must guarantee:

- At most one row per `(observation_id, path, name, scope)`; the writer collapses repeats before the insert rather than relying on the key to fail.
- At most 200 rows per manifest, with `checkout_manifests.total_dependencies` unchanged as the number of declared entries.
- A violated constraint other than the repeat still raises: the key is not relaxed and no `INSERT OR IGNORE` is used.

No field is added, removed, or retyped; no data-ownership entry changes.

## 7. Migrations and Backward Compatibility

No migration. The schema version stays at 11. Existing indexes are read and written exactly as before; rows already stored are untouched. An index left `partial` by the failure needs no repair beyond one successful `vyasa scan`, which upserts the affected checkouts. Rollback is reverting the store change: the schema and stored data remain valid either way.

## 8. Traceability

| Requirement | Operation | Field or rule | Acceptance scenario |
|---|---|---|---|
| REQ-001 | `vyasa scan` writes dependencies | One row per `(name, scope)`, first constraint kept | Declared twice in one scope |
| REQ-002 | `vyasa scan` writes dependencies | Scopes are not merged | Same name in two scopes |
| REQ-003 | `vyasa scan` writes dependencies | Other manifests unaffected | Repeat does not disturb other manifests |

## 9. Contract Review

- [x] Every affected operation is listed with request, response, and errors.
- [x] The error model states which conditions produce which error.
- [x] The trust boundary is stated per operation, including out-of-root and credential failures.
- [x] The data model states the invariants the index must hold.
- [x] Migration and backward compatibility are stated.
- [x] Every requirement in scope is traced to an operation or rule.
- [x] Unresolved contract questions are recorded as explicit open questions.

**Status:** Ready for design
