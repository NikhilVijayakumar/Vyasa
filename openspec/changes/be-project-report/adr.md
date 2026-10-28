# Architecture Decision Record: be-project-report

## 1. Decision Status

- **Status:** Proposed
- **Date:** 2026-10-28
- **OpenSpec Change ID:** `be-project-report`
- **Decision owners:** Nikhil Vijayakumar
- **Related artifacts:** `proposal.md`, `design.md`, `specs/`

## 2. Decision Checkpoint

- [x] **New decision required:** `knowledge/decisions/project-report-in-the-repository.md`
- [ ] **Existing decision applies**
- [ ] **No new ADR required**

### Rationale

Storing a large, agent-written, untrusted text in the index is a lasting choice that bounds what Vyasa holds and how agents use it.

## 3. Context and Problem

See the decision's Context.

## 4. Decision Drivers

No model calls in Vyasa; query from another repository; bounded untrusted text; no drift between template and reader.

## 5. Considered Options

Raise profile limits; serve only a path and hash; Vyasa writes the report with a model; free-form report. See the decision's alternatives.

## 6. Decision

A fixed-section markdown report beside the profile, read by the scan and stored by section as a bounded copy, served from the index as declared data. The template is served over MCP.

## 7. Consequences

The index grows by at most 256 KiB per checkout. Stored text can be stale or wrong and is labelled declared. A staleness check is a later change.
