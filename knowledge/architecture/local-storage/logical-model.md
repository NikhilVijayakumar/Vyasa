---
type: Architecture
title: "Local Storage: Logical Storage Model"
description: The logical groups of stored data and how they relate.
tags: [sqlite, storage, index]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/local-storage.md
    title: Local Storage
---

# Local Storage: Logical Storage Model

*Sections 5 of [Local Storage](/architecture/local-storage.md).*

## 5. Logical Storage Model

The database should separate stable entities from observations and operational records.

```mermaid id="dbmodel"
erDiagram
    PROJECT ||--o{ PROJECT_REPOSITORY : groups
    REPOSITORY ||--o{ PROJECT_REPOSITORY : belongs_to
    REPOSITORY ||--o{ LOCAL_CHECKOUT : checked_out_as
    PROJECT ||--o{ METADATA_OBSERVATION : has
    REPOSITORY ||--o{ METADATA_OBSERVATION : has
    LOCAL_CHECKOUT ||--o{ SCAN_ITEM_RESULT : inspected_in
    SCAN_RUN ||--o{ SCAN_ITEM_RESULT : contains
    METADATA_OBSERVATION ||--o{ EVIDENCE_REFERENCE : supported_by
    PROJECT ||--o{ PROJECT_RELATIONSHIP : source_or_target
    REPOSITORY ||--o{ FILE_INVENTORY_ITEM : contains
    SCAN_RUN ||--o{ FILE_INVENTORY_ITEM : observes

    PROJECT {
        string project_id PK
        string display_name
        string identity_status
        string lifecycle_status
        string details_status
    }

    REPOSITORY {
        string repository_id PK
        string repository_type
        string remote_identity
        string provider_type
    }

    PROJECT_REPOSITORY {
        string project_id FK
        string repository_id FK
        string association_type
    }

    LOCAL_CHECKOUT {
        string checkout_id PK
        string repository_id FK
        string local_path
        string workspace_root
    }

    METADATA_OBSERVATION {
        string observation_id PK
        string entity_type
        string entity_id
        string field_key
        string status
        string source_type
    }

    EVIDENCE_REFERENCE {
        string evidence_id PK
        string observation_id FK
        string source_ref
        string revision
    }

    PROJECT_RELATIONSHIP {
        string relationship_id PK
        string source_project_id
        string target_project_id
        string relationship_type
        string status
    }

    SCAN_RUN {
        string run_id PK
        string status
        datetime started_at
        datetime completed_at
    }

    SCAN_ITEM_RESULT {
        string result_id PK
        string run_id FK
        string entity_id
        string status
    }

    FILE_INVENTORY_ITEM {
        string inventory_id PK
        string repository_id FK
        string relative_path
        string fingerprint
    }
```

This diagram is conceptual. The physical schema may use composite keys or additional association tables where appropriate.

### 5.1 Core Storage Groups

| Group | Purpose |
|---|---|
| Identity and entities | Projects, repositories, local checkouts |
| Observations | Declared and detected metadata |
| Evidence | Source references supporting observations |
| Relationships | Dependencies and related-project links |
| Scanning | Runs, item results, detector outcomes |
| File inventory | Relevant files and fingerprints for incremental scanning |
| Resolved index | Efficiently queryable project summaries |
| Schema management | Migration version and storage compatibility |
| Future shared registry | Synchronization metadata in Phase 2 |
| Future remote discovery | Provider discovery and observation state in Phase 3 |
