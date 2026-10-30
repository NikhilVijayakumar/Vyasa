# Read-only CLI queries

The CLI exposes the existing indexed query services without starting MCP or scanning:

- `vyasa query version` reports the installed backend version.
- `vyasa query status` returns index status and freshness.
- `vyasa query search --query NAME --technology KEY --limit 50 --cursor CURSOR` searches the index; all options are optional.
- `vyasa query project PROJECT_ID`, `dependencies PROJECT_ID`, `context PROJECT_ID`, and `report PROJECT_ID` read the corresponding indexed data.

Query output is JSON. Indexed success results use the existing schema_version, data and meta envelope. Errors return an error object and nonzero exit code. The index is opened read-only and must already exist; queries never scan or create it. Repository-origin content is untrusted. `VYASA_HOME` selects the data directory when explicitly set; otherwise the standalone bundle uses its sibling data directory.
