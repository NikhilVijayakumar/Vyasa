---
name: backend-documentation-correctness
description: >-
  Keeps backend OpenSpec, API examples, README, environment, Docker, Makefile,
  and Postman documentation accurate against implemented behavior. Use before
  backend implementation (document-first) and when changes affect contracts,
  commands, configuration, models, security, or operational behavior; do not
  apply it to frontend documentation.
metadata:
  scope: backend
---

# Backend Documentation Correctness

Backend documentation is part of the contract. Write or update the applicable OpenSpec artifacts before changing implementation behavior, then reconcile durable documentation against the result.

## Document first

1. Read the target `FUN-*` requirements, current as-built baseline, coverage matrix, related changes, and `backend/README.md`.
2. Create or update the applicable proposal, observable specs, design, ADR decision, and actionable tasks before implementation begins, following the configured OpenSpec schema.
3. Keep the target product requirement separate from the current implementation status. Mark partial behavior and unresolved stakeholder decisions explicitly.
4. If implementation reveals a missing requirement or design decision, update the approved artifacts before continuing.

## Correctness checks

- Compare GraphQL operation names, inputs, outputs, nullability, permission codes, validation rules, and error behavior against resolvers, DTOs, services, and specs.
- Check all documented ports, container hostnames, service names, Make targets, and environment variable names/defaults against `docker-compose.yml`, `Makefile`, `.env.example`, and code.
- Never copy real `.env` values, passwords, tokens, recipient data, or local personal data into tracked documentation or Postman examples.
- Ensure migrations, seed commands, required extensions, persistence rules, and data ownership are described accurately.
- Update Postman request examples when a GraphQL contract changes; distinguish authored scripts/assertions from runs that actually executed.
- Check links, headings, filenames, relative paths, and whether referenced files exist. Avoid linking to generated or ignored local-only assets as though they are committed.
- Preserve known gaps from source CSVs and stakeholder questions; do not turn names or ambiguous labels into stable identifiers in prose.
- Do not duplicate reference documentation. Update the authoritative source and link to it.

## Closeout

Reconcile the as-built baseline, implementation coverage, README, agent instructions, Postman artifacts, and change tasks that the implementation made stale. Report checks as passed, failed, skipped, unavailable, or unverified. Gherkin is not an executable test unless a runner and step definitions are configured.

## Output

List the documents updated and the source evidence checked. Call out contradictions or missing inputs rather than silently inventing values.
