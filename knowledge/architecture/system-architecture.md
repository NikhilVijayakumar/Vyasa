---
type: Architecture
title: "Vyasa (व्यास) — System Architecture"
description: Layers, components, runtime model, and technology choices of the Vyasa MCP server.
tags: [architecture, components, python, mcp]
status: draft
generated: { by: human:nikhil-vijayakumar, at: 2026-10-26T00:00:00Z }
---
# Vyasa (व्यास) — System Architecture

**Product:** Vyasa — Workspace Intelligence MCP  
**Architecture style:** Modular, local-first, protocol-oriented  
**Primary language:** Python  
**Initial storage:** SQLite  
**Agent interface:** Model Context Protocol (MCP)

## Summary

This document defines the logical architecture of Vyasa, including its components, responsibilities, dependencies, data flows, and extension points.

## Parts

This concept is split into parts so each can be read on its own. Section numbers in the table are those of the original document, so references such as "§9.11" resolve to the part that contains them.

| Part | Sections | What it answers |
|---|---|---|
| [Context and Vision](system-architecture/context-and-vision.md) | §1–3 | Why Vyasa exists architecturally, its guiding principles, and the external systems it touches. |
| [Architectural Layers](system-architecture/layers.md) | §4 | The domain, application, adapter, and entry-point layers and what each may depend on. |
| [Component Responsibilities](system-architecture/components.md) | §5 | What each component owns: configuration, discovery, inspection, detectors, identity, normalization, index, persistence, query, MCP, Sheets, providers. |
| [Dependency Direction and Package Structure](system-architecture/structure.md) | §6–7 | The allowed dependency direction and the proposed Python package layout. |
| [Core Domain Model](system-architecture/domain-model.md) | §8 | Logical project, repository, checkout, observation, evidence, and relationship as architectural building blocks. |
| [Scan, Query, MCP, and Storage Data Flows](system-architecture/data-flows.md) | §9–12 | How data moves through a scan, an incremental scan, a query, an MCP call, and storage. |
| [Phase 2 and 3 Integrations and Security Architecture](system-architecture/phase-integrations.md) | §13–15 | How Google Sheets and provider adapters attach to the core and where the security boundaries sit. |
| [Error Handling, Testing, and Technology Choices](system-architecture/operations.md) | §16–18 | Error and observability architecture, the testing architecture, and the technology baseline. |
| [Decisions, Evolution, and Acceptance](system-architecture/decisions-and-evolution.md) | §19–22 | Mandatory constraints, undecided items, how the architecture grows by phase, and its acceptance criteria. |
