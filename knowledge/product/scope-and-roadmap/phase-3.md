---
type: Product
title: "Scope and Roadmap: Phase 3: Remote Repository Discovery"
description: What phase 3 includes, excludes, and delivers.
tags: [product, roadmap, phases]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /product/scope-and-roadmap.md
    title: Scope and Roadmap
---

# Scope and Roadmap: Phase 3: Remote Repository Discovery

*Sections 6.1–6.4 of [Scope and Roadmap](/product/scope-and-roadmap.md).*

## 6.1 Objective

Extend Vyasa to discover repositories on GitHub and Bitbucket using their APIs, without cloning or checking out repositories merely to enumerate them or inspect supported metadata.

## 6.2 In Scope

### A. GitHub discovery

- Enumerate repositories available through configured public or authenticated access.
- Support pagination.
- Retrieve repository metadata.
- Inspect supported files through API access where permissions allow.
- Respect API rate limits and report access failures.

### B. Bitbucket discovery

- Enumerate accessible Bitbucket Cloud repositories.
- Support authenticated access to private repositories using appropriately scoped credentials.
- Retrieve repository metadata and inspect supported files through APIs.
- Handle pagination, permission failures, and rate limits.

Bitbucket support initially targets Bitbucket Cloud. Other Bitbucket deployment types require separate validation and scope approval.

### C. Unified repository model

- Map remote records into the shared project and repository model.
- Match remote repositories to existing local or registered projects.
- Distinguish a project from its individual repositories.
- Handle multiple repositories belonging to one logical project.
- Flag uncertain matches and potential duplicates for human review.

### D. Remote metadata

Where supported by the provider and available permissions, extract:

- Repository name and URL.
- Description when explicitly provided.
- Default branch and repository status.
- Supported languages and technologies when evidence can be obtained.
- README and selected documentation metadata.
- Recognized manifests, instruction files, and project configuration.

Metadata unavailable through the provider API must remain unknown rather than being inferred.

### E. Authentication and reliability

- Store credentials outside the repository registry.
- Use the minimum permissions practical for discovery.
- Handle token expiration and authorization failures.
- Respect API rate limits.
- Record discovery timestamps and outcomes.
- Make failures distinguishable from empty results.

## 6.3 Out of Scope

Phase 3 will not include:

- Automatic repository cloning or checkout.
- Pushing commits or modifying remote repository content.
- Automatic deletion or archival.
- Unrestricted source-code crawling.
- Full semantic code search across remote repositories.
- Support for every Git hosting platform in the initial implementation.
- Treating a failed API request as proof that a repository no longer exists.

## 6.4 Phase 3 Deliverables

1. GitHub provider adapter.
2. Bitbucket Cloud provider adapter.
3. Remote repository discovery workflow.
4. Remote file inspection for supported metadata.
5. Cross-source identity and matching logic.
6. Credential and permission documentation.
7. API rate-limit and error-recovery behaviour.
8. Automated provider and integration tests.
9. Documentation for configuring remote discovery.

---

# 7. Cross-Phase Requirements

The following requirements apply throughout the roadmap.
