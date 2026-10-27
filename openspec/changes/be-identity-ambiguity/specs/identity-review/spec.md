# Specifications: be-identity-ambiguity

## 1. Specification Overview

- **OpenSpec Change ID:** `be-identity-ambiguity`
- **Purpose:** Raise deterministic review flags for duplicate checkouts and unresolved identity.
- **Related proposal:** `proposal.md`
- **Related design:** `design.md`
- **Api and data contract:** `api-contract.md`
- **Knowledge references:** `knowledge/concepts/project-identity.md`, `knowledge/decisions/stored-identity-with-aliases.md`
- **Team focus:** Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

## 2. Capability: identity-review

### Purpose

Make identity problems visible to a person without resolving them automatically.

### Scope

Flags, the `ambiguous` status, and their events. Obsolete candidates, other duplicate rules, and reviewer decisions are not covered.

## ADDED Requirements

### Requirement: Duplicate checkouts are flagged

The system SHALL keep one `duplicate_checkout` flag open for a project while it has more than one `active` checkout, with the rule `same_remote_identity`, the project's aliases, and the number of active checkouts as evidence, and SHALL NOT merge, move, or delete anything because of it.

#### Scenario: Two clones

- **GIVEN** two directories with the same remote identity
- **WHEN** their run is stored
- **THEN** one project has two active checkouts and one open `duplicate_checkout` flag with that evidence

#### Scenario: One clone moved

- **GIVEN** a project whose old checkout is `missing` and whose new checkout is `active`
- **WHEN** it is rescanned
- **THEN** no `duplicate_checkout` flag is open

#### Scenario: Clone removed

- **GIVEN** an open `duplicate_checkout` flag
- **WHEN** a complete run no longer finds one of the two checkouts
- **THEN** the flag is `cleared` and a `resolved` event is recorded

#### Scenario: Names alone never qualify

- **GIVEN** two repositories with the same folder name and different remotes
- **WHEN** they are stored
- **THEN** no flag is raised

### Requirement: Conflicting evidence makes identity ambiguous

The system SHALL, when a candidate's remote identity belongs to one project and its checkout path to another, set the path's project to `ambiguous` and keep an `identity_unresolved` flag open with the alias, the alias owner, and the path's project as evidence, creating and merging nothing.

#### Scenario: Conflict flagged

- **GIVEN** project B whose checkout is re-cloned from project A's remote
- **WHEN** the run is stored
- **THEN** B is `ambiguous`, one `identity_unresolved` flag is open on B with both projects named, and a `flagged` event exists

#### Scenario: Ambiguity is visible

- **GIVEN** an ambiguous project
- **WHEN** projects are listed
- **THEN** its `identity_status` is `ambiguous`, never `resolved`

#### Scenario: Evidence repaired

- **GIVEN** an ambiguous project whose checkout later reports a remote identity no other project owns
- **WHEN** it is rescanned
- **THEN** its status is `resolved` (or `provisional` when it has no alias), the flag is `cleared`, and a `resolved` event is recorded

#### Scenario: Absence does not clear

- **GIVEN** an ambiguous project
- **WHEN** a run omits its checkout
- **THEN** the project stays `ambiguous` and the flag stays open

### Requirement: Flags are idempotent and audited

The system SHALL keep at most one flag per project and kind, record a `flagged` event when a flag opens and a `resolved` event when it clears, add nothing when a rescan leaves the evidence unchanged, and keep no path and no URL in flag evidence or event details.

#### Scenario: Repeated scan

- **GIVEN** an open flag
- **WHEN** the same run is stored again
- **THEN** the flag count and event count are unchanged

#### Scenario: Reopened

- **GIVEN** a cleared flag
- **WHEN** the same condition returns
- **THEN** the same row is `open` again and a new `flagged` event is recorded

#### Scenario: Listing

- **GIVEN** open and cleared flags
- **WHEN** open flags are listed
- **THEN** only open ones are returned, in a stable order, each with its project, kind, evidence, and times

### Requirement: Existing indexes are migrated

The system SHALL, when opening an index at schema 2, add `review_flags` and extend the event kinds with `flagged` and `resolved` while keeping every existing event, and SHALL derive flags for conflicts and duplicates already present.

#### Scenario: Migration with data

- **GIVEN** a schema 2 index with events and a project with two active checkouts
- **WHEN** it is opened
- **THEN** every event is kept, the project has an open `duplicate_checkout` flag, and a backup exists
