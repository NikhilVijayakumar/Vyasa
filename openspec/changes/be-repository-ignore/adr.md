# Architecture Decision Record: be-repository-ignore

## 1. Decision Status

- **Status:** Proposed
- **Date:** 2026-10-27
- **OpenSpec Change ID:** `be-repository-ignore`
- **Decision owners:** Nikhil Vijayakumar
- **Related artifacts:** `proposal.md`, `design.md`, `specs/`

## 2. Decision Checkpoint

- [x] **New decision required:** a repository-provided, bounded, narrow-only ignore file.
- [ ] **Existing decision applies**
- [ ] **No new ADR required**

### Rationale

The durable decision is the standalone concept `knowledge/decisions/repository-ignore-file.md`. The owner chose a dedicated `.vyasaignore` over honoring `.gitignore` on 2026-10-27, and that the repository, not Vyasa, decides what to ignore.

## 3. Context and Problem

See the concept's Context.

## 4. Decision Drivers

Vyasa cannot know what to ignore; the file is untrusted; simple rules a person can read.

## 5. Considered Options

See the concept's Alternatives considered.

## 6. Decision

See the concept's Decision.

## 7. Consequences

See the concept's Consequences.
