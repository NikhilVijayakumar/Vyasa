---
type: Product
title: "Scope and Roadmap: Scope Principles and Roadmap"
description: Why delivery is phased and the principles that bound scope.
tags: [product, roadmap, phases]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /product/scope-and-roadmap.md
    title: Scope and Roadmap
---

# Scope and Roadmap: Scope Principles and Roadmap

*Sections 1–3 of [Scope and Roadmap](/product/scope-and-roadmap.md).*

## 1. Purpose

This document describes the scope and sequencing of Vyasa.

Vyasa will be developed in three phases:

1. **Phase 1 — Local Workspace Intelligence:** Discover local projects, extract metadata deterministically, maintain a SQLite index, and expose project information through MCP.
2. **Phase 2 — Shared Project Registry:** Synchronize approved project metadata through Google Sheets to provide cross-device visibility.
3. **Phase 3 — Remote Repository Discovery:** Discover and inspect GitHub and Bitbucket repositories through their APIs without cloning or checking them out.

Each phase must deliver independently useful functionality while preserving the architecture needed for subsequent phases.

## 2. Scope Principles

All implementation decisions must follow these principles.

### 2.1 Incremental Delivery

Implement and validate local discovery before adding external synchronization or remote repository providers.

Later phases must not be required for Phase 1 to work.

### 2.2 Deterministic Metadata

Routine scanning and metadata extraction must use defined rules and recognized repository evidence. LLM-based interpretation is outside the scope of the indexing pipeline.

If a fact cannot be established from an available source, report it as unknown or not documented.

### 2.3 Project-Owned Knowledge

Vyasa indexes project information but does not become the authoring authority for project-specific documentation.

A generated initial draft profile may be supported, subject to explicit draft and canonical-profile rules. Vyasa must not overwrite human-maintained project metadata.

### 2.4 Local and Shared Data Separation

Local filesystem paths, workspace configuration, machine-specific state, credentials, and secrets must remain outside the shared registry.

Only explicitly approved fields may be synchronized.

### 2.5 Non-Destructive Behaviour

Scanning, synchronization, and remote discovery must not modify repository source files or automatically delete, archive, or declare projects obsolete.

Potential duplicates, incomplete records, and obsolete-project candidates are reported for human review.

### 2.6 Provider Independence

The core project model must not depend on Google Sheets, GitHub, or Bitbucket-specific data structures.

Provider-specific adapters translate between external systems and the shared domain model.

## 3. Overall Roadmap

| Phase | Focus | Primary outcome |
|---|---|---|
| Phase 1 | Local scanner, SQLite, MCP | Queryable local project portfolio |
| Phase 2 | Google Sheets registry and synchronization | Shared project visibility across devices |
| Phase 3 | GitHub and Bitbucket APIs | Discovery of remote repositories without cloning |

The roadmap is capability-based rather than tied to calendar dates. A phase advances only when its acceptance criteria, maintained with the requirements, are satisfied.

---

# 4. Phase 1 — Local Workspace Intelligence
