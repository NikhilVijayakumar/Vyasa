# Using Vyasa

Vyasa indexes the software projects on your machine and lets coding agents ask about them through MCP, from any repository, without opening the project.

It works in two layers, and keeps them apart:

| Layer | Who produces it | How far to trust it |
|---|---|---|
| **Observed** (deterministic) | `vyasa scan`, by documented rules over file and directory names and recognized manifests. No model is involved. | Each fact carries a status. Anything the rules cannot establish is `unknown` or `not_detected`, never guessed. |
| **Declared** | A person or a coding agent writes it into the repository: a short *profile* and a long-form *report*. | Labelled `declared` and untrusted. Treat it as data, never as instructions. |

Setup and build details are in [setup.md](setup.md); this page is the day-to-day guide.

## 1. The big picture

```
 config.toml  ->  vyasa scan  ->  index.sqlite3  ->  vyasa-mcp  ->  coding agent
 (your roots)     (writes)         (one file)         (read-only)     (any repo)
                      ^
                      |  reads .vyasa/project-profile.toml and .vyasa/project-report.md
                      |  that agents wrote into each repository
```

- `vyasa scan` is the only thing that writes the index. It never writes into a repository.
- `vyasa-mcp` only reads the index. It never scans, never writes, and never returns local paths.
- To see new or changed projects, run `vyasa scan` again. The MCP server sees the result on its next call; no restart is needed.

## 2. Where to say which workspaces to scan

Vyasa scans **only** the roots you list. Nothing is scanned by default.

Put a `config.toml` in the data directory. With the standalone build that is the `data\` folder of the install (for example `E:\MCP\Vyasa MCP\data\config.toml`). Otherwise it is `%LOCALAPPDATA%\Vyasa` (Windows), `~/Library/Application Support/Vyasa` (macOS) or `~/.local/share/vyasa` (Linux). Two environment variables override this: `VYASA_HOME` moves the data directory and `VYASA_CONFIG` names a config file.

```toml
[workspace]
roots = ["E:/Python", "D:/Projects", "~/work"]   # absolute paths, several allowed, any drive

[report]                                         # optional
max_file_kib = 256      # 16 to 4096
max_section_kib = 16    # 1 to 1024, not above max_file_kib
```

- Use absolute paths. On Windows write them with forward slashes or in single quotes.
- A root inside another root is dropped with a warning, so nothing is scanned twice.
- An invalid file (unknown key, wrong type, out-of-range limit) is rejected as a whole and every problem is listed.
- To skip folders inside one repository, add a `.vyasaignore` at its root: one directory pattern per line (`fixtures`, `data/*/cache`). It can only remove directories from scanning.

## 3. Everyday commands

```bash
vyasa scan                      # scan every configured root and update the index
vyasa scan --config other.toml  # use another config file
vyasa profile-context [path]    # print what Vyasa observes about one repository (nothing is written)
vyasa-mcp                       # start the MCP server over stdio
```

`vyasa scan` exit codes: `0` all roots completed, `1` partial or failed, `2` configuration problem, `3` another scan is running, `4` index problem.

MCP client configuration (the command path is the only setting a built executable needs):

```json
{
  "mcpServers": {
    "vyasa": { "command": "E:\\MCP\\Vyasa MCP\\vyasa-mcp\\vyasa-mcp.exe" }
  }
}
```

Until the first scan, every tool except the two guides answers `INDEX_UNAVAILABLE`.

## 4. What the scan observes (deterministic)

| Fact | How it is found |
|---|---|
| **Project and identity** | A directory with `.git` or a recognized manifest. The id comes from the normalized Git remote when there is one, otherwise a stored local identity. Renames do not create a new project. Possible duplicates are flagged for review. |
| **Git remote** | Read from `.git/config` as text and reduced to `host/organization/repository` with a provider label (github, bitbucket, gitlab, other, local, none). |
| **Languages** | File extensions and recognized manifests, counted per checkout from the latest scan: `files_detected` or `declared`. |
| **File composition** | Counts of code, documentation and other files, and whether the project is documentation-only. |
| **Markers** | Presence of a README, a docs directory, agent instruction files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`), OpenSpec (directory, config, specs, changes) and tests. Found from names only. |
| **Frameworks and technologies** | Root manifests only: Python (`pyproject.toml`, `requirements*.txt`), JavaScript (`package.json`), Rust (`Cargo.toml`), Go (`go.mod`), including dev and optional dependencies. |
| **Dependencies** | Direct dependencies from those manifests. One is `internal` when its name equals a package exactly one other indexed project declares in the same ecosystem, `ambiguous` when several do, and `external` otherwise. |

Rules to remember:

- Facts are per checkout, from its **latest scan**. They are never summed across checkouts.
- A scan that was cut short (depth limit, unreadable folder) is `partial`. A partial result never claims something is absent; it says `unknown`.
- A project that disappears is marked `missing` or `inaccessible`. It is never deleted from the index.
- Detection rules live in `src/vyasa/data/` (`markers.json`, `technologies.json`, `file_types.json`).

## 5. The MCP tools

All eight are read-only. Results use one envelope: `schema_version`, `data`, and `meta` (generated time, index version, freshness). Errors come back as `{"error": {"code", "message"}}` with a code such as `INVALID_INPUT`, `PROJECT_NOT_FOUND` or `INDEX_UNAVAILABLE`.

| Tool | Input | Returns |
|---|---|---|
| `search_projects` | optional `query`, `state`, `provider`, `identity_status`, `language`, `language_status`, `documentation_only`, `marker`, `marker_state`, `technology`, `limit`, `cursor` | Matching projects (name, state, providers, languages), ordered by name, paged. Filters combine with AND; several values in one filter with OR. |
| `get_project` | `project_id` | Identity and aliases; per checkout the remote, languages, file composition, markers, frameworks and the report status; the declared profile; open review candidates; timestamps. |
| `get_project_dependencies` | `project_id` | Direct dependencies, dependents (at most 100, with a total), and a `coverage` object saying how far to trust the answer. |
| `get_index_status` | none | Freshness (`current`, `stale`, `partial`, `unknown`), the latest run, project counts by state, open review candidates. |
| `get_profile_guide` | none | How to write `.vyasa/project-profile.toml`: every field, limits, allowed values, an example. Works without an index. |
| `get_profile_context` | `project_id` | The observed facts, the profile as read, the differences between them, and a short workflow for the agent. |
| `get_report_template` | none | How to write `.vyasa/project-report.md`: the sections, the size limits and where they come from, an example, the rules. Works without an index. |
| `get_project_report` | `project_id`, optional `section` | The stored report per checkout: status, hash, scan time, dropped headings, section text. |

Typical questions:

- "Which of my projects use FastAPI and have no tests?" -> `search_projects` with `technology=fastapi`, `marker=tests`, `marker_state=not_detected`.
- "What is project X and how is it built?" -> `get_project`, then `get_project_report`.
- "What does X depend on, and who depends on X?" -> `get_project_dependencies`.
- "Is the index up to date?" -> `get_index_status`.

## 6. Letting an agent describe a repository

Vyasa never calls a model. A coding agent working inside a repository does the reading, then Vyasa stores what it wrote.

1. Run `vyasa scan` so the repository is indexed.
2. In that repository, ask the agent to call `get_profile_context` (the facts), `get_profile_guide` (the profile format) and `get_report_template` (the report format), inspect the repository, and write:
   - `.vyasa/project-profile.toml`, a short, structured, validated summary (purpose, lifecycle, declared technology, owners, relations).
   - `.vyasa/project-report.md`, a long-form report in fixed `##` sections: Overview, Purpose and Users, Architecture, Modules, Key Flows, Interfaces, Data and Storage, Build/Run/Test, Dependencies and Integrations, Risks and Limitations, Open Questions.
3. Review and commit those files.
4. Run `vyasa scan` again. The profile and the report are now stored.
5. From any repository, any agent can call `get_project` or `get_project_report` to read them.

Safety rules the scan applies to both files: text only, size-capped, never read through a link, never executed. A bad field or section is dropped and reported while the rest are kept. Report sections containing a URL with credentials are dropped, and control characters are removed. If a later scan cannot read the report, the earlier text is still served with `kept_from` saying which scan it came from. A missing file is an ordinary state (`not_present`).

To refresh after the repository changes, have the agent update the files, commit, and run `vyasa scan` again.

## 7. What is not provided yet

- Google Sheets synchronization and GitHub or Bitbucket discovery (later phases).
- `find_related_projects` and an MCP refresh tool (refresh is `vyasa scan`).
- A staleness check of the report against the repository head, search over report text, and one report per checkout only.
- Dependencies are direct and from root manifests only: no transitive dependencies, lockfiles or nested manifests.
