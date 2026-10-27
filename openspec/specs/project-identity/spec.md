# project-identity Specification

## Purpose
TBD - created by archiving change be-identity-create-and-rescan. Update Purpose after archive.

## Requirements

### Requirement: Identity is created once from the strongest evidence

The system SHALL give a new project the status `resolved` and source `remote` when its candidate has a normalized remote identity, storing that identity as an alias, and otherwise the status `provisional` and source `path`; and SHALL never change a project's identifier.

#### Scenario: Repository with a remote

- **GIVEN** an eligible repository whose remote identity is `github.com/o/r`
- **WHEN** its run is stored
- **THEN** the project is `resolved` from `remote`, has the alias `github.com/o/r`, and one `created` event exists

#### Scenario: Repository without a usable remote

- **GIVEN** an eligible repository with no remote, an ambiguous remote, or a local-path remote
- **WHEN** its run is stored
- **THEN** the project is `provisional` from `path`, has no alias, and one `created` event exists

### Requirement: Rediscovery finds the project by alias, then by path

The system SHALL look a candidate up first by its remote identity alias and then by its checkout path, and SHALL NOT create a second project for either.

#### Scenario: Rescan

- **GIVEN** a stored repository with a remote
- **WHEN** the same run is stored again
- **THEN** the project count and identifiers are unchanged and no event is added

#### Scenario: Moved or renamed

- **GIVEN** a stored repository with a remote, later found at a different path with the same remote
- **WHEN** the new run is stored
- **THEN** the project keeps its identifier, gains a checkout at the new path, and its old checkout becomes `missing` once a complete run omits it

#### Scenario: Project state follows its checkouts

- **GIVEN** a project with one `missing` and one `active` checkout
- **WHEN** it is listed
- **THEN** the project is `active`, and it is `missing` only when no checkout is active or inaccessible

#### Scenario: Provisional project moved

- **GIVEN** a stored repository without a remote, later found at a different path
- **WHEN** the new run is stored
- **THEN** it is a new provisional project and the old one becomes `missing`

### Requirement: Later evidence becomes an alias

The system SHALL, when a known checkout reports a remote identity not yet stored, add it as an alias of that checkout's project, move a `provisional` project to `resolved` from `remote`, and record an event, and SHALL keep earlier aliases.

#### Scenario: Remote added

- **GIVEN** a provisional project whose repository later gains a remote
- **WHEN** it is rescanned
- **THEN** the project is `resolved`, has the alias, keeps its identifier, and an `alias_added` event exists

#### Scenario: Remote renamed

- **GIVEN** a resolved project whose remote identity changes to a new one
- **WHEN** it is rescanned
- **THEN** both identities are aliases of the project and the project is not duplicated

#### Scenario: Remote removed

- **GIVEN** a resolved project whose repository loses its remote
- **WHEN** it is rescanned
- **THEN** the project keeps its status and aliases

### Requirement: Conflicting evidence is preserved

The system SHALL, when a candidate's alias belongs to one project and its checkout path to another, leave both projects and the checkout unchanged and record an `identity_conflict` event on the path's project.

#### Scenario: Alias and path disagree

- **GIVEN** project A with alias `h/o/a` and project B whose checkout was re-cloned from `h/o/a`
- **WHEN** the run is stored
- **THEN** neither project is merged or moved, and B has an `identity_conflict` event naming the alias

### Requirement: Identity changes are recorded

The system SHALL record each identity event with its project, kind (`created`, `alias_added`, `identity_conflict`), the run, a time, and details holding no path and no remote URL, and SHALL NOT record an event when nothing changed.

#### Scenario: Event contents

- **GIVEN** any recorded event
- **WHEN** it is read
- **THEN** it names the project, kind, run, and time, and its details contain no filesystem path

### Requirement: Existing indexes are migrated

The system SHALL, when opening an index at schema 1, add the identity columns and tables, give every project with a stored remote identity that alias and the status `resolved`, leave the rest `provisional`, and keep every project and checkout.

#### Scenario: Migration with data

- **GIVEN** an index at schema 1 with a project that has a remote and one that has none
- **WHEN** it is opened
- **THEN** the first is `resolved` with its alias, the second `provisional`, and no project is lost

#### Scenario: Two projects with one remote

- **GIVEN** an index at schema 1 with two projects sharing a remote identity
- **WHEN** it is opened
- **THEN** the alias belongs to the project whose checkout was stored first, and both projects remain
