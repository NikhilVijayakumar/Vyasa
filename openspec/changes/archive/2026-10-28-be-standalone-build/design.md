# Design: be-standalone-build

## 1. Overview

### Purpose
One install folder holds both executables and the data they share.

### Scope
A parameter on `data_directory()` and a rewrite of the build script's output stage.

### Design Principles
No behavior change outside frozen builds. Never touch user data on rebuild. Pure functions with injectable inputs.

## 2. Context and Constraints

### Current State
`data_directory()` returns `VYASA_HOME` or a platform folder. `build_mcp.py` builds only the MCP executable.

### Constraints
- Technical: standard library; PyInstaller is the optional `build` extra; per-OS builds.
- Security and privacy: `data/` stays local; no path reaches an MCP response.

### Existing Decisions and Conventions
Configuration location decision; single-writer index lifecycle; paths omitted from MCP.

### Knowledge References
- `knowledge/decisions/configuration-file-format-and-location.md`
- `knowledge/decisions/index-lifecycle-and-single-writer.md`

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| Locate the configuration file | `frozen_executable` parameter, default from `sys.frozen`/`sys.executable` | Unit tests for each branch |
| Both executables are built into one root | `build_one()` called twice | Real build in the verification step |
| A rebuild preserves the data | replace only the two bundle folders; seed config if absent | Test with a fake bundle and existing data |
| The output root comes from the environment | existing `--out`/env/.env order | Test: no source exits 2 |

## 4. Architecture and Design

### Architectural Approach
`data_directory(..., frozen_executable=None)`: when `VYASA_HOME` is unset and the running process is frozen, return `Path(executable).parent.parent / "data"`. The default for the parameter is `sys.executable` if `getattr(sys, "frozen", False)`, else none. The build script gains `build_one(name, entry, ...)` (the current PyInstaller call, parameterised), a `install(root, bundles)` step that replaces only the two bundle folders and creates `data/` with a seeded config, and `main()` that calls them. Filesystem work stays in `install()` so a test can pass a fake bundle.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `workspace.data_directory` | resolve the data directory | none |
| `scripts/build_mcp.py` | build, place, seed | PyInstaller |

### Interfaces and Contracts
See `api-contract.md`.

### Data Model and Storage
Unchanged.

### Error Handling and Failure Modes
Failed build of either bundle aborts before anything under `<root>` is replaced: both are built in a temp directory first, then moved.

### Security, Privacy, and Compliance
The frozen rule runs only when `sys.frozen` is set by the bundler. A hostile environment cannot make a source run read `data/`.

### Observability and Operations
The build prints both executable paths and the data folder.

## 5. Testing and Verification Strategy

| Layer | What it checks |
|---|---|
| Unit | `data_directory` for frozen, override, and source cases; `install()` preserves data and seeds once |
| Manual end to end | real build, `vyasa scan`, then `vyasa-mcp` lists projects, on this Windows machine |

## 6. Alternatives and Trade-offs

One executable with a `mcp` subcommand: fewer files but changes the client command and the MCP entry. Per-user data only: simplest but not portable or shareable.

## 7. Risks and Open Questions

Two bundles duplicate shared libraries (size). Accepted; revisit if size matters.

## 8. Rollout and Migration

Rebuild; update the MCP client command path once; copy existing data into `data/` if wanted.

## 9. Readiness Review

- [x] Design traces to the specifications.
- [x] Failure modes and verification are stated.
