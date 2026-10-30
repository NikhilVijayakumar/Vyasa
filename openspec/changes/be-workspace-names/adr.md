# ADR

Workspace names are local user-managed metadata, independent of the TOML settings that define scan roots. This preserves configuration comments and allows naming before an index exists; the root remains the stable local association and names cannot widen the scan scope. The metadata directory must be backed up with the installation's data.
