# Interface and Data Contract: be-mcp-server

- **OpenSpec Change ID:** `be-mcp-server`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the MCP tools, their inputs and outputs, the error shape, the entry points, and the packaging.

## 2. Scope

In: `vyasa.adapters.mcp`, `pyproject.toml`. Out: Sheets and provider calls (not affected); resources, prompts, other transports.

## 3. Interface Surface

Transport: stdio only. Server name `vyasa`. Every tool is annotated read-only and idempotent, closed-world.

| Tool | Access | Input | Success output | Errors |
|---|---|---|---|---|
| `search_projects` | Reads the index | `query` (string, 1 to 200), `state`, `provider`, `identity_status` (each a string or list of strings; allowed values in the description), `limit` (integer 1 to 100, default 20), `cursor` (string) | structured content: envelope with `data.projects` and `data.page` | `INVALID_INPUT`, `INVALID_CURSOR`, `INDEX_UNAVAILABLE` |
| `get_project` | Reads the index | `project_id` (string) | structured content: envelope with the project record | `INVALID_INPUT`, `PROJECT_NOT_FOUND`, `INDEX_UNAVAILABLE` |
| `get_index_status` | Reads the index | none | structured content: envelope with status | `INDEX_UNAVAILABLE` |

Record shapes are those of `be-project-query-basics`. Success results also carry a JSON text copy of the structured content.

Entry points: `python -m vyasa.adapters.mcp`; console script `vyasa-mcp = vyasa.adapters.mcp.server:main`. The index file is `index_path()` (so `VYASA_HOME` applies).

Packaging: `[project.optional-dependencies] mcp = ["mcp>=2,<3"]`.

## 4. Error Model

| Condition | Error code | Response shape | Safe to show the user |
|---|---|---|---|
| Bad value, range, or unknown filter value | `INVALID_INPUT` | `is_error` result; `{"error": {"code", "message"}}` | Yes |
| Cursor not issued by the server | `INVALID_CURSOR` | same | Yes |
| Unknown project | `PROJECT_NOT_FOUND` | same | Yes |
| Index file missing or unreadable | `INDEX_UNAVAILABLE` | same; message omits the full path | Yes |
| Argument of the wrong JSON type | none | SDK tool error with text only | Yes |
| Unexpected exception | `INTERNAL_ERROR` | same shape; message is generic; details to standard error | Yes |

## 5. Trust Boundary

Tool input comes from an agent and is untrusted: validated by the SDK for types and by the query layer for values; bound as SQL parameters. No input names a path, and the server never takes a path from a tool. The index file is chosen only by local configuration. Result text is repository-derived and must be treated as data by the client; the server description says so. Standard output carries protocol only.

Machine-local data: the index and everything in it. Nothing is synchronized.

## 6. Data Model

None. Reads through the query layer.

## 7. Migration and Compatibility

New surface; the tool snapshot (`tests/snapshots/mcp_tools.json`) pins it. A change to the snapshot needs a note in the change that makes it.

## 8. Traceability

| Requirement | Operation |
|---|---|
| The server speaks stdio and lists its tools | server, entry points |
| Tools return structured, read-only results | the three tools |
| Failures are structured results | error mapping |
| No paths cross the boundary | schemas and results |
| The tool contract is pinned | snapshot |
| The SDK is an optional extra | packaging, `main` |

## 9. Open Contract Questions

- [ ] Whether to map SDK argument-type errors to `INVALID_INPUT`.
