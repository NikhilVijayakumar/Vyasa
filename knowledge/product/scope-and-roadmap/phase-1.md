---
type: Product
title: "Scope and Roadmap: Phase 1: Local Workspace Intelligence"
description: What phase 1 includes, excludes, and delivers.
tags: [product, roadmap, phases]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /product/scope-and-roadmap.md
    title: Scope and Roadmap
---

# Scope and Roadmap: Phase 1: Local Workspace Intelligence

*Sections 4.1–4.4 of [Scope and Roadmap](/product/scope-and-roadmap.md).*

## 4.1 Objective

Build a deterministic local service that discovers projects across configured workspace roots, extracts supported metadata, indexes the results in SQLite, and exposes them through MCP.

The system must operate without Google Sheets, GitHub API access, Bitbucket API access, or an LLM.

## 4.2 In Scope

### A. Workspace discovery

- Configure one or more local workspace roots.
- Discover candidate project directories and Git repositories.
- Support configurable directory exclusions.
- Avoid repeatedly scanning excluded or irrelevant directories.
- Handle inaccessible paths and malformed repositories without terminating the entire scan.
- Distinguish a logical project from an individual repository where the available evidence supports that distinction.

### B. Project identity

- Generate stable project identifiers.
- Prefer normalized repository identity when a usable Git remote is available.
- Provide a deterministic local fallback identity for repositories without remotes.
- Avoid treating a filesystem rename as a new project when identity evidence remains unchanged.
- Detect potential duplicates and ambiguous identity mappings for review.

Identity resolution rules must be documented before implementation is considered complete.

### C. Deterministic metadata extraction

Extract supported facts from recognized repository evidence, including:

- Project name.
- Explicitly documented project purpose, when available.
- Git remote and repository URL.
- Programming languages.
- Frameworks and technologies supported by recognized manifests and configuration files.
- README presence and location.
- Documentation presence and recognizable structure.
- OpenSpec presence, configuration validity, and meaningful specification or change files.
- Recognized agent instruction files.
- Test-related files and configuration.
- Project-maintained status and other declared fields, when available.

The initial detector set must be documented and tested against representative repository fixtures.

OKF means Google Cloud's [Open Knowledge Format](/technologies/okf.md); its detector rules are in [Scanning and Evidence §9.11](/architecture/scanning-and-evidence.md).

### D. Local index

- Store project records and extracted metadata in SQLite.
- Store machine-specific paths and local repository mappings locally.
- Track scan timestamps, freshness, and outcomes.
- Maintain evidence references for extracted facts.
- Support incremental rescanning where practical.
- Handle schema migrations.
- Recover from interrupted or failed scans without corrupting previously valid records.

### E. MCP interface

Provide read-oriented MCP tools for:

- `search_projects`
- `get_project`
- `get_project_context`
- `find_related_projects`
- `get_project_dependencies`
- `get_index_status`

The final tool contracts, parameter schemas, response structures, and error behaviour will be defined in [mcp-interface](/architecture/mcp-interface.md).

An optional refresh operation may trigger a deterministic rescan and update the generated index. It must not be used to edit maintained project metadata.

### F. Project profile lifecycle

Define how Vyasa handles repositories without a canonical project profile.

The initial design must distinguish:

- Detected repository metadata.
- Human-declared project information.
- Generated draft information.
- Local indexing and scan state.

If a generated profile draft is implemented, it must follow the agreed git-ignored draft policy. Any committed canonical profile must remain project-owned and must not be silently replaced by the scanner.

### G. Quality and verification

- Unit tests for identity and extraction rules.
- Fixture-based scanner tests.
- SQLite persistence and migration tests.
- MCP contract tests.
- Error-handling and exclusion tests.
- End-to-end tests using temporary workspace directories.
- Documentation for local setup and MCP client configuration.

## 4.3 Out of Scope

Phase 1 will not include:

- Google Sheets integration.
- GitHub or Bitbucket API-based repository enumeration.
- Remote repository scanning without a local checkout.
- Cloud-hosted databases or mandatory cloud services.
- LLM-based project summarization, classification, or relationship inference.
- Automatic source-code modification or canonical profile maintenance.
- Automatic deletion, archival, or lifecycle changes.
- A dedicated graphical dashboard unless separately approved.
- Full semantic code search or indexing of every source-code symbol.

## 4.4 Phase 1 Deliverables

1. Python package and application entry point.
2. Configuration model and workspace discovery.
3. Project identity and metadata extraction modules.
4. Local SQLite schema and migration mechanism.
5. Deterministic scanner and index-refresh workflow.
6. MCP server and documented tool contracts.
7. Automated test suite.
8. Installation and configuration guide.
9. Example configuration and representative test fixtures.
10. Documented limitations and unsupported detection patterns.

---

# 5. Phase 2 — Shared Project Registry
