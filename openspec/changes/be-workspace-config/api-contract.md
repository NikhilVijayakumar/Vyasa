# Interface and Data Contract: be-workspace-config

- **OpenSpec Change ID:** `be-workspace-config`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the Python interface that loads workspace roots and checks them, and the configuration file format. No MCP tool, CLI command, index table, or sync exchange is involved.

## 2. Scope

In: `vyasa.application.configuration.workspace` and the result types in `vyasa.domain.workspace_config`. Out: MCP, SQLite, Google Sheets, provider calls (not affected).

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `data_directory(environ, home, platform)` | Python function | None; pure | `environ: Mapping[str, str]`, `home: Path`, `platform: str` | `Path` | none |
| `load_workspace_config(explicit, environ, home, platform)` | Python function | Reads one TOML file; writes nothing | `explicit: Path or None`, and the same environment inputs, all defaulting to the running process | `WorkspaceConfig` or `NotConfigured` | `ConfigError` |
| `check_roots(config)` | Python function | Lists each root directory once; opens no file | `WorkspaceConfig` | tuple of `RootCheck`, one per root, in order | none |

Result types:

- `WorkspaceConfig`: `roots` (tuple of absolute `Path`), `source` (the file read), `warnings` (tuple of strings).
- `NotConfigured`: `reason` (string).
- `RootCheck`: `root` (`Path`), `status` (`accessible`, `missing`, `not_a_directory`, or `unreadable`).
- `ConfigError(ValueError)`: `problems` (non-empty tuple of strings); its message lists them.

The file is read as UTF-8; a leading byte-order mark is ignored. Environment variables and `~user` forms are not expanded; only a leading `~` is.

Configuration file:

```toml
[workspace]
roots = ["E:/Python", "D:/Projects", "~/work"]
```

`VYASA_HOME` and `VYASA_CONFIG` are the only environment variables read. On Windows write paths with forward slashes or single-quoted literal strings.

## 4. Error Model

| Condition | Error code | Response shape | Safe to show the user |
|---|---|---|---|
| Explicit or `VYASA_CONFIG` file missing | `ConfigError` | problem names the file | Yes |
| File unreadable or not valid TOML | `ConfigError` | problem names the file and the parser message | Yes |
| Unknown top-level or `workspace` key | `ConfigError` | problem names the key | Yes |
| `workspace` not a table, `roots` not a list, or a root not a string | `ConfigError` | problem names the setting | Yes |
| Relative root | `ConfigError` | problem names the value | Yes |
| No file at the default location | none | `NotConfigured` | Yes |
| `roots` empty or absent | none | `NotConfigured` | Yes |
| A root missing, not a directory, or unreadable | none | `RootCheck.status` | Yes |

All problems found are collected into one `ConfigError`.

## 5. Trust Boundary

The configuration file is trusted user configuration, but it is validated as a whole before use. Roots are the only places later scanning may read. The functions never scan, follow, or open anything under a root; `check_roots` only lists each root once. Roots are machine-local paths: they are not synchronized and not returned to agents by default. The file holds no credentials.

## 6. Data Model

| Entity | Field | Type | Required | Constraint or invariant |
|---|---|---|---|---|
| File | `workspace.roots` | list of strings | No | Each absolute after `~` expansion; empty or absent means not configured |
| File | any other key | any | No | Rejected |
| WorkspaceConfig | `roots` | tuple of `Path` | Yes | Non-empty, absolute, normalized, unique by `normcase`, in first-appearance order |

## 7. Migrations and Backward Compatibility

New. Later settings add known keys; an older reader rejects them, which is intended. Rollback: revert the change.

## 8. Traceability

| Requirement | Operation | Field or rule | Acceptance scenario |
|---|---|---|---|
| Locate the configuration file | `data_directory`, `load_workspace_config` | resolution order | Explicit path wins; Environment variable next; Default location; Platform data directories; Home override; Explicit file missing |
| Load several workspace roots | `load_workspace_config` | `roots` | Multiple roots; Duplicates merged; Home expansion; Nested roots kept and reported |
| Not configured | `load_workspace_config` | `NotConfigured` | No file at the default location; Empty roots |
| Invalid configuration is rejected as a whole | `load_workspace_config` | `ConfigError` | Syntax error; Unknown key; Wrong type; Relative root; All problems together |
| Each root is checked on its own | `check_roots` | `RootCheck` | One missing root; File instead of directory; Unreadable root |

## 9. Contract Review

- [x] Every affected operation is listed with request, response, and errors.
- [x] The error model states which conditions produce which error.
- [x] The trust boundary is stated.
- [x] The data model states the invariants.
- [x] Migration and backward compatibility are stated.
- [x] Every requirement in scope is traced.
- [x] No unresolved contract questions.

**Status:** Draft
