# Architecture Decision Record: be-git-remote

## 1. Decision Status

- **Status:** Proposed
- **Date:** 2026-10-27
- **OpenSpec Change ID:** `be-git-remote`
- **Decision owners:** Nikhil Vijayakumar
- **Related artifacts:** `proposal.md`, `design.md`, `specs/`

## 2. Decision Checkpoint

- [x] **New decision required:** how the remote is read, which provider labels exist, and that unknown hosts stay visible as `other`.
- [ ] **Existing decision applies**
- [ ] **No new ADR required**

### Rationale

The durable decision is the standalone concept `knowledge/decisions/git-remote-provider-labels.md`. It builds on the existing remote identity normalization decision and records the owner's choice of 2026-10-27 to keep unknown hosts as `other`.

## 3. Context and Problem

See the concept's Context.

## 4. Decision Drivers

No credentials stored; nothing run; self-hosted hosts stay visible.

## 5. Considered Options

See the concept's Alternatives considered.

## 6. Decision

See the concept's Decision.

## 7. Consequences

See the concept's Consequences.
