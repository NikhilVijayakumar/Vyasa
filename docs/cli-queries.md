# Read-only CLI queries

The CLI exposes the existing indexed query services without starting MCP or scanning:

- `vyasa query version` reports the installed backend version.
- `vyasa query status` returns index status and freshness.
- `vyasa query search --query NAME --technology KEY --limit 50 --cursor CURSOR` searches the index; all options are optional.
- `vyasa query project PROJECT_ID`, `dependencies PROJECT_ID`, `context PROJECT_ID`, and `report PROJECT_ID` read the corresponding indexed data.

Query output is JSON. Indexed success results use the existing schema_version, data and meta envelope. Errors return an error object and nonzero exit code. The index is opened read-only and must already exist; queries never scan or create it. Repository-origin content is untrusted. `VYASA_HOME` selects the data directory when explicitly set; otherwise the standalone bundle uses its sibling data directory.

## Workspace selection

`vyasa query workspaces` lists configured roots and their accessibility without creating an index. `vyasa query search --workspace ROOT` filters before pagination. `vyasa scan --workspace ROOT` scans one configured root; omit the option to scan all configured roots. An unconfigured root is rejected. Workspace paths are local data. Project-level scans and editable workspace names are not yet supported.

`vyasa query technologies` lists the versioned detector registry without opening the index. These are supported filters, not a claim that any project uses them.

`vyasa workspace set-name --root ROOT --name NAME` assigns local human-managed display metadata to a configured root. Workspace listings include nullable `name`; configuration and index are unchanged. Back up `data/workspace-names/` with the rest of the installation data.
