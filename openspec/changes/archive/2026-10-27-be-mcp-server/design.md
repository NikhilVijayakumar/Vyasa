# Design: be-mcp-server

## 1. Overview

### Purpose
Put a thin, safe MCP front on the query layer.

### Scope
Server construction, three tools, error mapping, entry points, packaging, tests.

### Design Principles
No logic in the adapter beyond translation. Open per call, close per call. Structured errors. The SDK stays behind one package.

## 2. Context and Constraints

### Current State
`vyasa.application.query` provides the behavior; `index_path()` locates the index.

### Constraints
- Technical: Python 3.12+; `mcp>=2,<3` (`MCPServer`, in-memory `Client`).
- Security and privacy: stdio only; no path input or output; stdout protocol only.
- Compatibility: core must import without `mcp`.

### Existing Decisions and Conventions
Stdio-only transport; paths omitted by default; optional extras; explicit tools disabled by default.

### Knowledge References
- `knowledge/architecture/mcp-interface.md`
- `knowledge/decisions/stdio-only-mcp-transport.md`
- `knowledge/decisions/optional-extras-for-integrations.md`

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| stdio and tool list | `build_server`, `main`, `__main__` | Subprocess stdio smoke test |
| Structured, read-only results | `_run` wrapper | In-process client tests; file-bytes check |
| Failures are structured | `_run` error mapping | Error-code tests |
| No paths cross the boundary | schemas, no `include_paths` | Schema and result scans |
| Contract pinned | snapshot file | Snapshot test |
| SDK optional | lazy import in the adapter only | Import test with `mcp` blocked |

## 4. Architecture and Design

### Architectural Approach
`_run(index_file, fn, **kwargs)` opens `open_index(index_file, read_only=True)`, calls the query function, closes the connection, and returns a `CallToolResult` with the envelope as `structured_content` plus a text copy. `IndexStoreError` maps to an error result with its code; any other exception logs to standard error and returns `INTERNAL_ERROR`. A missing file is checked first so a read-only open cannot create it. The three tool functions are defined inside `build_server` so the index file is a closure value, and tests build servers over temporary indexes.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `vyasa.adapters.mcp.server` | `build_server`, `main` | `mcp`, query layer |
| `vyasa.adapters.mcp.__main__` | `python -m` entry | server |
| `pyproject.toml` | extra and script | none |

### Interfaces and Contracts
See `api-contract.md`.

### Key Workflows
Client call → SDK validation → `_run` → query → envelope → result.

## 5. Data and State Management

No state; each call is independent.

## 6. Error Handling and Resilience

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| Missing index | `INDEX_UNAVAILABLE`, no file created | Build the index |
| Query layer error | Mapped to its code | Client corrects input |
| Unexpected exception | `INTERNAL_ERROR`, detail to stderr | Report |
| SDK missing | Hint on stderr, exit 2 | Install the extra |

## 7. Security and Privacy

Contract §5. Server `instructions` state that results are data from untrusted repositories.

## 8. Quality Attributes

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Safety | Read-only | Read-only connection per call | Bytes unchanged |
| Stability | Pinned contract | Snapshot | Snapshot test |
| Isolation | Core free of the SDK | Lazy, adapter-only import | Blocked-import test |

## 9. Testing and Verification Strategy

### Behavioral Verification
One test per scenario.

### Test Strategy
In-process `Client(build_server(...))` for behavior; one real subprocess over stdio; a snapshot file; a blocked-import test. The MCP tests skip with a reported reason when `mcp` is absent.

### Testability
The server takes the index file as an argument.

### Verification Evidence
`pytest` with and without the extra; a manual stdio exchange.

## 10. Implementation and Migration Considerations

### Implementation Order
Packaging, server with status tool, search and project tools, errors, snapshot, smoke test.

### Migration and Rollout
Install `vyasa[mcp]`; point the client at `vyasa-mcp`.

### Documentation and Operations
README note on running the server.

## 11. Architecture Decision Checkpoint

- **New ADR required:** No — the stdio-only and optional-extra decisions apply; see `adr.md`.
