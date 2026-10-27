# Interface and Data Contract: be-review-candidates

- **OpenSpec Change ID:** `be-review-candidates`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the decision table, the candidate view, and the rule catalogue. No MCP tool, CLI command, or sync exchange is involved; decisions are never part of any sync.

## 2. Scope

In: migration `0004`, `vyasa.adapters.sqlite.review`, `vyasa.domain.index` (catalogue, errors). Out: MCP, CLI, Sheets, provider calls (not affected).

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `decide(connection, project_id, kind, status, note=None, *, now)` | Python function | Writes `review_decisions` only | an open flag's project and kind, status, optional note | none | `CANDIDATE_NOT_FOUND`, `INVALID_DECISION` |
| `list_candidates(connection, review=None)` | Python function | Read | optional review status filter | rows: project id, display name, kind, rule, confidence, criteria, evidence (JSON text), review status, note, decided time; ordered by project id then kind | none |

Rule catalogue (constant): `duplicate_checkout` is rule `same_remote_identity`, confidence `high`, criteria "More than one checkout of this project is active, and they share a remote identity."; `identity_unresolved` is rule `path_remote_conflict`, confidence `low`, criteria "A checkout's path belongs to this project, but its remote identity belongs to another."

## 4. Error Model

| Condition | Error code | Response shape | Safe to show the user |
|---|---|---|---|
| No open flag for project and kind | `CANDIDATE_NOT_FOUND` | `IndexStoreError(code, message)` | Yes |
| Status not allowed, or note over 500 characters | `INVALID_DECISION` | same | Yes |

## 5. Trust Boundary

The reviewer's input (status, note) is untrusted text: validated, bounded, and bound as parameters. Decisions are local, generated state and are never read by any export or synchronization. They are never written to a repository.

## 6. Data Model

`review_decisions`: `project_id` FK, `kind`, `status` (`open`, `dismissed`, `confirmed`), `evidence` TEXT (the flag evidence at decision time), `note` TEXT (at most 500 characters, nullable), `decided_at`; PRIMARY KEY (`project_id`, `kind`).

Candidate review status: the decision's status when a decision exists and its evidence parses equal to the flag's current evidence; otherwise `open`.

Invariants: `decide` writes only `review_decisions`; no row is deleted; a decision does not change a flag, project, checkout, or alias.

## 7. Migration and Compatibility

`0004_review_decisions.sql` creates the table, empty. Backup precedes (runner). Nothing existing changes.

## 8. Traceability

| Requirement | Operation / table |
|---|---|
| Candidates are explainable | `list_candidates`, catalogue |
| Decisions are stored locally | `decide`, `review_decisions` |
| A decision holds only for its evidence | evidence comparison |
| Nothing is changed automatically | write-set of `decide`; no lifecycle rule |
| Decisions are never shared | table is local; migration |

## 9. Open Contract Questions

- [ ] Where lifecycle comes from for obsolete candidates.
