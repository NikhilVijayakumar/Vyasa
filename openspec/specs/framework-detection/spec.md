# framework-detection Specification

## Purpose
TBD - created by archiving change be-framework-detector. Update Purpose after archive.

## Requirements

### Requirement: Manifests are read under strict rules

The system SHALL read a supported manifest only if it is a regular file at the checkout root and not a link, SHALL read at most 1 MiB of it, SHALL decode it as strict UTF-8, and SHALL NOT execute, import, or evaluate anything from the repository.

#### Scenario: Regular root file

- **GIVEN** a `package.json` at the checkout root
- **WHEN** the checkout is scanned
- **THEN** the file is read and parsed

#### Scenario: Symbolic link

- **GIVEN** a `package.json` that is a symbolic link to a file inside or outside the checkout
- **WHEN** the checkout is scanned
- **THEN** its status is `unreadable` with reason `link` and its target is not read

#### Scenario: Oversized file

- **GIVEN** a `package.json` larger than 1 MiB
- **WHEN** the checkout is scanned
- **THEN** its status is `too_large` and it is not parsed

#### Scenario: Not UTF-8

- **GIVEN** a `Cargo.toml` containing bytes that are not valid UTF-8
- **WHEN** the checkout is scanned
- **THEN** its status is `malformed` with reason `encoding`

#### Scenario: Setup script is never read

- **GIVEN** a checkout with `setup.py` containing code
- **WHEN** the checkout is scanned
- **THEN** `setup.py` is not opened and nothing from it is executed

### Requirement: Each manifest has its own status

The system SHALL record for every supported root manifest a status of `parsed`, `malformed`, `too_large`, or `unreadable` with a fixed reason code, SHALL NOT store file text, and SHALL NOT let one manifest's failure hide another.

#### Scenario: Truncated TOML

- **GIVEN** a truncated `pyproject.toml`
- **WHEN** the checkout is scanned
- **THEN** its status is `malformed` with reason `syntax`

#### Scenario: Deeply nested JSON

- **GIVEN** a `package.json` nested a thousand levels deep
- **WHEN** the checkout is scanned
- **THEN** its status is `malformed` with a fixed reason and the scan continues

#### Scenario: Wrong structure

- **GIVEN** a `package.json` whose top level is an array
- **WHEN** the checkout is scanned
- **THEN** its status is `malformed` with reason `structure`

#### Scenario: One bad file among good ones

- **GIVEN** a malformed `package.json` and a valid `Cargo.toml`
- **WHEN** the checkout is scanned
- **THEN** the Rust technologies are declared and the JavaScript manifest is `malformed`

### Requirement: Dependencies are recorded with constraint and scope

The system SHALL record the direct dependencies of a parsed manifest with name, declared constraint as written, and scope of `runtime`, `dev`, `optional`, or `build`, SHALL NOT merge scopes, and SHALL count dependency kinds it does not support as skipped.

#### Scenario: Python scopes

- **GIVEN** a `pyproject.toml` with project dependencies, an optional-dependencies group, a dependency group, and build requirements
- **WHEN** the checkout is scanned
- **THEN** each dependency carries scope `runtime`, `optional`, `dev`, or `build` respectively

#### Scenario: Poetry tables

- **GIVEN** a `pyproject.toml` using `tool.poetry.dependencies` and a dev group
- **WHEN** the checkout is scanned
- **THEN** the dependencies are recorded with scopes `runtime` and `dev` and `python` itself is not a dependency

#### Scenario: JavaScript scopes

- **GIVEN** a `package.json` with dependencies, devDependencies, optionalDependencies, and peerDependencies
- **WHEN** the checkout is scanned
- **THEN** they carry scopes `runtime`, `dev`, `optional`, and `optional`

#### Scenario: Rust scopes and platform tables

- **GIVEN** a `Cargo.toml` with dependencies, dev-dependencies, build-dependencies, and a target-specific table
- **WHEN** the checkout is scanned
- **THEN** the first three carry `runtime`, `dev`, and `build` and the target-specific entries are counted as skipped

#### Scenario: Go direct and indirect

- **GIVEN** a `go.mod` with direct requirements and requirements marked `// indirect`
- **WHEN** the checkout is scanned
- **THEN** the direct ones are `runtime` and the indirect ones are counted as skipped

#### Scenario: Requirements file scope

- **GIVEN** `requirements.txt` and `requirements-dev.txt`
- **WHEN** the checkout is scanned
- **THEN** the first file's dependencies are `runtime` and the second's are `dev`

#### Scenario: Requirements lines that are not dependencies

- **GIVEN** a requirements file with comments, `-r other.txt`, `-e .`, a URL, and an option line
- **WHEN** the checkout is scanned
- **THEN** none is a dependency and the option, include, editable, and URL lines are counted as skipped

#### Scenario: Constraint kept as written

- **GIVEN** a dependency written `requests>=2.28,<3; python_version >= "3.9"`
- **WHEN** the checkout is scanned
- **THEN** the name is `requests` and the constraint is `>=2.28,<3`

#### Scenario: Python names are normalized

- **GIVEN** dependencies written `Flask_SQLAlchemy` and `zope.interface`
- **WHEN** the checkout is scanned
- **THEN** their names are `flask-sqlalchemy` and `zope-interface`

#### Scenario: Cap

- **GIVEN** a manifest with 300 dependencies
- **WHEN** the checkout is scanned
- **THEN** 200 are stored and the total 300 is reported

#### Scenario: Workspace flag

- **GIVEN** a root `package.json` that declares workspaces
- **WHEN** the checkout is scanned
- **THEN** the manifest carries a workspace flag and its members are not read

### Requirement: Technologies come only from the registry

The system SHALL map a dependency to a technology only through the versioned registry, SHALL record for each technology the set of scopes in which it was declared and the manifests that declared it, and SHALL keep an unknown dependency as a dependency without creating a technology.

#### Scenario: Known dependency

- **GIVEN** `pyproject.toml` declaring `fastapi` as runtime and `pytest` as dev
- **WHEN** the checkout is scanned
- **THEN** the technologies `fastapi` with scope `runtime` and `pytest` with scope `dev` are declared

#### Scenario: Scopes are united

- **GIVEN** a package declared in both dependencies and devDependencies
- **WHEN** the checkout is scanned
- **THEN** its technology carries both scopes

#### Scenario: Same technology from two manifests

- **GIVEN** a dependency declared in `pyproject.toml` and `requirements.txt`
- **WHEN** the checkout is scanned
- **THEN** one technology is recorded with both manifests as evidence

#### Scenario: Unknown dependency

- **GIVEN** a manifest listing a dependency that is not in the registry
- **WHEN** the checkout is scanned
- **THEN** the dependency is recorded and no technology is created

#### Scenario: Ecosystems do not mix

- **GIVEN** a Python dependency and a Rust dependency with the same name
- **WHEN** the checkout is scanned
- **THEN** each is matched only against its own ecosystem's registry entries

### Requirement: Ecosystem states keep absence honest

The system SHALL report each ecosystem as `detected` when a root manifest of it was read, `not_detected` only when the walk was complete and none exists, `unknown` when the walk stopped early before one was seen, and the whole checkout as `not_assessed` when the observation has no registry version.

#### Scenario: Complete and empty

- **GIVEN** a complete scan of a checkout with no supported manifests
- **WHEN** the frameworks are read
- **THEN** every ecosystem is `not_detected`

#### Scenario: Partial walk

- **GIVEN** a scan that stopped at the entry cap before a root manifest was seen
- **WHEN** the frameworks are read
- **THEN** the ecosystem is `unknown`

#### Scenario: Malformed is detected

- **GIVEN** a malformed root `package.json`
- **WHEN** the frameworks are read
- **THEN** JavaScript is `detected` with the manifest `malformed` and no technology is claimed absent

### Requirement: Nested manifests are counted, not parsed

The system SHALL count, per ecosystem, supported manifests found below the checkout root, SHALL NOT parse them, and SHALL NOT expand workspace members.

#### Scenario: Monorepo

- **GIVEN** `package.json` files in three subdirectories and none at the root
- **WHEN** the checkout is scanned
- **THEN** JavaScript reports three nested manifests not parsed and declares no technology

### Requirement: Frameworks are stored on the observation

The system SHALL store the manifests, dependencies, technologies, nested counts, and the registry version with the observation of the same walk, so that they share its time, completeness, and retention of the current and previous observation.

#### Scenario: Stored with the observation

- **GIVEN** a repository with a parsed `pyproject.toml`
- **WHEN** a scan completes
- **THEN** the observation has the manifest, its dependencies, its technologies, and the registry version

#### Scenario: Retention

- **GIVEN** a checkout scanned three times
- **WHEN** the third scan completes
- **THEN** only the second and third observations, with their frameworks, exist

#### Scenario: Older and failed observations

- **GIVEN** an observation made before this detector, and one whose detection failed
- **WHEN** the frameworks are read
- **THEN** each is `not_assessed`

#### Scenario: Detection failure is isolated

- **GIVEN** framework detection raises for one of two checkouts
- **WHEN** the scan runs
- **THEN** the failing checkout has a failed observation, the other keeps its technologies, and the run is partial

### Requirement: Registry is validated versioned data

The system SHALL load the technology registry from versioned data and SHALL reject data with a missing or non-integer version, an entry without a key, name, category, ecosystem, and dependencies, an unknown ecosystem, a duplicate key, or a dependency claimed by two entries in one ecosystem.

#### Scenario: Valid registry

- **GIVEN** registry data with a version and valid entries
- **WHEN** it is loaded
- **THEN** the loaded registry carries the version and the entries

#### Scenario: Malformed registry

- **GIVEN** registry data with a duplicate key or a missing version
- **WHEN** it is loaded
- **THEN** loading fails naming the field

---

### Requirement: Parsed manifests record the package name they declare

The system SHALL record, for each parsed root manifest, the package name it declares: the `[project]` name or the Poetry name in `pyproject.toml`, the `name` in `package.json`, the `[package]` name in `Cargo.toml`, and the `module` path in `go.mod`. A name SHALL be stored in the form used to match dependencies (normalized for its ecosystem), at most 214 characters, and SHALL be absent when the manifest declares none, declares a value that is not text, or is a `requirements*.txt` file. A manifest that is not parsed SHALL have no declared name. Reading the name SHALL NOT change the dependencies, scopes, skipped counts, or statuses reported.

#### Scenario: Name in each ecosystem

- **GIVEN** a `pyproject.toml` named Billing_API, a `package.json` named @acme/ui, a `Cargo.toml` package named ledger-core, and a `go.mod` with module example.com/acme/tool
- **WHEN** the manifests are parsed
- **THEN** the declared names are billing-api, @acme/ui, ledger-core, and example.com/acme/tool

#### Scenario: No name declared

- **GIVEN** a `pyproject.toml` without a project name and a `requirements.txt`
- **WHEN** they are parsed
- **THEN** no declared name is recorded and their dependencies are unchanged

#### Scenario: Name that is not text or too long

- **GIVEN** a `package.json` whose name is a number, and another whose name is 215 characters
- **WHEN** they are parsed
- **THEN** no declared name is recorded for either and the manifests are still reported as parsed

#### Scenario: Unparsed manifest

- **GIVEN** a malformed `package.json`
- **WHEN** the checkout is scanned
- **THEN** the manifest has status malformed and no declared name

#### Scenario: Stored with the observation

- **GIVEN** a scanned checkout with a named manifest
- **WHEN** the index is read
- **THEN** the manifest row carries the declared name and the observation is marked as having recorded names, while an observation made before the migration has neither
