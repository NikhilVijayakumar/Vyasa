# Architecture Decision Record: be-standalone-build

## 1. Decision Status

- **Status:** Proposed
- **Date:** 2026-10-28
- **OpenSpec Change ID:** `be-standalone-build`
- **Decision owners:** Nikhil Vijayakumar
- **Related artifacts:** `proposal.md`, `design.md`, `specs/`

## 2. Decision Checkpoint

- [ ] **New decision required**
- [x] **Existing decision applies:** `knowledge/decisions/configuration-file-format-and-location.md`
- [ ] **No new ADR required**

### Rationale

The decision's data-directory rule gains one step: a built executable uses the `data` folder beside its install. The decision file is updated at closeout rather than a new one added.

## 3. Context and Problem

An install must be self-contained and shareable by every process on the machine.

## 4. Decision Drivers

Shared data without environment setup; no behavior change for source runs; no data loss on rebuild.

## 5. Considered Options

Sibling `data/` for frozen builds (chosen); one executable with subcommands; per-user folder only.

## 6. Decision

Sibling `data/` for frozen executables, `VYASA_HOME` still overrides.

## 7. Consequences

Frozen runs ignore the per-user folder unless `VYASA_HOME` is set. Clients update the MCP path once.
