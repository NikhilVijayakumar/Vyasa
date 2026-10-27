# Architecture Decision Record: be-profile-read

## 1. Decision Status

- **Status:** Proposed
- **Date:** 2026-10-27
- **OpenSpec Change ID:** `be-profile-read`
- **Decision owners:** Nikhil Vijayakumar
- **Related artifacts:** `proposal.md`, `design.md`, `specs/`

## 2. Decision Checkpoint

- [x] **New decision required:** the profile format changes from YAML to TOML, and an agent fills it once.
- [ ] **Existing decision applies**
- [ ] **No new ADR required**

### Rationale

The durable decision is the existing concept `knowledge/decisions/canonical-profile-and-draft.md`, updated here: TOML at `.vyasa/project-profile.toml` (no new dependency), per-field validation, and the file written by a coding agent or maintainer while Vyasa only reads it. Recorded on the owner's decision of 2026-10-27.

## 3. Context and Problem

See the concept's Context.

## 4. Decision Drivers

Renames must not duplicate; evidence must not be guessed; every mapping change must be auditable.

## 5. Considered Options

See the concept's Alternatives considered.

## 6. Decision

See the concept's Decision.

## 7. Consequences

See the concept's Consequences.
