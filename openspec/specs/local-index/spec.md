# local-index Specification

## Purpose
TBD - created by archiving change be-local-index. Update Purpose after archive.

## Requirements

### Requirement: The database is created safely

The system SHALL create the index file `index.sqlite3` in the data directory, creating the directory when missing, with user-only permissions on POSIX, and SHALL open every connection with foreign keys on, WAL journal mode, and a 5 second busy timeout.

#### Scenario: First open

- **GIVEN** a data directory that does not exist
- **WHEN** the index is opened
- **THEN** the directory and the file exist, the schema is at the current version, and no workspace root was touched

#### Scenario: Permissions on POSIX

- **GIVEN** a platform with POSIX permissions
- **WHEN** the index is created
- **THEN** the directory has mode 0700 and the file mode 0600

#### Scenario: Pragmas

- **GIVEN** an open connection
- **WHEN** its pragmas are read
- **THEN** foreign keys are on, the journal mode is WAL, and the busy timeout is 5000 ms

### Requirement: Migrations are forward-only

The system SHALL record the schema version in `PRAGMA user_version`, apply each pending numbered migration in one transaction, copy the database with the SQLite backup API before applying any, and refuse a database whose version is higher than the code's with `INDEX_SCHEMA_TOO_NEW`, changing nothing.

#### Scenario: Pending migration

- **GIVEN** a database at an older version with projects stored
- **WHEN** it is opened
- **THEN** a backup copy exists, the version is current, and the projects are unchanged

#### Scenario: Failed migration

- **GIVEN** a migration that raises part-way
- **WHEN** it is applied
- **THEN** that migration's changes are rolled back, the version is unchanged, and a controlled error is raised

#### Scenario: Newer schema

- **GIVEN** a database with a version above the code's
- **WHEN** it is opened
- **THEN** `INDEX_SCHEMA_TOO_NEW` is raised and the file is byte-identical to before

#### Scenario: Up to date

- **GIVEN** a database at the current version
- **WHEN** it is opened again
- **THEN** no backup is made and nothing is migrated

### Requirement: Discovered projects are stored

The system SHALL store each eligible repository of a discovery run as a project with a checkout, in one transaction per project, and SHALL keep them after the process ends.

#### Scenario: New project

- **GIVEN** an empty index and a run with one eligible repository
- **WHEN** the run is stored
- **THEN** one project and one checkout exist and the project is `active`

#### Scenario: Survives restart

- **GIVEN** a stored run
- **WHEN** the index is closed and opened again
- **THEN** the same projects are returned

#### Scenario: Changed project

- **GIVEN** a stored project whose remote or markers changed
- **WHEN** a new run is stored
- **THEN** the project reflects the new values and keeps its identifier

#### Scenario: Remote kept without credentials

- **GIVEN** a candidate with a normalized remote
- **WHEN** it is stored
- **THEN** only the provider, host, and `host/org/repo` identity are stored, never the original URL

### Requirement: Rescans do not duplicate

The system SHALL match a candidate to an existing project by its canonical checkout path, so storing the same run twice, or the same tree in a different order, yields the same projects.

#### Scenario: Same tree twice

- **GIVEN** a stored run
- **WHEN** an identical run is stored
- **THEN** the number of projects is unchanged and each keeps its identifier

#### Scenario: Different order

- **GIVEN** two runs listing the same repositories in a different order
- **WHEN** both are stored
- **THEN** the projects and identifiers are the same

### Requirement: A vanished project is marked, not erased

The system SHALL mark a stored checkout under a scanned root `missing` when a complete run no longer finds it, and `inaccessible` when the run reports it as inaccessible, keep its project and history, and restore `active` when a later run finds it.

#### Scenario: Directory removed

- **GIVEN** a stored project and a complete run of its root that omits it
- **WHEN** the run is stored
- **THEN** the project is `missing` and its record and history remain

#### Scenario: Unreadable

- **GIVEN** a stored project and a run that reports its path as inaccessible
- **WHEN** the run is stored
- **THEN** the project is `inaccessible` and its record remains

#### Scenario: Partial run

- **GIVEN** a stored project and a `partial` or `failed` run that omits it
- **WHEN** the run is stored
- **THEN** the project's state is unchanged

#### Scenario: Skipped directories

- **GIVEN** a stored project and a `completed` run that reports directories skipped by depth, link, or Git-link policy
- **WHEN** the run is stored
- **THEN** no project is marked `missing`, because the whole tree was not seen

#### Scenario: Reappears

- **GIVEN** a `missing` project
- **WHEN** a run finds it again
- **THEN** it is `active` with the same identifier

#### Scenario: Other roots untouched

- **GIVEN** projects stored from root A and a complete run of root B
- **WHEN** the run is stored
- **THEN** the projects from root A are unchanged

### Requirement: Runs have a visible lifecycle

The system SHALL write a scan run as `running` before storing projects and finish it as `completed`, `partial`, or `failed` from the discovery status, and SHALL commit each project independently so a failure on one leaves earlier projects stored.

#### Scenario: Completed run

- **GIVEN** a complete discovery run
- **WHEN** it is stored
- **THEN** a run row records its status `completed`, start and finish times, and counts

#### Scenario: Failure part-way

- **GIVEN** a run of three repositories and a failure while storing the second
- **WHEN** storing stops
- **THEN** the first project is stored, the second and third are not, the run is `interrupted` or `failed`, and the error is raised

#### Scenario: Previous data kept

- **GIVEN** a stored project and a run that fails before reaching it
- **WHEN** the run ends
- **THEN** the project is unchanged

### Requirement: One writer at a time

The system SHALL allow one storing run at a time through a lock with an owner and a heartbeat, refuse a second with `OPERATION_IN_PROGRESS` instead of waiting, treat a lock whose heartbeat is older than 60 seconds as dead, and mark any run left `running` by a dead writer `interrupted`.

#### Scenario: Second writer refused

- **GIVEN** a run holding the lock
- **WHEN** another process stores a run
- **THEN** it receives `OPERATION_IN_PROGRESS` and writes nothing

#### Scenario: Lock released

- **GIVEN** a run that finishes or fails
- **WHEN** another run starts
- **THEN** it takes the lock

#### Scenario: Dead writer

- **GIVEN** a lock with a heartbeat older than 60 seconds and a run still `running`
- **WHEN** a new run starts
- **THEN** the old run becomes `interrupted` and the new run takes the lock

### Requirement: Freshness is reported

The system SHALL report the index freshness as `current` when the latest run completed within 24 hours, `stale` when it completed earlier, `partial` when the latest run ended `partial`, `failed`, or `interrupted`, and `unknown` when no run exists, and SHALL NOT scan or write when asked.

#### Scenario: Each state

- **GIVEN** an index with no runs, a recent completed run, an old completed run, and an interrupted latest run, in turn
- **WHEN** freshness is read with a fixed clock
- **THEN** it is `unknown`, `current`, `stale`, and `partial`

#### Scenario: Read-only

- **GIVEN** a read-only connection
- **WHEN** freshness and projects are read
- **THEN** no row changes

### Requirement: The index works offline

The system SHALL perform every operation of this capability without network access.

#### Scenario: Sockets blocked

- **GIVEN** socket creation is blocked
- **WHEN** the index is opened, written, and read
- **THEN** every operation succeeds
