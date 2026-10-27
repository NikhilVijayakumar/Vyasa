# Architecture Decision Record: be-identity-create-and-rescan

## 1. Decision Status

- **Status:** Proposed
- **Date:** 2026-10-27
- **OpenSpec Change ID:** `be-identity-create-and-rescan`
- **Decision owners:** Nikhil Vijayakumar
- **Related artifacts:** `proposal.md`, `design.md`, `specs/`

## 2. Decision Checkpoint

- [ ] **New decision required**
- [x] **Existing decision applies:** `knowledge/decisions/stored-identity-with-aliases.md`
- [ ] **No new ADR required**

### Rationale

The existing decision already fixes creation once, aliases, the lookup order, and identity events. This change implements it and adds one rule the decision lacked, recorded there: conflicting evidence changes nothing and is recorded as an event. It also records the interim fallback: until root-commit identity exists, a repository without a remote is provisional and matched by path.

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
