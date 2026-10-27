# file-composition Specification

## Purpose
TBD - created by archiving change be-file-composition-counts. Update Purpose after archive.

## Requirements

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

The system SHALL NOT follow directory symlinks or junctions, SHALL count a symlinked file as itself, and SHALL NOT count files inside directories whose name matches the exclusion set, compared case-insensitively. The checkout root itself SHALL NOT be excluded by name.

#### Scenario: Symlink escape

- **GIVEN** a directory symlink inside the checkout points outside it
- **WHEN** the composition is computed
- **THEN** no file behind the symlink is counted

#### Scenario: Junction escape

- **GIVEN** a directory junction inside the checkout points outside it
- **WHEN** the composition is computed
- **THEN** no file behind the junction is counted

#### Scenario: Excluded directory name ignores case

- **GIVEN** the exclusion set contains `node_modules` and the checkout has a directory named `Node_Modules`
- **WHEN** the composition is computed
- **THEN** files in that directory are not counted

#### Scenario: Checkout named like an exclusion

- **GIVEN** the checkout directory is itself named `build`, which is in the exclusion set
- **WHEN** the composition is computed
- **THEN** its files are counted

#### Scenario: Excluded directory

- **GIVEN** a directory named in the exclusion set contains files
- **WHEN** the composition is computed
- **THEN** those files are not counted
- **AND** the exclusion set is recorded as evidence

### Requirement: Evidence

The system SHALL return with every result the file-type data version, the exclusion set, the limits used, and the completeness marker.

#### Scenario: Evidence present

- **GIVEN** any computed composition
- **WHEN** the result is read
- **THEN** it carries the data version, the sorted exclusion set, the limits used, and the completeness marker

#### Scenario: Deterministic order

- **GIVEN** the same tree listed in two different directory orders
- **WHEN** the composition is computed for each
- **THEN** the results are equal

#### Scenario: Partial counts are repeatable

- **GIVEN** a tree larger than the entry cap
- **WHEN** the composition is computed twice
- **THEN** both results have the same counts and the same stopping bound

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

### Requirement: One walk feeds counts and languages

The system SHALL walk a checkout once per scan and derive both the counts and the language results from that file list, and SHALL keep `compose` and `detect_languages` returning the same results as before.

#### Scenario: Languages sum to the code count

- **GIVEN** a checkout with files of recognized code extensions, documentation, and other types
- **WHEN** it is scanned once
- **THEN** the language counts sum to the code count of the same scan

#### Scenario: Walk happens once

- **GIVEN** a scan of one checkout
- **WHEN** the scan runs
- **THEN** the checkout is walked exactly once

#### Scenario: Public functions unchanged

- **GIVEN** any tree
- **WHEN** `compose` and `detect_languages` are called
- **THEN** each returns what it returned before this change

### Requirement: Counts are stored on the observation

The system SHALL store the code, documentation, and other counts on the same observation as the languages of that walk, so that they share its time, completeness, and retention of the current and previous observation.

#### Scenario: Counts stored

- **GIVEN** a repository with 3 Python files and 2 Markdown files
- **WHEN** a scan completes
- **THEN** the observation holds 3 code, 2 documentation, and 0 other files

#### Scenario: Partial walk stores lower bounds

- **GIVEN** a checkout larger than the entry cap
- **WHEN** a scan completes
- **THEN** the observation is partial naming the cap and holds the counts gathered so far

#### Scenario: Retention

- **GIVEN** a checkout scanned three times
- **WHEN** the third scan completes
- **THEN** only the second and third observations, with their counts, exist

### Requirement: Failed and older observations have no counts

The system SHALL leave the counts empty on a failed observation and on an observation made before counts existed, and SHALL NOT store zeros for them.

#### Scenario: Failed observation

- **GIVEN** detection fails for a checkout
- **WHEN** the scan stores it
- **THEN** the observation is failed and its counts are empty

#### Scenario: Upgrade keeps old observations

- **GIVEN** an index at the previous version with language observations
- **WHEN** it is opened for writing
- **THEN** the observations are unchanged and their counts are empty

---
