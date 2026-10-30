# API contract

`vyasa query workspaces` returns schema version 1 and `data.workspaces`, each with a local `root` and `status`; no index is required. `vyasa query search --workspace ROOT` returns the existing search envelope restricted to a configured root. `vyasa scan --workspace ROOT` scans only that configured root. A nonconfigured root fails before opening or creating the index. Existing CLI commands retain their behavior. Workspace paths are local-only and accepted only when they match loaded configuration. No MCP or database schema changes.
