# Proposal: Read-only desktop CLI queries

## Why

The installed CLI exposes scanning and live profile context but not the indexed project search and details required by the desktop. The existing backend query services already supply read-only indexed results.

## What Changes

Expose a versioned, machine-readable CLI interface to existing index status, project search, project details, dependencies, profile context and project report queries. Missing or corrupt indexes must return a structured error without creating or modifying data.

## Scope and constraints

Phase 1; affects the CLI adapter and its tests, not scanners, SQLite schema, MCP contracts, registry or providers. Reuse existing query semantics and redaction. No shell execution, implicit scan, absolute path disclosure or database migrations.

## Risks and dependencies

CLI outputs are a public interface consumed by the desktop and must retain the query envelope, bounded inputs and explicit errors. The installed executable must be rebuilt after backend tests.

## Acceptance

The CLI emits parseable JSON for supported queries, distinguishes missing index and invalid input, and leaves index data unchanged.

## Traceability

- Change: be-desktop-cli-query; branch: feature/be-desktop-cli-query.
- Requirement package: docs/requirements/project-query/requirement.md and docs/requirements/local-index/requirement.md.
- Knowledge: knowledge/concepts/evidence-and-provenance.md, knowledge/concepts/explicit-operations.md and knowledge/architecture/mcp-interface.md.
- Existing specifications: project-query, local-index, mcp-server.
