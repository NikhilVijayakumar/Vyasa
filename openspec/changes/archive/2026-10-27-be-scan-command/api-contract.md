# Interface and Data Contract: be-scan-command

- **OpenSpec Change ID:** `be-scan-command`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the command line, the orchestration function, the report, and the exit codes.

## 2. Scope

In: `vyasa.adapters.cli`, `vyasa.application.indexing.scan`, `pyproject.toml`. Out: MCP, Sheets, provider calls (not affected).

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `vyasa scan [--config PATH]` | CLI command (also `python -m vyasa scan`) | Reads the configured roots (read-only); writes the data directory and index | optional configuration path | report on standard output; exit code | see below |
| `scan_workspace(config, connection, *, owner, discover, now)` | Python function | Reads roots; writes the index | `WorkspaceConfig`, writable connection | tuple of `RootResult` (root, discovery run, stored run) | `OPERATION_IN_PROGRESS` propagates |

Exit codes: 0 every root `complete`; 1 any root `partial` or `failed`; 2 configuration absent or invalid, or an unknown command; 3 `OPERATION_IN_PROGRESS`; 4 `INDEX_UNAVAILABLE`, `INDEX_SCHEMA_TOO_NEW`, or `INDEX_MIGRATION_FAILED`.

Report (standard output, plain text): a header naming the configuration file and the root count; for each root a line `<root>: <status> - <n> repositories (<counts>)`, indented skip lines `skipped <reason> x<count>: <advice>`, and failure reasons; a final `Indexed <n> projects in <index path>.` line, preceded by `Created the index.` on first use. Diagnostics and errors go to standard error.

## 4. Error Model

| Condition | Error code | Response shape | Safe to show the user |
|---|---|---|---|
| No configuration file or no roots | none | message with the searched path and an example; exit 2 | Yes (the owner's own paths) |
| Invalid configuration | none | one line per problem; exit 2 | Yes |
| Another scan running | `OPERATION_IN_PROGRESS` | message; exit 3 | Yes |
| Index cannot be opened or migrated | `INDEX_*` | code and message; exit 4 | Yes |
| Root missing or unreadable | none | root reported `failed` with its reason; exit 1 | Yes |

## 5. Trust Boundary

The configuration is trusted local input; repository content is untrusted and only read through the existing bounded discovery. The command takes no root from the command line, so it cannot be pointed outside the configuration. Output includes the owner's local paths, which is acceptable on their own terminal; nothing is sent anywhere.

Machine-local data: the index and the report.

## 6. Data Model

No schema change. One `scan_runs` row per root per scan.

## 7. Migration and Compatibility

New surface. An older index is migrated by the existing runner (with a backup) when opened for writing.

## 8. Traceability

| Requirement | Operation |
|---|---|
| Only configured roots are scanned | `scan_workspace` over `config.roots` |
| The first run creates what it needs | `open_index`, report line |
| Each root is reported | report |
| The exit code tells the truth | exit codes |
| Scanning does not change repositories | read-only discovery |

## 9. Open Contract Questions

- [ ] A `--root` subset option.
