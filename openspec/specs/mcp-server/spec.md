# mcp-server Specification

## Purpose
TBD - created by archiving change be-mcp-server. Update Purpose after archive.

## Requirements

### Requirement: The server speaks stdio and lists its tools

The system SHALL provide a server started with `python -m vyasa.adapters.mcp` (and `vyasa-mcp`) that speaks MCP over standard input and output only, opens no network listener, and lists exactly `search_projects`, `get_project`, and `get_index_status`, each with a description and an input schema.

#### Scenario: Discover tools

- **GIVEN** the server is started as a subprocess
- **WHEN** a client lists tools over stdio
- **THEN** it receives exactly those three tools with schemas

#### Scenario: Standard output is protocol only

- **GIVEN** the running server answering requests
- **WHEN** a client reads its output
- **THEN** every line it receives is a protocol message and diagnostics go to standard error

#### Scenario: Unregistered tools

- **GIVEN** the server
- **WHEN** a client calls `get_project_context`
- **THEN** the call fails as an unknown tool and no data is returned

### Requirement: Tools return structured, read-only results

The system SHALL return each successful result as structured content in the shared envelope (with a JSON text copy), open the index read-only for every call, and never write to the index or scan.

#### Scenario: Search

- **GIVEN** an index with projects
- **WHEN** `search_projects` is called with a query
- **THEN** the structured content holds `schema_version`, `data` with `projects` and `page`, and `meta`

#### Scenario: Project and status

- **GIVEN** an index with a project
- **WHEN** `get_project` and `get_index_status` are called
- **THEN** each returns its envelope

#### Scenario: Index unchanged

- **GIVEN** an index file
- **WHEN** all three tools are called
- **THEN** the file's bytes are unchanged

### Requirement: Failures are structured results

The system SHALL return domain failures as results flagged as errors whose structured content is `{"error": {"code", "message"}}` with the documented code, and SHALL NOT raise protocol errors for them.

#### Scenario: Invalid input

- **GIVEN** a search with state `retired`
- **WHEN** it is called
- **THEN** the result is an error with code `INVALID_INPUT`

#### Scenario: Unknown project

- **GIVEN** an unknown identifier
- **WHEN** `get_project` is called
- **THEN** the result is an error with code `PROJECT_NOT_FOUND`

#### Scenario: No index

- **GIVEN** no index file
- **WHEN** any tool is called
- **THEN** the result is an error with code `INDEX_UNAVAILABLE` and no file is created

### Requirement: No paths cross the boundary

The system SHALL accept no filesystem path or path-like option in any tool input and SHALL include no absolute path or scanned root in any result.

#### Scenario: Schemas

- **GIVEN** the tool list
- **WHEN** input schemas are inspected
- **THEN** no property is named or described as a path, and none is named `include_paths`

#### Scenario: Results

- **GIVEN** projects indexed from a local root
- **WHEN** every tool is called
- **THEN** no result string contains the root

### Requirement: The tool contract is pinned

The system SHALL keep a committed snapshot of the tool list (names, descriptions, input schemas, annotations), and a test SHALL fail when the live list differs from it.

#### Scenario: Matches

- **GIVEN** the committed snapshot
- **WHEN** the live tool list is compared
- **THEN** they are equal

#### Scenario: Read-only hints

- **GIVEN** the tool list
- **WHEN** annotations are inspected
- **THEN** every tool is marked read-only

### Requirement: The SDK is an optional extra

The system SHALL declare the MCP SDK only as the optional extra `mcp`, import it only inside `vyasa.adapters.mcp`, and, when it is missing, make the entry point print an installation hint to standard error and exit with a non-zero status.

#### Scenario: Core without the SDK

- **GIVEN** the `mcp` package cannot be imported
- **WHEN** the query layer and the index are imported and used
- **THEN** they work

#### Scenario: Entry point without the SDK

- **GIVEN** the `mcp` package cannot be imported
- **WHEN** the entry point runs
- **THEN** it exits non-zero with a message naming the `mcp` extra
