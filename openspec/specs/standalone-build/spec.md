# standalone-build Specification

## Purpose
TBD - created by archiving change be-standalone-build. Update Purpose after archive.

## Requirements

### Requirement: Both executables are built into one root

The system SHALL build `vyasa` and `vyasa-mcp` as separate one-folder bundles at `<root>/vyasa/` and `<root>/vyasa-mcp/`, where `<root>` is the output root joined with the install name, and SHALL create `<root>/data/` when absent.

#### Scenario: Layout

- **GIVEN** an output root and an install name
- **WHEN** the build finishes
- **THEN** `<root>/vyasa/vyasa[.exe]`, `<root>/vyasa-mcp/vyasa-mcp[.exe]`, and `<root>/data/` exist

### Requirement: A rebuild preserves the data

The system SHALL replace only `<root>/vyasa/` and `<root>/vyasa-mcp/` on a rebuild, SHALL NOT modify or delete anything under `<root>/data/`, and SHALL copy `examples/config.toml` to `<root>/data/config.toml` only when that file is absent.

#### Scenario: Existing data survives

- **GIVEN** `<root>/data/` holds a `config.toml` and an index
- **WHEN** the build runs again
- **THEN** both files are byte-for-byte unchanged

#### Scenario: Config seeded once

- **GIVEN** `<root>/data/config.toml` is absent
- **WHEN** the build runs
- **THEN** it holds a copy of the example configuration

### Requirement: The output root comes from the environment

The system SHALL take the output root from `--out`, then `VYASA_MCP_OUT`, then `VYASA_MCP_OUT` in the repository `.env`, and SHALL refuse to build with no default when none is set.

#### Scenario: No output root

- **GIVEN** none of the three sources is set
- **WHEN** the build starts
- **THEN** it exits non-zero with a message naming `VYASA_MCP_OUT` and builds nothing
