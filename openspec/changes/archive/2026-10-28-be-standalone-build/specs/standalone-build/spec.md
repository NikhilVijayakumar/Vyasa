# Specifications: be-standalone-build

## 1. Specification Overview

- **OpenSpec Change ID:** `be-standalone-build`
- **Purpose:** Build both executables and their data folder into one install root.
- **Related proposal:** `proposal.md`
- **Related design:** `design.md`
- **Api and data contract:** `api-contract.md`
- **Knowledge references:** `knowledge/decisions/configuration-file-format-and-location.md`
- **Team focus:** Changes are judged on interface contracts and trust boundaries; failure modes, data integrity, and migration impact; and the verification layer that owns each behavior.

## 2. Capability: standalone-build

### Purpose

One folder, chosen by the user, holds the scan command, the MCP server, and the data they share.

### Scope

`scripts/build_mcp.py` and its output layout.

## ADDED Requirements

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
