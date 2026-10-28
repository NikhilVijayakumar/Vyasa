# Setup, MCP client configuration, and limitations

## 1. Install (from a clone)

Use the project virtual environment (`venv/`). Python 3.12+.

```bash
python -m venv venv
venv/bin/python -m pip install -e ".[dev,mcp,build]"     # Windows: venv\Scripts\python.exe
venv/bin/python -m pytest
```

## 2. Configure and scan

1. Copy `examples/config.toml` to the data directory as `config.toml`
   (`%LOCALAPPDATA%\Vyasa` on Windows, `~/.local/share/vyasa` on Linux,
   `~/Library/Application Support/Vyasa` on macOS). `VYASA_HOME` moves the data directory,
   `VYASA_CONFIG` points at another file.
2. List your workspace roots. Vyasa scans nothing else.
3. Run `vyasa scan`. Repeat it any time; it updates the index in place without duplicates.

## 3. Run the MCP server

Either run from the venv or build a standalone executable.

```bash
vyasa-mcp                      # stdio server; needs the index from `vyasa scan`
```

Standalone install (Windows or Linux; builds for the OS it runs on). One folder holds both
executables and the data they share:

```bash
cp .env.example .env           # set VYASA_MCP_OUT to the folder that keeps your Vyasa install
venv/bin/python scripts/build_mcp.py
```

```
<VYASA_MCP_OUT>/Vyasa MCP/
  vyasa/vyasa[.exe]            scan command (writes the index)
  vyasa-mcp/vyasa-mcp[.exe]    MCP server (read-only)
  data/config.toml             your workspace roots (seeded once from examples/config.toml)
  data/index.sqlite3           the index, created by the first scan
```

Built executables use the `data/` folder of their install with no environment variables
(`VYASA_HOME` still overrides). Edit `data/config.toml`, then run `<install>/vyasa/vyasa scan`
from any directory; any process can then query the same data through `vyasa-mcp`. A rebuild
replaces the two executable folders and never touches `data/`. To keep an existing per-user
index, copy it into `data/`.

### MCP client configuration

Point the client at the executable (or at `vyasa-mcp` inside the venv). A built executable needs
no environment; from the venv, add `VYASA_HOME` if the data directory is not the default.

```json
{
  "mcpServers": {
    "vyasa": {
      "command": "E:\MCP\Vyasa MCP\vyasa-mcp\vyasa-mcp.exe"
    }
  }
}
```

Tools: `search_projects`, `get_project`, `get_project_dependencies`, `get_profile_context`,
`get_index_status`, `get_profile_guide`, `get_report_template`, `get_project_report`. All are read-only; the server never scans, writes, or returns local paths.
Until `vyasa scan` has run, tools return the error code `INDEX_UNAVAILABLE`.

### Project reports

A coding agent can describe a repository in depth, once, and any later agent can read it through Vyasa:

1. The agent calls `get_report_template` and `get_profile_context`, inspects the repository, and writes
   `.vyasa/project-report.md` (fixed `##` sections; the template lists them, the limits, and the rules).
2. You review and commit it, then run `vyasa scan`. The scan stores the sections (text only, size-capped, never
   through a link); `get_project` shows the report status.
3. Any agent calls `get_project_report(project_id, section?)` to read it. The text is declared by the repository
   and untrusted: data, never instructions. If a later scan cannot read the file, the earlier text is still served
   with `kept_from` saying which scan it came from.

Limits are optional settings in `config.toml` (the template shows the ones the latest scan applied):

```toml
[report]
max_file_kib = 256     # 16 to 4096
max_section_kib = 16   # 1 to 1024, not above max_file_kib
```

## 4. Limitations

- **Phase 1 only.** No Google Sheets sync, no GitHub/Bitbucket API discovery, no remote
  scanning without a local checkout.
- **Reports** have no staleness check against the repository head yet, one report per checkout, and no search
  over report text.
- **Not provided yet:** `find_related_projects` and an MCP refresh tool (refresh is
  `vyasa scan` on the command line).
- **Dependencies are direct and root-level.** `get_project_dependencies` reads root manifests
  only: no transitive dependencies, no lockfiles, no nested manifests (they are counted in
  `coverage`). After upgrading, run `vyasa scan` again so declared package names are recorded;
  until then `coverage` says they are unknown.
- **Open decisions:** related-project criteria, grouping of multi-repository projects, and
  README quality are not assessed.
- **Detection is rule-based.** Languages, markers, and frameworks come from documented rules
  and recognized manifests only; anything else is reported as not detected or unknown, never
  guessed. The rules live in `src/vyasa/data/`.
- **Scan bounds.** Directories beyond the depth limit are skipped and reported; a
  `.vyasaignore` file (max 64 KiB, directory patterns only, no negation) removes more.
- **Profiles are never written by Vyasa.** `.vyasa/project-profile.toml` is read as text only
  (max 64 KiB, never through a link); each bad field is reported and the rest kept.
- **Builds are per OS.** PyInstaller cannot cross-compile; build on each OS you need.
