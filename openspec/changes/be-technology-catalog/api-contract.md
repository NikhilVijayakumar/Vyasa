# API contract

`vyasa query technologies` returns JSON `{schema_version: "1", data: {registry_version: integer, technologies: [{key, name, category, ecosystem}]}}`. Entries are deterministically ordered by name and key. Errors use the existing structured CLI error envelope. This catalog is the set supported by detection, not a list of observed project technologies. It neither opens the index nor initiates a scan. Existing search and MCP contracts are unchanged.
