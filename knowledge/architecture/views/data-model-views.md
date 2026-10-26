---
type: Architecture
title: "Data Model Views"
description: Entity relationships at table level, and the state machines of identity, availability, value status, and runs.
tags: [data-model, er-diagram, state-machine, statuses]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: dm
    resource: /architecture/data-model.md
    title: Data Model
  - id: tables
    resource: /architecture/local-storage/tables-core.md
    title: Proposed Tables: Core
  - id: ops
    resource: /architecture/local-storage/tables-operations.md
    title: Proposed Tables: Relationships, Runs, and Inventory
---

# Question

Which tables hold what, how do they connect, and which states can the key entities be in?

# Tables and their keys

```mermaid
erDiagram
    projects ||--o{ project_repositories : has
    repositories ||--o{ project_repositories : belongs_to
    repositories ||--o{ local_checkouts : checked_out_as
    projects ||--o{ metadata_observations : described_by
    repositories ||--o{ metadata_observations : described_by
    metadata_observations ||--o{ evidence_references : supported_by
    projects ||--o{ project_relationships : source
    projects ||--o{ project_relationships : target
    scan_runs ||--o{ scan_item_results : contains
    scan_runs ||--o{ detector_runs : contains
    repositories ||--o{ file_inventory : inventory_of
    projects {
        text project_id PK
        text display_name
        text identity_status
        text lifecycle_status
        text details_status
        text last_observed_at
    }
    repositories {
        text repository_id PK
        text remote_identity
        text provider_repository_id
        text repository_status
    }
    project_repositories {
        text project_id FK
        text repository_id FK
        text association_type
    }
    local_checkouts {
        text checkout_id PK
        text repository_id FK
        text local_path
        text checkout_status
    }
    metadata_observations {
        text observation_id PK
        text entity_type
        text entity_id
        text field_key
        text status
        text detector_id
        text detector_version
        int is_current
    }
    evidence_references {
        text evidence_id PK
        text observation_id FK
        text relative_path
        text content_fingerprint
    }
    project_relationships {
        text relationship_id PK
        text source_project_id FK
        text target_project_id FK
        text relationship_type
        text status
    }
    scan_runs {
        text run_id PK
        text status
        text started_at
        text completed_at
    }
    scan_item_results {
        text result_id PK
        text run_id FK
        text status
    }
    detector_runs {
        text detector_run_id PK
        text run_id FK
        text detector_id
        text input_fingerprint
    }
    file_inventory {
        text inventory_id PK
        text repository_id FK
        text relative_path
        text content_fingerprint
    }
```

The diagram shows the key columns only; the full field lists are in the table concepts. `local_path` is machine-local and is
never exported. The resolved index is a projection built from observations and is not drawn.

# Identity status

```mermaid
stateDiagram-v2
  [*] --> provisional: weak evidence only
  [*] --> resolved: strong evidence at creation
  provisional --> resolved: stronger evidence found
  resolved --> ambiguous: conflicting evidence appears
  provisional --> ambiguous: conflicting evidence appears
  ambiguous --> resolved: evidence or review settles it
```

# Availability of repositories and checkouts

```mermaid
stateDiagram-v2
  [*] --> unknown
  unknown --> available: successfully observed
  available --> inaccessible: permission or transient failure
  inaccessible --> available: access restored
  available --> missing: confirmed absent
  missing --> available: reappears
  inaccessible --> missing: confirmed absent
```

A timeout or permission failure never sets `missing`, and `missing` never deletes the project or repository record.

# Value status of an observation

```mermaid
stateDiagram-v2
  [*] --> unknown
  unknown --> observed: detector finds evidence
  unknown --> declared: authoritative source states it
  observed --> not_detected: complete inspection finds nothing
  observed --> stale: source may have changed
  observed --> inaccessible: source cannot be read
  observed --> conflicting: sources disagree
  declared --> conflicting: sources disagree
  stale --> observed: refreshed
  inaccessible --> observed: readable again
  conflicting --> observed: conflict resolved by ownership
```

# Run status

```mermaid
stateDiagram-v2
  [*] --> pending
  pending --> running
  running --> completed: scope completed
  running --> partial: some items failed or incomplete
  running --> failed: essential purpose not met
  running --> cancelled: stopped by the user
  running --> interrupted: process ended unexpectedly
  completed --> [*]
  partial --> [*]
  failed --> [*]
  cancelled --> [*]
  interrupted --> [*]
```

An interrupted or cancelled run is never reported as a successful complete run.

# Related

- [Data Model](/architecture/data-model.md)
- [Local Storage](/architecture/local-storage.md)
- [Evidence and Provenance](/concepts/evidence-and-provenance.md)
