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

Standalone build (Windows or Linux; builds for the OS it runs on):

```bash
cp .env.example .env           # set VYASA_MCP_OUT to the folder that keeps your MCP builds
venv/bin/python scripts/build_mcp.py     # result: <VYASA_MCP_OUT>/Vyasa MCP/vyasa-mcp[.exe]
```

### MCP client configuration

Point the client at the executable (or at `vyasa-mcp` inside the venv). Add `VYASA_HOME` only if
the data directory is not the default.

```json
{
  "mcpServers": {
    "vyasa": {
      "command": "E:\MCP\Vyasa MCP\vyasa-mcp.exe",
      "env": { "VYASA_HOME": "C:\Users\you\AppData\Local\Vyasa" }
    }
  }
}
```

Tools: `search_projects`, `get_project`, `get_profile_context`, `get_index_status`,
`get_profile_guide`. All are read-only; the server never scans, writes, or returns local paths.
Until `vyasa scan` has run, tools return the error code `INDEX_UNAVAILABLE`.

## 4. Limitations

- **Phase 1 only.** No Google Sheets sync, no GitHub/Bitbucket API discovery, no remote
  scanning without a local checkout.
- **Not provided yet:** `find_related_projects`, `get_project_dependencies`, and an MCP
  refresh tool. Dependencies appear inside `get_project` under frameworks; refresh is
  `vyasa scan` on the command line.
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
