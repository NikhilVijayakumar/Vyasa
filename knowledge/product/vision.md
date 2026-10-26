---
type: Product
title: "Product Vision"
description: Why Vyasa exists, who it serves, its principles, success criteria, and non-goals.
tags: [product, vision, principles]
status: draft
generated: { by: human:nikhil-vijayakumar, at: 2026-10-26T00:00:00Z }
---

# Vyasa (व्यास) — Product Vision

## 1. Vision

Vyasa is a local-first workspace intelligence system that helps developers and AI coding agents understand, discover, and connect information across multiple software projects.

It provides a unified, searchable view of projects distributed across local workspaces and remote repositories. By extracting verifiable information from repository metadata, configuration files, and documentation, Vyasa makes project knowledge accessible without requiring developers or AI agents to open and inspect every project individually.

**Vision statement:**

> Enable developers and AI coding agents to discover, understand, and reuse knowledge across an entire ecosystem of software projects through a reliable, deterministic, and privacy-conscious interface.

## 2. Problem Statement

Developers often maintain many independent repositories across different domains, technologies, and stages of development. Each repository may have its own documentation, architecture, conventions, tools, and implementation history.

Although individual projects may be well organized, knowledge across the overall project portfolio is fragmented.

Common challenges include:

- **Fragmented project knowledge:** Understanding the purpose, technologies, structure, and status of another project requires opening its repository and examining its files.
- **Expensive context switching:** Developers must repeatedly reconstruct project context when moving between projects.
- **Limited cross-project discovery:** Finding existing implementations, reusable components, shared libraries, or similar projects is difficult when information is scattered across repositories.
- **Incomplete portfolio visibility:** It is difficult to maintain an overview of project documentation, engineering practices, technologies, and lifecycle status.
- **AI agent context limitations:** Coding agents generally work within the context of the current repository and may not know what useful information exists elsewhere.
- **Distributed development environments:** Project repositories may be available on different devices or hosted across different Git platforms, making a single local index insufficient for long-term portfolio visibility.

Vyasa addresses these challenges by providing a common intelligence layer across projects without requiring those projects to surrender ownership of their documentation or source code.

## 3. Target Users

### 3.1 Developers and Technical Leads

Developers and technical leads use Vyasa to:

- Search projects by name, technology, framework, or documented capability.
- Retrieve a concise, evidence-backed summary of a project.
- Discover related projects and potentially reusable implementations.
- Understand the documentation and engineering setup of other repositories.
- Maintain visibility across a growing collection of projects.

### 3.2 AI Coding Agents

AI coding agents such as OpenCode and Claude Code can access Vyasa through the Model Context Protocol (MCP).

Agents can use Vyasa to:

- Discover relevant projects before proposing or implementing a solution.
- Retrieve project metadata and documented context.
- Identify related repositories and existing dependencies.
- Locate the relevant repository for deeper inspection.
- Avoid unnecessary reinvention when a suitable implementation may already exist.

Vyasa provides discovery and context. The agent remains responsible for inspecting source code, evaluating suitability, and making changes through the target repository's normal development workflow.

### 3.3 Project and Portfolio Maintainers

People responsible for multiple projects can use Vyasa to:

- Maintain a consolidated project registry.
- Identify projects with missing or incomplete documentation.
- Review project metadata and lifecycle information.
- Discover potential duplicates or projects that may need attention.
- Share project-level metadata across development devices.

## 4. Product Objectives

Vyasa aims to achieve the following objectives.

### 4.1 Unified Project Discovery

Provide a consistent way to discover projects across configured local workspaces and, in later phases, remote repository platforms.

### 4.2 Reliable Project Context

Expose useful project information extracted from repository evidence, including:

- Project identity and repository location.
- Programming languages, frameworks, and technologies.
- README and documentation structure.
- Recognized agent instruction files.
- OpenSpec configuration and other explicitly supported engineering conventions.
- Test-related files and configuration.
- Human-maintained project status and other explicitly documented metadata.

### 4.3 Cross-Project Knowledge Reuse

Help developers and coding agents locate potentially relevant projects, libraries, dependencies, and implementations before creating new solutions.

### 4.4 Cross-Device Project Visibility

Establish a shared project registry through Google Sheets so projects can remain discoverable across devices, even when their repositories have not been cloned locally.

### 4.5 Remote Repository Discovery

Enable future discovery of GitHub and Bitbucket repositories through their APIs, without requiring repository clones or checkouts merely to discover project metadata.

### 4.6 Maintainable Project Portfolio

Make it easier to identify missing metadata, documentation gaps, stale information, duplicate candidates, and projects that may require human review.

## 5. Product Principles

### 5.1 Deterministic by Default

Vyasa derives information from defined rules and recognized sources such as repository metadata, manifests, configuration files, and documentation.

It does not require an LLM to scan repositories, extract supported facts, or answer metadata queries.

When information is unavailable, Vyasa reports it as `unknown`, `not documented`, or an equivalent explicit state rather than inventing an answer.

### 5.2 Evidence-Based Results

Detected facts should be traceable to their source wherever practical. Results should distinguish between:

- **Detected:** Directly established from repository files or configuration.
- **Declared:** Explicitly provided by a project maintainer in project metadata or documentation.
- **Unknown:** Not established by an available source.
- **Stale or unavailable:** Previously known information that may no longer reflect the current state, or information that could not be checked.

File presence must not automatically be treated as proof of validity, completeness, or quality.

### 5.3 Project-Owned Knowledge

Each repository remains responsible for its project-specific knowledge and documentation.

Vyasa indexes and exposes that information; it does not become a competing authoring system or silently overwrite maintained project details.

If a project profile is missing, Vyasa may support generating an initial draft for a maintainer to complete. Draft-generation and canonical-profile rules must be defined separately, and machine-generated drafts must not overwrite maintained information.

### 5.4 Local-First and Privacy-Conscious

The initial implementation should operate locally without requiring cloud services.

Local paths, machine-specific configuration, credentials, and other sensitive operational details remain local unless an explicitly designed and authorized operation requires otherwise.

Only an approved set of project metadata may be shared through the future registry.

### 5.5 Read-Only Project Access

Vyasa primarily provides read-only discovery and retrieval.

It may update its own generated index, scan history, and synchronization state. It must not silently modify project source code or maintained project documentation.

### 5.6 Modular and Extensible

The system should separate its core project model and domain rules from filesystem scanning, local persistence, MCP access, Google Sheets synchronization, and remote repository providers.

New repository platforms and metadata detectors should be addable without redesigning the entire system.

### 5.7 Human Oversight

Vyasa can identify candidates for review, but it should not automatically delete, archive, or declare projects obsolete. Such decisions remain with the project owner.

## 6. Product Scope and Evolution

Vyasa will evolve in three planned phases.

### Phase 1 — Local Workspace Intelligence

Build the foundational system with:

- Configurable workspace discovery.
- Git repository and project identification.
- Deterministic metadata extraction.
- A local SQLite index.
- Evidence-backed project search and retrieval.
- MCP tools for querying project information.
- Index freshness and scan status.
- Local-only storage for machine-specific information.

**Outcome:** An AI coding agent can query projects across configured local workspaces without manually opening each repository.

### Phase 2 — Shared Project Registry

Add Google Sheets as a shared cross-device project registry.

The registry will provide shared project metadata, support controlled synchronization, preserve human-maintained fields, and record scan and synchronization history.

The local SQLite index remains responsible for local indexing and machine-specific state.

**Outcome:** Projects remain visible across devices, including projects that are registered but not currently cloned locally.

### Phase 3 — Remote Repository Discovery

Add GitHub and Bitbucket repository discovery through their APIs.

The system will support remote enumeration and metadata inspection without cloning or checking out repositories solely for discovery. Access will follow the user's permissions and configured authentication.

**Outcome:** Vyasa can extend project discovery beyond local workspaces and provide a broader view of the project portfolio.

## 7. Success Criteria

Vyasa will be considered successful when:

1. Developers can discover and query projects across configured workspaces from a single interface.
2. Coding agents can retrieve useful project context through MCP.
3. Returned metadata is reproducible and supported by identifiable evidence.
4. Missing information is represented honestly instead of inferred without evidence.
5. Refreshing the index does not overwrite project-owned knowledge.
6. The local implementation works without external services.
7. Shared registry synchronization supports cross-device visibility without leaking local paths or secrets.
8. Remote discovery can be added without coupling provider-specific logic to the core project model.
9. Potentially obsolete or duplicate projects can be surfaced for review without destructive automation.

## 8. Non-Goals

Vyasa is not intended to:

- Replace Git, GitHub, Bitbucket, or existing project documentation.
- Replace an IDE, source-code search engine, or full code-analysis platform.
- Automatically rewrite project documentation or source code.
- Require an LLM to generate or interpret metadata during routine indexing.
- Guarantee that a project is reusable merely because its metadata appears similar to another project.
- Automatically delete, archive, or mark projects obsolete without human review.
- Store repository credentials, local clone paths, or machine-specific configuration in the shared registry.
- Become a general-purpose project management or task tracking system.

## 9. Long-Term Direction

The long-term direction is to make Vyasa a dependable knowledge and discovery layer for a portfolio of software projects.

A developer or AI coding agent should be able to ask questions such as:

- Which projects use Python and have OpenSpec configured?
- Do I already have a library that solves this problem?
- Which projects contain a particular framework or dependency?
- Which projects have no README or recognizable test configuration?
- What documented information is available about a project I have not cloned on this device?
- Which projects have incomplete metadata or may need a maintainer's attention?

Vyasa should answer such questions using available, traceable evidence and clearly communicate what it cannot establish.

The intended result is not an autonomous system that guesses what every project means. It is a reliable system that makes existing project knowledge easier to find, verify, and reuse.

## 10. Guiding Statement

**Vyasa makes project knowledge discoverable without taking ownership away from the projects themselves.**

It connects repositories, local indexes, shared metadata, and AI coding agents through a consistent, deterministic, and privacy-conscious system.
