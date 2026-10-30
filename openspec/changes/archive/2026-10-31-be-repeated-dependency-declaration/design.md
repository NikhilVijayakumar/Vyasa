# Design: be-repeated-dependency-declaration

## 1. Overview

### Purpose

Make dependency storage honor the primary key `checkout_dependencies` already declares, so a manifest that repeats a dependency in one scope is indexed instead of aborting the scan.

### Scope

`projects._store_frameworks` in `src/vyasa/adapters/sqlite/projects.py`, the function that writes one manifest row and its dependency rows for an observation. Parsers, caps, scopes, technology mapping, and every read path are out of scope.

### Design Principles

- One row per name and scope, as migration 0009 declares; the writer respects the key rather than discovering it through an exception.
- Fix the single place that writes these rows; do not teach four parsers a rule that exists for storage-shape reasons.
- Keep constraint failures meaningful: only the known repeat is collapsed, everything else still raises.
- Deterministic output: the kept row is the first declaration in parsed order.

## 2. Context and Constraints

### Current State

`framework-detection` parses the supported root manifests and returns every declared dependency with its constraint and scope, sorted by `(name, scope)`. `detect_frameworks` caps the list at 200 per manifest. `projects._store_frameworks` writes the manifest row to `checkout_manifests` and then inserts each dependency into `checkout_dependencies`, whose primary key is `(observation_id, path, name, scope)` and whose `scope` carries a CHECK constraint. `technologies_of` derives technologies from the same dependency list before the cap, so the repeat is already harmless there.

### Constraints

- **Technical:** standard library only, no schema change, no new module.
- **Security and privacy:** reads nothing new; no file text beyond name, constraint, and scope.
- **Performance and reliability:** a repeat must not cost a second query or a retry; deduplication is in memory over an already capped list.
- **Compatibility and migration:** schema version stays 11; existing indexes remain valid; no data-ownership change.
- **Operational:** an index left `partial` by an interrupted scan recovers with one successful scan.

### Existing Decisions and Conventions

- `knowledge/decisions/framework-detection-from-manifests.md` — scopes are never merged, dependencies are bounded per manifest.
- `knowledge/decisions/index-lifecycle-and-single-writer.md` — the scan is the only writer; a failed run must report failure rather than leave partial state silently.
- `knowledge/decisions/local-first-sqlite-index.md` — the index is the single local store.

### Knowledge References

- `knowledge/decisions/framework-detection-from-manifests.md` — how dependencies are scoped and bounded, and why repeats collapse to one row.
- `knowledge/decisions/index-lifecycle-and-single-writer.md` — writer responsibility and run status.
- `knowledge/practices/vertical-slices.md` — the slice shape used in `tasks.md`.

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| REQ-001, scenario "Declared twice in one scope" | Deduplicating insert in `_store_frameworks` | Persistence test on a real database file |
| REQ-002, scenario "Same name in two scopes" | Key is `(name, scope)`, not `name` | Persistence test with two scopes |
| REQ-003, scenario "Repeat does not disturb other manifests" | Deduplication is per manifest, before `executemany` | Existing store tests plus the new one |
| Scenario "A real violation still fails" | No `INSERT OR IGNORE`; the CHECK stays enforced | Constraint test on the same table |

## 4. Architecture and Design

### Architectural Approach

The invariant belongs to the index repository, so the fix lives in the repository adapter at the insert. The domain keeps returning what the manifest declares, scopes intact, which is what the specification requires; the adapter reduces that to the rows the table can hold.

```
manifest parse (domain) -> FrameworkReport -> _store_frameworks (sqlite adapter) -> checkout_dependencies
                                                |
                                                +-- unique by (name, scope), first wins
```

### Components and Responsibilities

| Component | Responsibility | Dependencies |
|---|---|---|
| `domain.manifests` | Parse a manifest into dependencies with constraint and scope | unchanged |
| `application.scanning.frameworks` | Cap dependencies, map technologies | unchanged |
| `adapters.sqlite.projects._store_frameworks` | Write manifest, dependency, technology, nested rows | `checkout_dependencies` primary key |

### Interfaces and Contracts

Internal function only; no MCP, CLI, or schema surface changes. The contract is the one in `api-contract.md` §6: one row per `(observation_id, path, name, scope)`.

### Alternatives Considered

- **Add `constraint_text` to the primary key (migration).** Rejected: the key deliberately models one dependency per name and scope; two constraints for one name and scope are not both meaningful to the read paths, and a migration buys nothing for a storage-shape fix.
- **`INSERT OR IGNORE`.** Rejected: it would also swallow CHECK and foreign-key violations, turning real defects into silent data loss.
- **Deduplicate in the domain parser layer (`_bounded`).** Rejected as the primary fix: it puts a storage-shape rule in the parser and would change what the domain reports; the store is the only consumer that cannot represent repeats.
- **Report the repeat as `skipped`.** Rejected: `skipped` means an unsupported dependency kind, and inflating it would misstate the manifest.

### Error Handling and Failure Modes

- A repeat is collapsed before the insert, so no exception path is involved.
- Any other constraint violation still propagates out of the transaction, as today, and the scan reports failure rather than a silent omission.
- The deduplication is local to one manifest's list; a manifest that fails cannot remove rows from another.

### Data Flow and Storage

Read path unchanged: `projects.checkout_frameworks` selects rows by `observation_id` and `path` ordered by `name, scope`. Because the stored set is unique per name and scope, the read returns the same shape it did for manifests without repeats.

## 5. Security, Performance, and Quality

- **Security:** nothing new is read; manifest text stays untrusted data; no path or credential enters the row.
- **Performance:** one dictionary pass over at most 200 items per manifest; no extra query.
- **Quality:** deterministic first-wins order; the CHECK and foreign keys stay enforced.
- **Accessibility, platform:** not applicable.

## 6. Migration and Rollout

No migration. Order of work: write the failing persistence test, apply the store change, run the suite, rebuild the standalone executable, then scan real roots. Rollback is a revert of the one function change.

## 7. Risks and Trade-offs

| Risk | Impact | Mitigation |
|---|---|---|
| A differing constraint in the repeat is not stored | An agent sees one of two declared constraints | First declaration wins deterministically; the index models one constraint per name and scope |
| Future writers bypass the deduplication | The same crash returns from a new call site | The regression test covers the store entry point; the key remains the last line of defense |

## 8. Open Questions

- [ ] Whether `total_dependencies` should report distinct names rather than declared entries. Deferred: no consumer depends on the difference and the specification keeps the declared-entry total.

## 9. Review Checklist

- [x] The design addresses every in-scope requirement.
- [x] Component boundaries and responsibilities are clear.
- [x] Interfaces and data flows are described.
- [x] Failure handling is explicit.
- [x] Security, performance, and data integrity are considered in proportion to the change.
- [x] Alternatives and trade-offs are recorded.
- [x] Knowledge concepts the design builds on are cited.

**Status:** Ready for tasks
