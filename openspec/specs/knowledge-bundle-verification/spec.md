# knowledge-bundle-verification Specification

## Purpose
TBD - created by archiving change openspec-okf-knowledge-rules. Update Purpose after archive.

## Requirements

### Requirement: Required sections per type

The verifier SHALL fail a concept whose type lists `required_sections` in the profile when any listed top-level heading is absent or has no content before the next top-level heading.

#### Scenario: Decision without alternatives

- **GIVEN** the profile requires "Alternatives considered" for type Decision
- **AND** a Decision concept has no such heading
- **WHEN** the verifier runs
- **THEN** it reports an error naming the file and the missing section
- **AND** exits non-zero

#### Scenario: Empty required section

- **GIVEN** a Decision concept has the heading "Consequences" followed directly by another top-level heading
- **WHEN** the verifier runs
- **THEN** it reports an error naming the file and the empty section

#### Scenario: Extra sections allowed

- **GIVEN** a Decision concept has all required sections plus "Related"
- **WHEN** the verifier runs
- **THEN** it reports no section error

### Requirement: Banned delivery words

The verifier SHALL fail a concept whose body or description matches a pattern in the profile's `forbidden_words`, matching case-insensitively.

#### Scenario: Task vocabulary in a concept

- **GIVEN** `forbidden_words` contains `\bthis change\b`
- **AND** a concept body says "as this change adds"
- **WHEN** the verifier runs
- **THEN** it reports an error naming the file and the pattern

#### Scenario: Invalid pattern

- **GIVEN** `forbidden_words` contains an invalid regular expression
- **WHEN** the verifier runs
- **THEN** it reports an error naming the profile and the pattern, and does not crash

### Requirement: Stable concepts have no open questions

The verifier SHALL fail a concept with status `stable` that has a top-level "Open questions" heading.

#### Scenario: Stable concept with a question

- **GIVEN** a concept has status `stable` and a "# Open questions" heading
- **WHEN** the verifier runs
- **THEN** it reports an error naming the file

#### Scenario: Draft concept with a question

- **GIVEN** a concept has status `draft` and a "# Open questions" heading
- **WHEN** the verifier runs
- **THEN** it reports no error for that heading

### Requirement: Deprecated decisions name a replacement

The verifier SHALL fail a Decision with status `deprecated` that has no `superseded_by`, and SHALL fail any concept whose `superseded_by` target does not exist in the bundle or is not a concept of the same type.

#### Scenario: Dangling pointer

- **GIVEN** decision A has status `deprecated` and `superseded_by: /decisions/b.md`
- **AND** no such concept exists
- **WHEN** the verifier runs
- **THEN** it reports an error naming A and the target

#### Scenario: Valid replacement

- **GIVEN** deprecated decision A names an existing Decision B in `superseded_by`
- **WHEN** the verifier runs
- **THEN** it reports no supersession error

#### Scenario: Deprecated without replacement

- **GIVEN** a Decision has status `deprecated` and no `superseded_by`
- **WHEN** the verifier runs
- **THEN** it reports an error naming the file

#### Scenario: Target outside the bundle

- **GIVEN** `superseded_by` points outside the bundle
- **WHEN** the verifier runs
- **THEN** it reports an error and does not crash

### Requirement: Profiles without the new keys keep working

The verifier SHALL skip a check whose profile key is absent and SHALL report no new error for a bundle that passed before.

#### Scenario: Old profile

- **GIVEN** a profile with none of the new keys
- **WHEN** the verifier runs on a bundle that previously passed
- **THEN** the result has the same errors and warnings as before

---
