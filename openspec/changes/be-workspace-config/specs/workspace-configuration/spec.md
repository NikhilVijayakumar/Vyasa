# Specifications: be-workspace-config

## 1. Specification Overview

- **OpenSpec Change ID:** `be-workspace-config`
- **Purpose:** Load the configured workspace roots safely and report each root's state.
- **Related proposal:** `proposal.md`
- **Related design:** `design.md`
- **Api and data contract:** `api-contract.md`
- **Knowledge references:** `knowledge/decisions/configuration-file-format-and-location.md`, `knowledge/practices/configuration.md`
- **Team focus:** Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

## 2. Capability: workspace-configuration

### Purpose

Return the workspace roots a user configured, or say why there are none.

### Scope

One TOML file, the `workspace.roots` setting, and per-root accessibility. No scanning.

## ADDED Requirements

### Requirement: Locate the configuration file

The system SHALL use, in order, the explicit path given by the caller, the path in the `VYASA_CONFIG` environment variable, and `config.toml` in the data directory, where the data directory is `VYASA_HOME` when set and otherwise the platform data directory.

#### Scenario: Explicit path wins

- **GIVEN** an explicit path and `VYASA_CONFIG` both name files
- **WHEN** the configuration is loaded
- **THEN** the explicit file is used

#### Scenario: Environment variable next

- **GIVEN** no explicit path and `VYASA_CONFIG` names a file
- **WHEN** the configuration is loaded
- **THEN** that file is used

#### Scenario: Default location

- **GIVEN** no explicit path and no `VYASA_CONFIG`
- **WHEN** the configuration is loaded
- **THEN** `config.toml` in the data directory is used

#### Scenario: Platform data directories

- **GIVEN** `VYASA_HOME` is unset
- **WHEN** the data directory is computed for Windows, macOS, and Linux
- **THEN** it is `%LOCALAPPDATA%\Vyasa` (or `AppData\Local\Vyasa` under the home directory when unset), `Library/Application Support/Vyasa` under the home directory, and `$XDG_DATA_HOME/vyasa` (or `.local/share/vyasa` under the home directory when unset)

#### Scenario: Home override

- **GIVEN** `VYASA_HOME` is set
- **WHEN** the data directory is computed on any platform
- **THEN** it is `VYASA_HOME`

#### Scenario: Explicit file missing

- **GIVEN** an explicit path or `VYASA_CONFIG` names a file that does not exist
- **WHEN** the configuration is loaded
- **THEN** loading fails with an error naming the file

### Requirement: Load several workspace roots

The system SHALL load every path in `workspace.roots`, expanding a leading `~`, requiring each to be absolute, normalizing it, removing duplicates, and keeping the order of first appearance.

#### Scenario: Multiple roots

- **GIVEN** a file listing two absolute roots on different drives or directories
- **WHEN** the configuration is loaded
- **THEN** both roots are returned in the listed order

#### Scenario: Duplicates merged

- **GIVEN** a file listing the same root twice, once with a trailing separator or redundant segments
- **WHEN** the configuration is loaded
- **THEN** the root is returned once

#### Scenario: Home expansion

- **GIVEN** a root written as `~/work`
- **WHEN** the configuration is loaded with a known home directory
- **THEN** the root is that home directory joined with `work`

#### Scenario: Nested roots kept and reported

- **GIVEN** one listed root lies inside another
- **WHEN** the configuration is loaded
- **THEN** both are returned
- **AND** a warning names the nesting

### Requirement: Not configured

The system SHALL return a not-configured result with a reason, and SHALL NOT supply a default root, when no file exists at the default location or the file lists no roots.

#### Scenario: No file at the default location

- **GIVEN** no explicit path, no `VYASA_CONFIG`, and no file in the data directory
- **WHEN** the configuration is loaded
- **THEN** the result is not configured with a reason naming the expected file

#### Scenario: Empty roots

- **GIVEN** a valid file whose `workspace.roots` is empty or absent
- **WHEN** the configuration is loaded
- **THEN** the result is not configured with a reason naming the setting

### Requirement: Invalid configuration is rejected as a whole

The system SHALL report every problem found and apply nothing when the file cannot be read, is not valid TOML, has an unknown key, has a value of the wrong type, or lists a relative path.

#### Scenario: Syntax error

- **GIVEN** a file that is not valid TOML
- **WHEN** the configuration is loaded
- **THEN** loading fails with an error naming the file

#### Scenario: Unknown key

- **GIVEN** a file with an unrecognized key under `workspace` or at the top level
- **WHEN** the configuration is loaded
- **THEN** loading fails with an error naming the key

#### Scenario: Wrong type

- **GIVEN** `workspace.roots` is a string, or a list containing a non-string
- **WHEN** the configuration is loaded
- **THEN** loading fails with an error naming the setting

#### Scenario: Relative root

- **GIVEN** a root that is not absolute
- **WHEN** the configuration is loaded
- **THEN** loading fails with an error naming the value

#### Scenario: All problems together

- **GIVEN** a file with an unknown key and a relative root
- **WHEN** the configuration is loaded
- **THEN** the error lists both problems

### Requirement: Each root is checked on its own

The system SHALL report each configured root as accessible, missing, not a directory, or unreadable, and a problem with one root SHALL NOT change the report of another.

#### Scenario: One missing root

- **GIVEN** two roots, one of which does not exist
- **WHEN** the roots are checked
- **THEN** the first is accessible and the second is missing

#### Scenario: File instead of directory

- **GIVEN** a root that is a file
- **WHEN** the roots are checked
- **THEN** it is reported as not a directory

#### Scenario: Unreadable root

- **GIVEN** a root that exists but cannot be listed
- **WHEN** the roots are checked
- **THEN** it is reported as unreadable

---

## 5. Specification Review

- [x] Every in-scope behavior is described by a requirement.
- [x] Every requirement sits inside a delta section heading.
- [x] Scenarios cover normal, boundary, and failure behavior.
- [x] Assumptions and unresolved questions are identified in the proposal.

**Status:** Draft
