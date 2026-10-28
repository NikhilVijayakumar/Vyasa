# mcp-server Specification

## Purpose
TBD - created by archiving change be-mcp-server. Update Purpose after archive.

## Requirements

### Requirement: The server speaks stdio and lists its tools

The system SHALL provide a server started with `python -m vyasa.adapters.mcp` (and `vyasa-mcp`) that speaks MCP over standard input and output only, opens no network listener, and lists exactly `search_projects`, `get_project`, `get_index_status`, and `get_profile_guide`, each with a description and an input schema.

#### Scenario: Discover tools

- **GIVEN** the server is started as a subprocess
- **WHEN** a client lists tools over stdio
- **THEN** it receives exactly those four tools with schemas

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

### Requirement: The profile guide needs no index

The system SHALL serve `get_profile_guide` with no input, with no index present, without opening any file, and in the shared envelope with `meta.generated_at`.

#### Scenario: No index

- **GIVEN** no index file
- **WHEN** `get_profile_guide` is called
- **THEN** it returns the guide and creates no file

#### Scenario: Same guide as the domain

- **GIVEN** the tool result
- **WHEN** it is compared with `profile_guide()`
- **THEN** `data` is equal

#### Scenario: Read-only and path-free

- **GIVEN** the tool list
- **WHEN** the tool's annotations and schema are read
- **THEN** it is marked read-only and takes no properties

### Requirement: The report template needs no index

The system SHALL provide a `get_report_template` tool that takes no input, reads no repository file, reads the index only to learn the applied limits when one exists, and returns the template in the shared envelope.

#### Scenario: No index

- **GIVEN** no index exists
- **WHEN** `get_report_template` is called
- **THEN** it returns the template with the default limits, source `default`, and not `INDEX_UNAVAILABLE`

#### Scenario: Limits from the latest scan

- **GIVEN** an index whose latest report observation applied a 512 KiB file limit
- **WHEN** `get_report_template` is called
- **THEN** the template shows 512 KiB with source `index`

### Requirement: The stored report is served as declared data

The system SHALL provide a `get_project_report` tool taking a `project_id` and an optional `section`, reading the index only, and returning for each checkout the status, the content hash, the scan time, and the requested sections as text marked `declared` with a warning that the text is untrusted, and no local path.

#### Scenario: Whole report

- **GIVEN** a stored report
- **WHEN** `get_project_report` is called with a project id
- **THEN** it returns every stored section with status, hash, scan time, and `declared`

#### Scenario: One section

- **GIVEN** a stored report
- **WHEN** it is called with a known section
- **THEN** only that section's text is returned

#### Scenario: Unknown section

- **GIVEN** a stored report
- **WHEN** it is called with a name that is not a template section
- **THEN** it fails with `INVALID_INPUT` and returns no text

#### Scenario: No report

- **GIVEN** a project whose checkouts have no report
- **WHEN** it is called
- **THEN** it returns status `not_present` for each checkout and no text

#### Scenario: Unknown project

- **GIVEN** an unknown project id
- **WHEN** it is called
- **THEN** it fails with `PROJECT_NOT_FOUND`

### Requirement: Project details show the report status only

The system SHALL include in `get_project` a `report` object per checkout with its status, section names and sizes, and dropped headings, and SHALL NOT include any section text.

#### Scenario: Status without text

- **GIVEN** a stored report
- **WHEN** `get_project` is called
- **THEN** `report` lists section names and sizes and contains no section text
