# repository-ignore Specification

## Purpose
TBD - created by archiving change be-repository-ignore. Update Purpose after archive.

## Requirements

### Requirement: Patterns name directories

The system SHALL read each non-blank line that does not start with `#` as a directory pattern, treating a pattern without a slash as a name matching at any depth below the repository root, and a pattern with a slash as a path from the repository root, where `*` matches within one segment, `**` across segments, `?` one character, case is ignored, a leading slash anchors the pattern at the repository root, a trailing slash is allowed, and backslashes are read as slashes.

#### Scenario: Bare name at any depth

- **GIVEN** the pattern `fixtures`
- **WHEN** directories `fixtures`, `a/fixtures`, and `a/b/fixtures` are tested
- **THEN** all match

#### Scenario: Path from the root

- **GIVEN** the pattern `data/novel/output`
- **WHEN** `data/novel/output` and `other/data/novel/output` are tested
- **THEN** only the first matches

#### Scenario: Glob characters

- **GIVEN** the patterns `data/*/cache` and `build-?`
- **WHEN** `data/x/cache`, `data/x/y/cache`, `build-1`, and `build-12` are tested
- **THEN** only `data/x/cache` and `build-1` match

#### Scenario: Recursive glob

- **GIVEN** the pattern `data/**/cache`
- **WHEN** `data/x/y/cache` is tested
- **THEN** it matches

#### Scenario: Case is ignored

- **GIVEN** the pattern `Fixtures`
- **WHEN** `fixtures` is tested
- **THEN** it matches

#### Scenario: Comments, blanks, and slashes

- **GIVEN** a file with comments, blank lines, `/data/`, and `docs\old`
- **WHEN** it is parsed
- **THEN** the patterns are `data` and `docs/old`, both anchored at the repository root

### Requirement: The file cannot widen the scan

The system SHALL treat a line that starts with `!`, starts with a drive letter, or has a `..` segment as invalid, SHALL report it with its line number, and SHALL skip it while applying the valid lines.

#### Scenario: Invalid lines

- **GIVEN** lines `!keep`, `/etc/x/../y`, `C:/Windows`, `../outside`, and `ok`
- **WHEN** the file is parsed
- **THEN** four problems are reported with line numbers
- **AND** only `ok` applies

### Requirement: The file is bounded

The system SHALL reject a file larger than 64 KiB as a whole, reporting it, and SHALL accept at most 1,000 patterns, reporting the excess.

#### Scenario: Oversized file

- **GIVEN** a file of more than 64 KiB
- **WHEN** it is read
- **THEN** no pattern applies
- **AND** a problem says the file was too large

#### Scenario: Too many patterns

- **GIVEN** a file with 1,001 valid patterns
- **WHEN** it is parsed
- **THEN** the first 1,000 apply
- **AND** a problem reports the excess

### Requirement: Discovery honors the file

When nested repositories are enabled, the system SHALL NOT enter a directory below a repository that matches the patterns of that repository's ignore file or of an enclosing repository's, SHALL count it as excluded, and SHALL NOT report it as a skip. Discovery does not enter projects by default, so it does not read their ignore files by default; file composition always does.

#### Scenario: Ignored directory is not entered

- **GIVEN** a repository whose ignore file lists `data`, containing `data/inner` with a repository
- **WHEN** discovery runs
- **THEN** the inner repository is not found
- **AND** the excluded count includes `data`
- **AND** there is no warning for it

#### Scenario: Only below its own repository

- **GIVEN** two sibling repositories and an ignore file in the first listing `data`
- **WHEN** discovery runs
- **THEN** `data` is skipped in the first and entered in the second

#### Scenario: Nested repositories keep enclosing rules

- **GIVEN** an outer repository ignoring `vendor-data` and a nested repository ignoring `cache`
- **WHEN** discovery runs
- **THEN** inside the nested repository both `vendor-data` and `cache` are skipped

#### Scenario: Ignored directories do not become depth warnings

- **GIVEN** an ignored directory that is also deeper than the depth limit
- **WHEN** discovery runs
- **THEN** it is excluded and no `max_depth` warning counts it

### Requirement: Mistakes are reported

The system SHALL report invalid lines, oversized files, and excess patterns in an `ignore_file` warning giving the number of problems, the files, and up to five problem messages, SHALL NOT change the run status because of them, and SHALL still apply the valid lines.

#### Scenario: Warning for an invalid line

- **GIVEN** a repository whose ignore file has an invalid line and a valid pattern
- **WHEN** discovery runs
- **THEN** the valid pattern applies
- **AND** an `ignore_file` warning names the file and the line
- **AND** the status is unchanged

### Requirement: File composition honors the file

The system SHALL NOT count files in directories matching the checkout's ignore file, and SHALL record in the evidence whether an ignore file was used, its pattern count, and a digest of its patterns.

#### Scenario: Ignored files are not counted

- **GIVEN** a checkout whose ignore file lists `reference`, a directory holding many files
- **WHEN** the composition is computed
- **THEN** those files are not counted and the count is complete

#### Scenario: Evidence of use

- **GIVEN** a checkout with an ignore file of two patterns
- **WHEN** the composition is computed
- **THEN** the evidence records two patterns and their digest, not their text

#### Scenario: No file

- **GIVEN** a checkout without an ignore file
- **WHEN** the composition is computed
- **THEN** the evidence records no ignore file

### Requirement: Only the ignore file is read

The system SHALL read at most 64 KiB of `.vyasaignore` and SHALL open no other repository file beyond the `.git` pointer files.

#### Scenario: Files opened

- **GIVEN** repositories with and without ignore files
- **WHEN** discovery runs
- **THEN** the only files opened are `.git` pointer files and `.vyasaignore` files

---
