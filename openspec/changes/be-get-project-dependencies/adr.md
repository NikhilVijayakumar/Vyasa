# Architecture Decision Record: be-get-project-dependencies

## 1. Decision Status

- **Status:** Proposed
- **Date:** 2026-10-28
- **OpenSpec Change ID:** `be-get-project-dependencies`
- **Decision owners:** Nikhil Vijayakumar
- **Related artifacts:** `proposal.md`, `design.md`, `specs/`

## 2. Decision Checkpoint

- [x] **New decision required:** a dependency is internal only by exact normalized name against a package another indexed project declares in the same ecosystem; ambiguity is listed; coverage is always stated.
- [ ] **Existing decision applies**
- [ ] **No new ADR required**

### Rationale

The durable decision is the standalone concept `knowledge/decisions/internal-dependencies-by-declared-package-name.md`, so it reads correctly after this change is archived. It applies the requirement decision Q6 and keeps the framework-detection and partial-results decisions unchanged.

## 3. Context and Problem

See the concept's Context.

## 4. Decision Drivers

No invented edges; honest coverage; reuse of stored evidence; no new dependency or file read.

## 5. Considered Options

See the concept's Alternatives considered: remote or path matching, cross-ecosystem matching, picking one of several, lockfiles, display names.

## 6. Decision

See the concept's Decision.

## 7. Consequences

See the concept's Consequences.
