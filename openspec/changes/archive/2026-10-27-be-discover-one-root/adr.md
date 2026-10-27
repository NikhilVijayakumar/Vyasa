# Architecture Decision Record: be-discover-one-root

## 1. Decision Status

- **Status:** Proposed
- **Date:** 2026-10-27
- **OpenSpec Change ID:** `be-discover-one-root`
- **Decision owners:** Nikhil Vijayakumar
- **Related artifacts:** `proposal.md`, `design.md`, `specs/`

## 2. Decision Checkpoint

- [x] **New decision required:** how a repository is recognized without running Git, how kinds are told apart, and when a run is partial.
- [ ] **Existing decision applies**
- [ ] **No new ADR required**

### Rationale

The durable decision is the standalone concept `knowledge/decisions/repository-recognition-and-run-status.md`. The closed outcome set and the run record fields are already settled in the workspace-discovery grill log (Q9, Q10); the concept adds recognition rules and the partial-status rule.

## 3. Context and Problem

See the concept's Context.

## 4. Decision Drivers

Nothing is run; unassessed areas are never reported as scanned; submodules and worktrees are not mistaken for projects.

## 5. Considered Options

See the concept's Alternatives considered.

## 6. Decision

See the concept's Decision.

## 7. Consequences

See the concept's Consequences.
