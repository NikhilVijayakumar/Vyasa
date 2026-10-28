# Interface and Data Contract: be-standalone-build

- **OpenSpec Change ID:** `be-standalone-build`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the install layout, the data-directory rule for built executables, and the build command.

## 2. Scope

In: `data_directory()`, `scripts/build_mcp.py`, the install layout. Out: MCP tool contracts (unchanged), Sheets and provider calls (not affected).

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `data_directory(environ, home, platform, frozen_executable)` | Python function | none; pure | optional overrides | data directory path | none |
| `python scripts/build_mcp.py [--out DIR] [--name NAME]` | build command | writes `<out>/<name>/` | output root, install name | prints `Saved: <root>` and both executable paths | exit 2: no output root; exit 2: PyInstaller missing |
| `vyasa scan`, `vyasa-mcp` | existing | unchanged | unchanged | unchanged | unchanged |

Install layout:

```
<out>/<name>/
  vyasa/vyasa[.exe]            scan command (reads and writes the index)
  vyasa-mcp/vyasa-mcp[.exe]    MCP server (read-only)
  data/config.toml             workspace roots
  data/<index file>            SQLite index
```

Data directory order: `VYASA_HOME`; a frozen executable's `<its folder>/../data`; the platform folder.

## 4. Error Model

The build reports a missing output root or missing PyInstaller on standard error and exits 2. A PyInstaller failure propagates as a non-zero exit. No MCP error changes.

## 5. Trust Boundary

`data/` is trusted local configuration and machine-local index state. It is never returned by an MCP tool beyond what tools already return (no local paths). The build copies only `examples/config.toml`; it reads no workspace content.

## 6. Data Model

None. The index schema and config format are unchanged.

## 7. Migration and Compatibility

- An existing per-user data directory is untouched and still used by non-frozen runs.
- To reuse existing data in an install, copy it into `<root>/data/` or set `VYASA_HOME`.
- The MCP executable path changes from `<root>/vyasa-mcp.exe` to `<root>/vyasa-mcp/vyasa-mcp.exe`; clients update their command once.

## 8. Traceability

| Item | Requirement |
|---|---|
| layout | Both executables are built into one root |
| `data_directory` | Locate the configuration file |
| rebuild rules | A rebuild preserves the data |
| output root | The output root comes from the environment |

## 9. Open Questions

- [ ] An MCP refresh tool.
