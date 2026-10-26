---
name: backend-prisma-postgresql-integrity-review
description: >-
  Reviews backend Prisma models, PostgreSQL migrations, repositories, transactions,
  and seed/import code for relational integrity, concurrency safety, and
  recoverability. Use only when a backend change alters persistence, migrations,
  data imports, identifiers, or multi-record invariants.
metadata:
  scope: backend
---

# Prisma and PostgreSQL Integrity Review

Inspect the Prisma schema, generated migration SQL, repository behavior, and existing data assumptions together. A valid Prisma schema alone does not prove database integrity.

## Schema and migration review

- Give each relation a clear owner, cardinality, foreign-key behavior, and deletion policy. Prefer explicit constraints over application-only assumptions for invariants the database can enforce.
- Check unique constraints against normalized business keys and source namespaces; confirm nullable uniqueness semantics match PostgreSQL behavior.
- Add indexes for demonstrated foreign-key, lookup, filter, and ordering paths. Avoid speculative indexes without workload evidence.
- Review check constraints, exclusion constraints, date-range boundaries, partial predicates, and extension requirements in the migration SQL.
- Confirm migrations are ordered, reproducible from an empty database, and safe for existing records. Flag destructive or locking changes and require an explicit migration/backfill plan.
- Keep Prisma naming/mapping consistent with the database and application model; never leak Prisma-generated types across infrastructure boundaries.

## Transactions and concurrency

- Identify invariants that can race: unique creation, single-use token consumption, role assignment, last-active-manager protection, overlapping effective dates, and status transitions.
- Ensure read-check-write sequences that enforce invariants are atomic or backed by database constraints. Consider concurrent transactions, isolation, retries, and idempotency.
- Keep transactions inside the repository adapter that owns the records; return domain outcomes rather than raw Prisma errors.
- Check update code distinguishes an omitted field from explicit `null` and cannot overwrite unrelated fields.

## Seeds and source imports

- Seeds should be repeatable and idempotent. Verify which fields are source-owned versus administrator-owned, and do not silently overwrite manual data.
- Validate CSV encodings, required headers, row numbers, populated-row constraints, normalization, and reference lookups before commit.
- Match source people using a confirmed stable identifier. In the current roster files, normalized email is used by the seed; names are not stable join keys for managers, owners, or responsible people.
- Do not infer a client, employee, tower lead, or cross-domain relation from ambiguous labels. Record unresolved mappings for stakeholder confirmation.
- Ensure a failed import rolls back as specified and reports enough context to repair source data without leaking personal data unnecessarily.

## Output

Report confirmed data-integrity defects with schema/migration/repository paths, the invariant at risk, and a concrete remediation. Distinguish schema-validation success from migration execution and data verification; state which checks were not run.
