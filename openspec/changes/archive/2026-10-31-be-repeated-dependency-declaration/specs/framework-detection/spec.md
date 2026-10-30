# Specifications: be-repeated-dependency-declaration

## 1. Specification Overview

- **OpenSpec Change ID:** `be-repeated-dependency-declaration`
- **Purpose:** Keep dependency storage defined when a manifest declares the same dependency more than once in one scope.
- **Related proposal:** `proposal.md`
- **Related design:** `design.md`
- **Api and data contract:** `api-contract.md`
- **Knowledge references:** `knowledge/decisions/framework-detection-from-manifests.md` — dependency scopes and the one-row-per-name-and-scope rule
- **Team focus:** Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

## 2. Capability: framework-detection

### Purpose

Record the direct dependencies a root manifest declares at the checkout root, with their scopes, as evidence of the technologies the project uses.

### Scope

The storage of parsed dependencies on the observation of the same walk. Reading, filtering, capping, scopes, and technology mapping are unchanged.

## MODIFIED Requirements

### Requirement: Dependencies are recorded with constraint and scope

The system SHALL record the direct dependencies of a parsed manifest with name, declared constraint as written, and scope of `runtime`, `dev`, `optional`, or `build`, SHALL NOT merge scopes, and SHALL count dependency kinds it does not support as skipped. The system SHALL store at most one dependency row per name and scope for a manifest: when the manifest declares the same name more than once in the same scope, the system SHALL store the first declaration, with its constraint, and SHALL NOT store the repeats. A repeat in one scope SHALL NOT fail the scan, change the manifest's status, or affect the dependencies of another manifest. The declared-entry total SHALL be reported as before.

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

#### Scenario: Declared twice in one scope

- **GIVEN** a `pyproject.toml` whose two optional-dependencies groups both declare `pandas`, first as `>=2` and then as `>=1`
- **WHEN** the checkout is scanned
- **THEN** one `pandas` row with scope `optional` and constraint `>=2` is stored, the scan completes, and the manifest is `parsed`

#### Scenario: Same name in two scopes

- **GIVEN** a `package.json` declaring `lodash` in `dependencies` and in `devDependencies`
- **WHEN** the checkout is scanned
- **THEN** two rows are stored, one with scope `runtime` and one with scope `dev`

#### Scenario: Repeat does not disturb other manifests

- **GIVEN** one manifest that repeats a dependency and one that does not
- **WHEN** the checkout is scanned
- **THEN** both manifests are stored with their own observation and no manifest is missing

#### Scenario: A real violation still fails

- **GIVEN** a dependency whose scope is outside `runtime`, `dev`, `optional`, and `build`
- **WHEN** it is stored
- **THEN** the constraint violation still raises rather than being skipped

## 3. Cross-Capability Requirements

None. `project-dependencies` only reads these rows and its behavior is unchanged; the scenarios above cover the shape it reads.

## 4. Quality and Operational Requirements

- **Determinism (NFR-001):** the stored row for a repeated declaration is always the first one in the manifest's parsed order, so the same files give the same rows.
- **No silent data loss:** only a repeat of an already stored name and scope is collapsed; every other insert still raises on a constraint violation.

## 5. Specification Review

- [x] Every in-scope behavior is described by a requirement.
- [x] Every requirement sits inside a delta section heading, and every requirement heading is at level three with its scenarios at level four.
- [x] Requirements use precise, unambiguous, observable language.
- [x] Each requirement has a stable, descriptive name.
- [x] Scenarios describe context, action, and expected outcome.
- [x] Relevant normal, boundary, and failure behaviors are covered.
- [x] Requirements are consistent with the proposal and do not prescribe unnecessary implementation details.
- [x] Cross-capability behavior is specified without unnecessary duplication.
- [x] Quality requirements use measurable criteria where applicable.
- [x] Assumptions and unresolved questions are explicitly identified.
- [x] The specifications provide sufficient detail for design, task breakdown, and verification.

**Status:** Ready for design and task breakdown
