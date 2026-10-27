# review-candidates Specification

## Purpose
TBD - created by archiving change be-review-candidates. Update Purpose after archive.

## Requirements

### Requirement: Candidates are explainable

The system SHALL present each open flag as a candidate with its project, kind, rule id, confidence tier (`high`, `medium`, or `low`), plain-language criteria, and the stored evidence.

#### Scenario: Duplicate checkout candidate

- **GIVEN** an open `duplicate_checkout` flag
- **WHEN** candidates are listed
- **THEN** it shows rule `same_remote_identity`, confidence `high`, criteria text, and its evidence

#### Scenario: Unresolved identity candidate

- **GIVEN** an open `identity_unresolved` flag
- **WHEN** candidates are listed
- **THEN** it shows rule `path_remote_conflict`, confidence `low`, criteria text, and both pieces of evidence

#### Scenario: Cleared flags are not candidates

- **GIVEN** a cleared flag
- **WHEN** candidates are listed
- **THEN** it is absent

### Requirement: Decisions are stored locally

The system SHALL store a reviewer's decision (`open`, `dismissed`, or `confirmed`, with an optional note of at most 500 characters) for an open candidate in the local index, and SHALL NOT write it anywhere else.

#### Scenario: Dismiss

- **GIVEN** an open candidate
- **WHEN** the reviewer dismisses it with a note
- **THEN** it is listed as `dismissed` with the note and the decision time

#### Scenario: Change of mind

- **GIVEN** a dismissed candidate
- **WHEN** the reviewer sets it back to `open`
- **THEN** it is listed as `open`

#### Scenario: Unknown candidate

- **GIVEN** no open flag of that kind on that project
- **WHEN** a decision is attempted
- **THEN** `CANDIDATE_NOT_FOUND` is raised and nothing is written

#### Scenario: Invalid decision

- **GIVEN** an open candidate
- **WHEN** a status other than `open`, `dismissed`, or `confirmed`, or a note over 500 characters, is given
- **THEN** `INVALID_DECISION` is raised and nothing is written

### Requirement: A decision holds only for the evidence it was made on

The system SHALL list a candidate as `open` when its current evidence differs from the evidence stored with the decision, and SHALL keep the decision when a cleared flag is raised again with the same evidence.

#### Scenario: Evidence changed

- **GIVEN** a dismissed duplicate candidate whose number of active checkouts later changes
- **WHEN** candidates are listed
- **THEN** it is `open`

#### Scenario: Same condition returns

- **GIVEN** a dismissed candidate whose flag cleared and later reopened with the same evidence
- **WHEN** candidates are listed
- **THEN** it is `dismissed`

### Requirement: Nothing is changed automatically

The system SHALL NOT modify, archive, merge, or delete any project, checkout, alias, or flag because of a decision, and SHALL NOT flag a project because it is inaccessible or was not scanned recently.

#### Scenario: Decision leaves the index alone

- **GIVEN** the index contents
- **WHEN** a candidate is confirmed
- **THEN** only `review_decisions` changes

#### Scenario: Inaccessible project

- **GIVEN** a stored project whose path is later reported inaccessible
- **WHEN** the run is stored and candidates are listed
- **THEN** no candidate exists for it

#### Scenario: Not scanned recently

- **GIVEN** a project not seen for longer than the freshness window
- **WHEN** candidates are listed
- **THEN** no candidate exists for it

### Requirement: Decisions are never shared

The system SHALL keep review decisions in a table that no export or synchronization reads, and SHALL migrate existing indexes to include it.

#### Scenario: Migration

- **GIVEN** a schema 3 index with open flags
- **WHEN** it is opened
- **THEN** `review_decisions` exists and is empty, and a backup exists
