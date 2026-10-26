---
type: Concept
title: "Glossary"
description: Definitions of the terms Vyasa documents use, in one place.
tags: [glossary, terms]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: dm
    resource: /architecture/data-model.md
    title: Data Model
  - id: scan
    resource: /architecture/scanning-and-evidence.md
    title: Scanning and Evidence
---

# How to use

Each term has one meaning across the bundle. Where a term has its own concept, follow the link.

| Term | Meaning |
|---|---|
| Alias | An additional identity (a renamed remote, a provider id) that resolves to an existing project or repository. See [Project Identity](/concepts/project-identity.md). |
| Allowlist | The explicit list of fields permitted to leave the machine. A field not on it is never exported. |
| Candidate | A directory found under a workspace root that might be a project; it ends with one outcome such as eligible, excluded, or inaccessible. |
| Canonical profile | The project-maintained file that declares facts a scanner cannot detect. Vyasa reads it and does not write it. |
| Checkout | A repository's working copy on one device. A repository can have several. |
| Conflict | Two sources give incompatible values for a field and the ownership rules do not decide. The field status is `conflicting`. |
| Declared value | A value stated by an authoritative source such as the canonical profile. |
| Derived value | A value computed by a deterministic rule from owned or observed inputs. See [Field Ownership](/concepts/field-ownership.md). |
| Detector | A versioned, deterministic function that turns recognized files into observations. See [Deterministic Extraction](/concepts/deterministic-extraction.md). |
| Draft profile | A generated, opt-in starting point for a canonical profile. Never authoritative. |
| Evidence | The source, location, and fingerprint that explain an observation. See [Evidence and Provenance](/concepts/evidence-and-provenance.md). |
| Freshness | How recently the index was successfully refreshed; distinct from the status of one observation. See [Freshness and Staleness](/concepts/freshness-and-staleness.md). |
| Index | The local SQLite database of projects, observations, evidence, and run history. Everything a query reads. |
| Logical project | The project as a concept, independent of its name, path, or hosting. |
| Machine-local data | Information that belongs to one device, such as clone paths and workspace roots. Never exported. |
| Observation | One value for one field from one source, with a status and evidence. |
| Observation status | `observed`, `declared`, `not_detected`, `unknown`, `unsupported`, `inaccessible`, `stale`, or `conflicting`. |
| Owner | The party whose value for a field is authoritative: the repository, a scan, a portfolio maintainer, a provider, the device, or a rule. |
| Portfolio field | A field managed by a person in the shared registry, such as tracking level. |
| Provider | An external repository host such as GitHub or Bitbucket Cloud. |
| Provisional identity | An identity built from weak evidence, flagged until stronger evidence appears. |
| Registry | The shared Google Sheets workbook holding approved project summaries and portfolio fields. |
| Remote-only project | A project known from a provider or the registry with no checkout on this device. |
| Repository | A Git repository, identified by its remote or by a local fallback. |
| Scan run | One discovery or refresh operation, with a status and counts. |
| Unknown | The available evidence cannot establish a value. Different from `not_detected`, which means a complete inspection found nothing. |
| Workspace root | A configured directory under which projects are discovered. |
