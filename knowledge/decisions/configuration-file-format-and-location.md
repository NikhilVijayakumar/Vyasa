---
type: Decision
title: "Configuration File Format and Location"
description: One TOML file found by explicit path, then environment variable, then the data directory; no root is ever implied, and an invalid file is rejected as a whole.
tags: [adr, configuration, workspace]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-27T15:00:00Z }
sources:
  - id: cfg
    resource: /practices/configuration.md
    title: Configuration
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

Workspace roots are the one setting without which nothing may be scanned, and a user may have several, on different drives. The configuration practice already requires explicit, validated, fail-closed settings. The file needs a format, a place to live on Windows, macOS, and Linux, and a defined result for each way it can be absent or wrong.

# Decision

The configuration is one TOML file, read with the standard library. It is found in this order: an explicit path given by the caller, the `VYASA_CONFIG` environment variable, then `config.toml` in the data directory. The data directory is `VYASA_HOME` when set; otherwise `%LOCALAPPDATA%\Vyasa` on Windows, `~/Library/Application Support/Vyasa` on macOS, and `$XDG_DATA_HOME/vyasa` or `~/.local/share/vyasa` elsewhere.

Workspace roots are a list of absolute paths under a `workspace` table. A leading `~` is expanded; a relative path is invalid. Duplicate roots are merged, and a root inside another is kept and reported. Unknown keys are invalid.

Four outcomes are distinct:

- **Loaded:** valid, with at least one root.
- **Not configured:** no file at the default location, or no roots listed. Nothing is scanned and no default location is used.
- **Invalid:** an unreadable file, a syntax error, an unknown key, a wrong type, or a relative path. Every problem is reported together and nothing is applied.
- **Explicit path missing:** a path given by the caller or `VYASA_CONFIG` that does not exist is invalid, not "not configured", because the user asked for that file.

Each root is then checked on its own as accessible, missing, not a directory, or unreadable, so one bad root never hides the others.

# Alternatives considered

- **YAML or JSON.** YAML needs a dependency; JSON has no comments. TOML is in the standard library and suits hand-edited settings.
- **A single `~/.vyasa` directory on every platform.** Simpler, but it ignores each platform's convention for application data and differs from the index location.
- **Fall back to the current directory or the home directory when no root is configured.** Convenient, but it scans a location the user never chose.
- **Fail on the first problem.** Simpler code, but the user fixes one error per run.

# Consequences

- A missing default file is a normal first-run state, not an error.
- Adding a setting means adding a known key; older versions reject files that use it.
- Roots are machine-local paths and are never synchronized or returned to agents by default.
- Platform differences are confined to one function of the home directory, the platform name, and the environment, so every layout can be tested on any system.

# Related

- [Configuration](/practices/configuration.md)
- [Local-First Operation](/concepts/local-first.md)
- [Untrusted Content](/concepts/untrusted-content.md)
- [Scanning and Evidence: Workspace Discovery and Repository Inspection](/architecture/scanning-and-evidence/discovery-and-inspection.md)
