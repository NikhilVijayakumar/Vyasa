---
type: Architecture
title: "MCP Interface: Later Phases and Client Configuration"
description: How Sheets and remote operations attach later, and how MCP clients launch the server.
tags: [mcp, interface, contracts]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/mcp-interface.md
    title: MCP Interface
---

# MCP Interface: Later Phases and Client Configuration

*Sections 17–19 of [MCP Interface](/architecture/mcp-interface.md).*

## 17. Phase 2 — Google Sheets Integration

Google Sheets adds a shared registry; it does not replace the local index or become the authoritative source for repository file evidence.

### 17.1 Query Behaviour

The existing tools should continue working against the unified project query model.

Where a project is known to the shared registry but is not present on the current machine, Vyasa may return shared metadata with explicit provenance.

For example:

- Project identity may be known from the shared registry.
- Local checkout status may be `not_present` or `unknown`, depending on whether the local workspace has been fully checked.
- Documentation presence may reflect the last recorded scan, not a fresh local inspection.

### 17.2 Synchronization

Synchronization should be implemented as a separate application capability with explicit scope and error handling.

If a sync MCP tool is later introduced, it should be named explicitly, such as `sync_shared_registry`, and must document its write effects, conflict behaviour, and field ownership rules.

It must not be hidden inside `search_projects` or `get_project`.

### 17.3 Source Provenance

Each shared value should indicate that it came from the shared registry.

The interface must distinguish human-maintained portfolio fields from scanner-generated metadata and must not silently overwrite human-managed fields.

### 17.4 Cross-Device Identity

A project discovered from Sheets may have no local checkout on the current machine.

The MCP interface must still support querying the shared record without inventing a local path or claiming that local files were inspected.

---

## 18. Phase 3 — Remote Repository Discovery

### 18.1 Remote Discovery

Remote repository discovery should be exposed through a separate capability, for example `discover_remote_repositories`, if an MCP tool is warranted.

It must not be an implicit side effect of ordinary queries.

### 18.2 Remote Inspection

A future tool may expose remote repository metadata or evidence-backed remote context. The final tool name and schema should be defined when Phase 3 requirements are finalized.

Remote evidence must identify:

- Provider.
- Repository identity.
- Relevant revision, where available.
- Repository-relative path.
- Observation time.
- Authentication or access limitations, where safe to report.

### 18.3 No-Clone Behaviour

Remote tools must use provider APIs rather than requiring repository clones.

A remote API failure must not be presented as proof that a repository or file does not exist.

### 18.4 Authentication and Access

The MCP client must not receive provider credentials as part of ordinary tool responses.

Access should be determined by the configured provider connection and its permissions.

The implementation must not promise private-repository visibility unless the configured credentials have sufficient access.

---

## 19. MCP Client Configuration

Vyasa should provide documented configuration examples for supported clients after testing their current configuration formats.

The examples must specify:

- Command or executable used to launch Vyasa.
- Arguments and working directory requirements.
- Required environment variables, if any.
- How local configuration and credentials are supplied.
- How to disable operational tools such as `refresh_index`.
- How to verify that the server is connected.

Client configuration examples must not contain real credentials or assume that all MCP clients use the same configuration syntax.

The Python package should provide a documented launch entry point so clients do not need to know internal module paths.
