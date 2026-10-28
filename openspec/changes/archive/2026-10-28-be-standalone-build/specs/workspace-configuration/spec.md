# Specifications: be-standalone-build (workspace-configuration)

## 1. Specification Overview

- **OpenSpec Change ID:** `be-standalone-build`
- **Purpose:** Let a built Vyasa executable find its data beside itself.
- **Related proposal:** `proposal.md`

## 2. Capability: workspace-configuration

### Purpose

One data directory shared by every Vyasa executable in an install.

## MODIFIED Requirements

### Requirement: Locate the configuration file

The system SHALL use, in order, the explicit path given by the caller, the path in the `VYASA_CONFIG` environment variable, and `config.toml` in the data directory, where the data directory is `VYASA_HOME` when set, otherwise the `data` folder next to the folder containing a built (frozen) executable, and otherwise the platform data directory.

#### Scenario: Explicit path wins

- **GIVEN** an explicit path and `VYASA_CONFIG` both name files
- **WHEN** the configuration is loaded
- **THEN** the explicit file is used

#### Scenario: Environment variable next

- **GIVEN** no explicit path and `VYASA_CONFIG` names a file
- **WHEN** the configuration is loaded
- **THEN** that file is used

#### Scenario: Default location

- **GIVEN** no explicit path, no `VYASA_CONFIG`, and a run that is not a built executable
- **WHEN** the configuration is loaded
- **THEN** `config.toml` in the platform data directory is used

#### Scenario: Platform data directories

- **GIVEN** `VYASA_HOME` is unset and the run is not a built executable
- **WHEN** the data directory is computed for Windows, macOS, and Linux
- **THEN** it is `%LOCALAPPDATA%\Vyasa` (or `AppData\Local\Vyasa` under the home directory when unset), `Library/Application Support/Vyasa` under the home directory, and `$XDG_DATA_HOME/vyasa` (or `.local/share/vyasa` under the home directory when unset)

#### Scenario: Home override

- **GIVEN** `VYASA_HOME` is set
- **WHEN** the data directory is computed on any platform
- **THEN** it is `VYASA_HOME`, even for a built executable

#### Scenario: Explicit file missing

- **GIVEN** an explicit path or `VYASA_CONFIG` names a file that does not exist
- **WHEN** the configuration is loaded
- **THEN** loading fails with an error naming the file

#### Scenario: Built executable uses the sibling data folder

- **GIVEN** a built executable at `<root>/vyasa-mcp/vyasa-mcp.exe` and no `VYASA_HOME`
- **WHEN** the data directory is resolved
- **THEN** it is `<root>/data`

#### Scenario: Source run is unchanged

- **GIVEN** a run from source or a virtual environment and no `VYASA_HOME`
- **WHEN** the data directory is resolved
- **THEN** it is the platform data directory as before
