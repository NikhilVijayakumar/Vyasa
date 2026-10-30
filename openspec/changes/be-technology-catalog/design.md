# Design

Read the existing `default_registry` through its public application service and serialize only its public descriptive fields. No duplication of registry entries, no changes to persisted data. Search uses the existing technology filter key. The desktop consumes the catalog through an allowlisted IPC channel and shows backend errors explicitly.
