# Specifications: be-language-detector

## 1. Specification Overview

- **OpenSpec Change ID:** `be-language-detector`
- **Purpose:** Report the languages of one checkout as files detected by extension and languages declared by manifest name, kept separate.
- **Related proposal:** `proposal.md`
- **Related design:** `design.md`
- **Api and data contract:** `api-contract.md`
- **Knowledge references:** `knowledge/architecture/scanning-and-evidence/detector-inventory.md` (§9.3), `knowledge/decisions/language-evidence-statuses.md`
- **Team focus:** Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

## 2. Capability: language-detection

### Purpose

Say which languages a checkout contains or declares, and how that was established.

### Scope

One checkout path per call. No persistence, no MCP, no discovery.

## ADDED Requirements

### Requirement: Files detected by extension

The system SHALL map each file with a code extension to exactly one language label from the versioned data, compared case-insensitively, and SHALL report the count per label as `files_detected`.

#### Scenario: Extensions give counts

- **GIVEN** a checkout with 3 `.py` files and 2 `.rs` files
- **WHEN** languages are detected
- **THEN** Python has 3 `files_detected` and Rust has 2

#### Scenario: Extension case ignored

- **GIVEN** files named `a.PY` and `b.py`
- **WHEN** languages are detected
- **THEN** Python has 2 `files_detected`

#### Scenario: Shared extension maps to one label

- **GIVEN** 2 `.h` files and the data maps `.h` to the label `C/C++ header`
- **WHEN** languages are detected
- **THEN** `C/C++ header` has 2 `files_detected` and no other label counts them

#### Scenario: Unknown types are ignored

- **GIVEN** a file named `data.xyz` and a file with no extension
- **WHEN** languages are detected
- **THEN** no language is reported for them

#### Scenario: Content is not read

- **GIVEN** a file named `notes.md` whose content is Python source
- **WHEN** languages are detected
- **THEN** no language is reported for it and no file is opened

### Requirement: Histogram agrees with the code count

The system SHALL return `files_detected` counts that sum to the code count that `compose` returns for the same checkout, limits, and exclusions.

#### Scenario: Sum equals code count

- **GIVEN** a mixed checkout with code, documentation, and other files
- **WHEN** languages are detected and the composition is computed
- **THEN** the `files_detected` counts sum to the composition's code count

#### Scenario: Partial sum equals partial code count

- **GIVEN** a checkout larger than the entry cap
- **WHEN** languages are detected and the composition is computed with the same limits
- **THEN** the sum still equals the composition's code count

### Requirement: Declared by manifest presence

The system SHALL report a language as `declared` when a file whose name matches a recognized manifest name, compared case-insensitively, exists in the walked tree, and SHALL NOT read the manifest.

#### Scenario: Manifest without sources

- **GIVEN** a checkout with a `Cargo.toml` and no `.rs` files
- **WHEN** languages are detected
- **THEN** Rust is `declared`
- **AND** Rust has no `files_detected` entry

#### Scenario: Nested manifest

- **GIVEN** a `go.mod` in a subdirectory
- **WHEN** languages are detected
- **THEN** Go is `declared`

#### Scenario: Unrecognized manifest

- **GIVEN** a file named `project.manifest`
- **WHEN** languages are detected
- **THEN** no language is declared

### Requirement: Statuses stay separate

The system SHALL keep `files_detected` and `declared` as distinct results and SHALL NOT merge them into one claim.

#### Scenario: Found both ways

- **GIVEN** a `pyproject.toml` and 2 `.py` files
- **WHEN** languages are detected
- **THEN** Python is `declared`
- **AND** Python has 2 `files_detected`

### Requirement: Partial walk reports absence as unknown

The system SHALL mark the result partial naming the bound when the walk stops early, and SHALL treat a language not found in a partial result as unknown, never absent.

#### Scenario: Entry cap reached

- **GIVEN** a checkout with more entries than the entry cap
- **WHEN** languages are detected
- **THEN** the result is partial naming the entry cap
- **AND** `is_absent("Rust")` is unknown (None) when Rust was not found

#### Scenario: Complete result

- **GIVEN** a tree within all limits and no Rust files or manifests
- **WHEN** languages are detected
- **THEN** the result is complete
- **AND** `is_absent("Rust")` is true

### Requirement: Evidence

The system SHALL return the file-type data version, the exclusion set, the limits used, and the completeness marker with every result, and SHALL return equal results for the same tree listed in a different directory order.

#### Scenario: Evidence present

- **GIVEN** any detected result
- **WHEN** it is read
- **THEN** it carries the data version, the sorted exclusion set, the limits, and the completeness marker

#### Scenario: Deterministic order

- **GIVEN** the same tree listed in two directory orders
- **WHEN** languages are detected for each
- **THEN** the results are equal

### Requirement: Validated language data

The system SHALL load `languages` (extension to non-empty label) and `manifests` (file name to non-empty label) from the file-type data, SHALL treat both as optional for version 1 data, and SHALL reject data whose `languages` keys differ from `code_extensions` or that is malformed.

#### Scenario: Valid data

- **GIVEN** version 2 data with `languages` keys equal to `code_extensions` and a `manifests` map
- **WHEN** it is loaded
- **THEN** the loaded types carry both maps

#### Scenario: Version 1 data

- **GIVEN** version 1 data with no `languages` or `manifests`
- **WHEN** it is loaded
- **THEN** loading succeeds and detection reports no language

#### Scenario: Languages disagree with code extensions

- **GIVEN** data where `languages` has an extension missing from `code_extensions`
- **WHEN** it is loaded
- **THEN** loading fails naming the extension

#### Scenario: Malformed label

- **GIVEN** data where a label is empty or not a string
- **WHEN** it is loaded
- **THEN** loading fails naming the field

---

## 5. Specification Review

- [x] Every in-scope behavior is described by a requirement.
- [x] Every requirement sits inside a delta section heading.
- [x] Scenarios cover normal, boundary, and failure behavior.
- [x] Assumptions and unresolved questions are identified in the proposal.

**Status:** Draft
