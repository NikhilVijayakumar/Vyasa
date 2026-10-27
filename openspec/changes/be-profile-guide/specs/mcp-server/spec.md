# Specifications: be-profile-guide (mcp-server)

## 1. Specification Overview

- **OpenSpec Change ID:** `be-profile-guide`
- **Purpose:** Add the profile guide tool to the server.
- **Related proposal:** `proposal.md`

## 2. Capability: mcp-server

### Purpose

Serve the guide through MCP without needing an index.

## MODIFIED Requirements

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

## ADDED Requirements

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
