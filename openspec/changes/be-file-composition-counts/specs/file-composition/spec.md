# Specifications: be-file-composition-counts

## 1. Specification Overview

- **OpenSpec Change ID:** `be-file-composition-counts`
- **Purpose:** Count code, documentation, and other files of one checkout from file names, within bounds.
- **Related proposal:** `proposal.md`
- **Related design:** `design.md`
- **Api and data contract:** `api-contract.md`
- **Knowledge references:** `knowledge/architecture/scanning-and-evidence/detector-inventory.md` (§9.13), `knowledge/decisions/file-composition-data-and-limits.md`
- **Team focus:** Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

## 2. Capability: file-composition

### Purpose

Report how many files are code, documentation, or other, with a completeness marker and evidence.

### Scope

One checkout path per call. No persistence, no MCP, no discovery.

## ADDED Requirements

### Requirement: Counts classify by extension and agree

The system SHALL classify each counted file by its extension, compared case-insensitively, against the file-type data, and SHALL return counts where code plus documentation plus other equals the total.

#### Scenario: Mixed checkout

- **GIVEN** a checkout with 3 code files, 2 documentation files, and 4 files of other types
- **WHEN** the composition is computed
- **THEN** the counts are 3 code, 2 documentation, 4 other, and 9 total

#### Scenario: Extension case ignored

- **GIVEN** files named `a.MD` and `b.md`, with `.md` a documentation extension
- **WHEN** the composition is computed
- **THEN** both are counted as documentation

#### Scenario: Unknown type is other

- **GIVEN** a checkout containing only files with an extension in neither list, and files with no extension
- **WHEN** the composition is computed
- **THEN** every file is counted as other and none as code

#### Scenario: Content is not read

- **GIVEN** a file named `notes.md` whose content is source code
- **WHEN** the composition is computed
- **THEN** it is counted as documentation
- **AND** no file is opened

### Requirement: Documentation-only indicator

The system SHALL derive `documentation_only` as true when the count is complete, documentation files exist, and code files do not; false when the count is complete otherwise; and unknown when the count is partial.

#### Scenario: Documentation only

- **GIVEN** a complete count with documentation files and no code files
- **WHEN** the indicator is derived
- **THEN** it is true

#### Scenario: Documentation and code

- **GIVEN** a complete count with documentation files and code files
- **WHEN** the indicator is derived
- **THEN** it is false

#### Scenario: Empty checkout

- **GIVEN** a checkout with no files
- **WHEN** the composition is computed
- **THEN** all counts are zero, the count is complete, and the indicator is false

### Requirement: Bounded walk with a partial marker

The system SHALL stop descending when the depth limit, the time limit, or the entry cap is reached or a directory cannot be read, SHALL mark the count partial naming the bound, and SHALL report the counts gathered so far as lower bounds.

#### Scenario: Entry cap reached

- **GIVEN** a checkout with more entries than the entry cap
- **WHEN** the composition is computed
- **THEN** the count is partial naming the entry cap
- **AND** the documentation-only indicator is unknown

#### Scenario: Depth limit reached

- **GIVEN** files exist deeper than the depth limit
- **WHEN** the composition is computed
- **THEN** the count is partial naming the depth limit

#### Scenario: Time limit reached

- **GIVEN** the clock passes the time limit during the walk
- **WHEN** the composition is computed
- **THEN** the count is partial naming the time limit

#### Scenario: Unreadable directory

- **GIVEN** a directory inside the checkout cannot be read
- **WHEN** the composition is computed
- **THEN** the count is partial naming an unreadable directory
- **AND** files in readable directories are still counted

#### Scenario: Limits are not exceeded

- **GIVEN** a tree within all limits
- **WHEN** the composition is computed
- **THEN** the count is complete with no stopping bound

### Requirement: Symlinks and exclusions

The system SHALL NOT follow directory symlinks, SHALL count a symlinked file as itself, and SHALL NOT count files inside directories named in the exclusion set.

#### Scenario: Symlink escape

- **GIVEN** a directory symlink inside the checkout points outside it
- **WHEN** the composition is computed
- **THEN** no file behind the symlink is counted

#### Scenario: Excluded directory

- **GIVEN** a directory named in the exclusion set contains files
- **WHEN** the composition is computed
- **THEN** those files are not counted
- **AND** the exclusion set is recorded as evidence

### Requirement: Evidence

The system SHALL return with every result the file-type data version, the exclusion set, and the completeness marker.

#### Scenario: Evidence present

- **GIVEN** any computed composition
- **WHEN** the result is read
- **THEN** it carries the data version, the sorted exclusion set, and the completeness marker

#### Scenario: Deterministic order

- **GIVEN** the same tree listed in two different directory orders
- **WHEN** the composition is computed for each
- **THEN** the results are equal

### Requirement: Validated versioned file-type data

The system SHALL load file-type data with an integer version, a list of code extensions, and a list of documentation extensions, each extension starting with a dot, and SHALL reject data in which an extension appears in both lists or any field is malformed.

#### Scenario: Valid data

- **GIVEN** a data file with a version and two disjoint extension lists
- **WHEN** it is loaded
- **THEN** the loaded types carry the version and lower-cased extensions

#### Scenario: Overlapping lists

- **GIVEN** a data file where `.md` is in both lists
- **WHEN** it is loaded
- **THEN** loading fails with an error naming the extension

#### Scenario: Malformed data

- **GIVEN** a data file with a missing version or an extension without a leading dot
- **WHEN** it is loaded
- **THEN** loading fails with an error naming the field

---

## 5. Specification Review

- [x] Every in-scope behavior is described by a requirement.
- [x] Every requirement sits inside a delta section heading.
- [x] Scenarios cover normal, boundary, and failure behavior.
- [x] Assumptions and unresolved questions are identified in the proposal.

**Status:** Draft
