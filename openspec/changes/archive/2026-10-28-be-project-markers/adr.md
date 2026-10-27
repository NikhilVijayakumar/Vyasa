# Architecture Decision Record: be-project-markers

## 1. Decision Status

- **Status:** Proposed
- **Date:** 2026-10-27
- **OpenSpec Change ID:** `be-project-markers`
- **Decision owners:** Nikhil Vijayakumar
- **Related artifacts:** `proposal.md`, `design.md`, `specs/`

## 2. Decision Checkpoint

- [x] **New decision required:** markers are presence-only, reported in three states, with capped repository-relative evidence.
- [ ] **Existing decision applies**
- [ ] **No new ADR required**

### Rationale

The durable decision is the standalone concept `knowledge/decisions/project-marker-observations.md`, so it reads correctly after this change is archived. The owner chose the scope, test rules, evidence paths, filter, per-marker locations, and not-assessed handling on 2026-10-27. The checkout walk observation and partial-results decisions apply unchanged.

## 3. Context and Problem

See the concept's Context.

## 4. Decision Drivers

Names answer the question cheaply; absence must not be inferred from a partial or missing assessment; no file content is read; the tool signature must not grow per detector.

## 5. Considered Options

See the concept's Alternatives considered: file reading, count-only, uncapped paths, any depth, older observations as not detected, one boolean per marker.

## 6. Decision

See the concept's Decision.

## 7. Consequences

See the concept's Consequences.
