# API contract

## CLI

`vyasa query status`, `vyasa query search [--query TEXT] [--technology KEY] [--limit N] [--cursor CURSOR]`, `vyasa query project PROJECT_ID`, `vyasa query dependencies PROJECT_ID`, `vyasa query context PROJECT_ID`, and `vyasa query report PROJECT_ID` print one JSON object to stdout. Success uses the existing query envelope, including schema_version, data and meta. Errors use `{"error":{"code":"...","message":"..."}}` and exit nonzero. Query validation and path redaction follow the existing application services. Unknown exceptions emit a generic internal error without repository content.

`vyasa query version` returns `{"schema_version":"1","data":{"version":"..."} }` without opening the index. The distribution packages the backend's own version metadata.

## Data and trust

The index location follows existing VYASA_HOME/install discovery. Open read-only for each query and close after use. No SQLite schema, migration, MCP tool or stored data changes. Repository-origin text is untrusted data.

## Compatibility and traceability

Existing scan and profile-context commands and MCP results remain unchanged. The change adds a CLI entry point to the existing FR-009–012 and FR-027–028 query behavior.
