---
type: Architecture
title: "Vyasa (व्यास): Data Classification, Filesystem, and Local Storage"
description: Classification and minimization, filesystem and repository boundaries, and local database security.
tags: [security, privacy, trust-boundary]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/security-and-privacy.md
    title: Vyasa (व्यास)
---

# Vyasa (व्यास): Data Classification, Filesystem, and Local Storage

*Sections 4–6 of [Vyasa (व्यास)](/architecture/security-and-privacy.md).*

## 4. Data classification and minimization

Vyasa must classify information before storing, returning, or synchronizing it.

### 4.1 Proposed classifications

| Classification | Examples | Handling |
|---|---|---|
| Public | Public repository URL, public project name | May be shared when required |
| Internal project metadata | Project purpose, technologies, documentation status | Local by default; approved fields may be synchronized |
| Sensitive operational metadata | Local paths, internal repository URLs, private project relationships | Local by default; explicit review before sharing |
| Secret | API tokens, OAuth refresh tokens, private keys, passwords | Never indexed as values, logged, or exported |
| Potentially sensitive repository content | Configuration files, internal documents, source code | Inspect only when needed; do not retain raw contents by default |

These categories are a proposed baseline. Organizations may need stricter classification rules.

### 4.3 Evidence minimization

Evidence should explain *why* a metadata value was reported without reproducing the underlying file.

An evidence record may contain:

- Repository-relative file path.
- Metadata field or detector identifier.
- Line range, where appropriate and safe.
- File fingerprint or relevant revision identifier.
- Observation timestamp.
- Detector version and result status.

It should not contain the complete matching line by default. A line from a configuration file can contain a password or token even when the filename itself appears harmless.

---

## 5. Filesystem and repository security

### 5.1 Workspace boundaries

Vyasa must operate only within explicitly configured workspace roots and approved remote scopes.

### 5.2 Read-only operation

- Do not edit, rename, delete, move, or reformat repository files.
- Do not modify Git configuration, branches, commits, remotes, hooks, or working-tree state.
- Do not run repository-provided scripts or execute project code.
- Do not initialize repositories or change their configuration.
- Do not write scanner output into a repository except through a separately approved, explicit operation.

### 5.3 Draft profile generation

If draft generation is implemented, it must be a separate, opt-in capability.

- Use the designated draft location, proposed as `.vyasa/project-profile.draft.yaml`.
- Do not overwrite an existing draft without explicit approval.
- Do not modify the canonical profile.
- Do not automatically promote a draft to authoritative metadata.
- Ensure the draft path is covered by the repository's ignore policy where appropriate.
- Explain that `.gitignore` prevents normal Git tracking but does not provide confidentiality or guarantee that the file cannot be committed.
- Avoid putting secrets or raw sensitive content into generated drafts.
- Report the intended write operation before execution and restrict it to the exact approved path.

The standard scanner and MCP query tools remain read-only with respect to repository content.

---

## 6. Local database and machine security

### 6.1 Storage location and permissions

SQLite must be stored in a dedicated application-data directory, not inside a scanned repository by default.

### 6.2 Encryption at rest

SQLite encryption is not assumed to be enabled by default. The initial deployment should rely on appropriately secured OS account permissions and, where available, operating-system or disk encryption.

A decision is required on whether application-level database encryption is necessary for the expected threat model. If introduced, use a maintained, reviewed implementation with a secure key-storage strategy. Do not design a custom encryption scheme.

Encryption at rest does not protect data from a process that can access both the database and its decryption key.

### 6.3 Retention and deletion

- Retain only observations, evidence, and history needed for the documented product functions.
- Define configurable retention for scan history, stale observations, and operational logs.
- Remove obsolete index records when a project is deliberately removed from the index, subject to the chosen retention policy.
- Ensure deletion or cleanup does not affect repository-owned files.
- Explain that deleting an index record does not delete the source repository or remove previously synchronized copies from Google Sheets.
- Provide an explicit process for removing shared registry entries and local caches when a project is retired.
