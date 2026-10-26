---
type: Architecture
title: "Remote Repository Discovery: Remote Identity and Reconciliation With Local Data"
description: Matching remote repositories to projects, and reconciling remote with local observations.
tags: [github, bitbucket, phase-3]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/remote-repositories.md
    title: Remote Repository Discovery
---

# Remote Repository Discovery: Remote Identity and Reconciliation With Local Data

*Sections 11–12 of [Remote Repository Discovery](/architecture/remote-repositories.md).*

## 11. Remote Identity and Logical Project Resolution

### 11.1 Separate Entities

The data model must distinguish:

- Logical project.
- Remote repository.
- Local checkout.
- Provider identity.
- Shared registry record.

A remote repository may be known even when it has no local checkout and no confirmed logical project association.

### 11.2 Matching Existing Projects

The identity resolver may use:

- Stable provider repository ID.
- Canonical remote identity.
- Existing repository-to-project associations.
- Explicit canonical project profile references.
- Approved repository identity mappings.

Names and descriptions may help produce candidates, but must not independently establish identity.

### 11.3 One Project, Multiple Repositories

A logical project may consist of multiple remote repositories.

For example, a project may maintain separate frontend and backend repositories.

Vyasa should support multiple repository associations without forcing them into one repository record.

### 11.4 Forks and Mirrors

Forks and mirrors must remain separate repository identities.

They may be associated through a distinct relationship such as `fork_of` or `mirror_of` if that relationship type is added to the data model.

A fork must not automatically replace the upstream repository associated with a logical project.

### 11.5 Duplicate Candidates

When multiple remote repositories appear to represent the same logical project, Vyasa may create a `potential_duplicate` candidate.

The candidate must include the evidence and deterministic rule that produced it.

The system must not merge records or delete a repository automatically.

### 11.6 Identity Conflicts

If a repository appears to match multiple logical projects, the resolver must preserve the ambiguity.

The MCP interface should expose the conflict or review status rather than arbitrarily selecting one project.

---

## 12. Reconciliation With Local Observations

### 12.1 Independent Observation Sources

Remote and local observations are separate records.

For example:

- Local README: observed at local working-tree state.
- Remote README: observed at a specific remote commit.
- Shared registry README status: last synchronized summary.

These are not interchangeable.

### 12.2 Resolution Rules

The field ownership policy determines which observation supplies the resolved value.

A newer remote observation must not automatically overwrite a local working-tree observation, and a local observation must not automatically overwrite a shared human-managed field.

### 12.3 Conflicts

A conflict may arise when:

- The local profile differs from the remote profile.
- The local working tree differs from the remote branch.
- The remote repository identity conflicts with an existing association.
- The shared registry contains a human-managed value that disagrees with repository metadata.

The resolution service must preserve the observations and apply field-specific ownership rules.

### 12.4 Remote-Only Projects

If a repository is discovered remotely and no local checkout exists:

- Store the remote repository record.
- Associate it with a logical project if identity is unambiguous.
- Extract supported metadata when inspection is enabled.
- Make it searchable through the MCP interface.
- Mark local checkout state according to what was actually verified.
- Avoid inventing a local path.

### 12.5 Local-Only Projects

A local repository may have no accessible remote repository or may not be hosted on a supported provider.

It remains a valid local project and must not be deleted from the index simply because remote discovery does not find it.
