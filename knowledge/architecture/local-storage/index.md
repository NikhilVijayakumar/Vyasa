# Local Storage — parts

Parts of [Local Storage](/architecture/local-storage.md).

* [Storage Principles and Database Location](principles-and-location.md) - Storage principles and responsibilities, and where and how the database is created.
* [Logical Storage Model](logical-model.md) - The logical groups of stored data and how they relate.
* [Proposed Tables: Core](tables-core.md) - Tables for migrations, projects, repositories, associations, checkouts, observations, and evidence.
* [Proposed Tables: Relationships, Runs, and Inventory](tables-operations.md) - Tables for relationships, scan runs and results, detector runs, file inventory, and the resolved index.
* [Data Types, SQLite Configuration, and Transactions](types-config-transactions.md) - Serialization, journal mode and pragmas, connection use, and transaction boundaries.
* [Incremental State, Identity, and Local-Only Data](incremental-identity-sharing.md) - What incremental scanning stores, deduplication, and the line between local and shareable data.
* [Phase 2 and 3 Storage and Retention](phase-tables-retention.md) - Registry and remote provider state, and retention and cleanup.
* [Backup, Migrations, and Query Performance](backup-migrations-performance.md) - Consistent backup and recovery, schema migrations, and indexing for queries.
* [Concurrency, Diagnostics, Testing, and Acceptance](operations-testing-acceptance.md) - Locking and concurrent operation, logging, test strategy, sequence, decisions, and acceptance.
