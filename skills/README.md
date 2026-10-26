# Skill Catalog

Authoritative inventory of every skill in `skills/`, with its home category and
its role in the lifecycle. Categories follow `README.md`:

- **Core** — required for the shared lifecycle; every change may rely on them.
- **Conditional** — required when a change has the relevant impact (testing,
  architecture, behavioral specification, review).
- **Extension-specific** — required only for a selected technology or
  discipline (the consuming project's stack).
- **Optional** — a project may adopt or invoke them deliberately.

Use only skills present in this directory. A skill mentioned anywhere but absent
here does not exist in the repository.

## Layout

Every skill lives in exactly one category directory under `skills/`, and that
directory is the skill's home:

```
skills/
├── shared/      # lifecycle spine and cross-cutting quality — every team
├── frontend/    # frontend team
├── backend/     # backend team
└── qa/          # QA team
```

`skills/shared/` holds the skills the shared configuration may name, and the
skills every schema may name. The three team directories hold the skills
that belong to one team; the team's schema (`openspec/schemas/<team>/`) may
name them, and `openspec/config.yaml` maps each team to its schema and skill
home.

Agent directories (`.opencode/skills/`, `.agents/skills/`, `.claude/skills/`,
`.github/skills/`, `.codex/skills/`) stay **flat**: one directory link per
skill name, whatever its home. `scripts/sync_skills.py` creates and verifies
those links.

## `skills/shared/`

### Core

| Skill | Responsibility |
|---|---|
| `openspec-propose` | Propose a new OpenSpec change with generated artifacts |
| `openspec-apply-change` | Implement tasks from an approved OpenSpec change |
| `openspec-update-change` | Revise an existing change's planning artifacts coherently |
| `openspec-sync-specs` | Sync delta specs from a change into main specs |
| `openspec-archive-change` | Archive a completed change |
| `openspec-git-discipline` | Branch naming, change-ID traceability, review/verification gates |
| `git-flow-branch-creator` | Create feature/fix branches per the branching model |
| `git-commit` | Conventional commit analysis, staging, and message generation |
| `git-guardrails-claude-code` | Hooks blocking dangerous git commands in Claude Code |
| `neat-freak` | Reconcile documentation and knowledge with what was implemented (closeout) |

### Conditional

| Skill | Required when | Responsibility |
|---|---|---|
| `openspec-explore` | Thinking through an idea before/during a change | Socratic exploration and problem clarification |
| `grill-me` | Proposal or design needs assumptions challenged | Relentless interview to expose gaps and risks |
| `gherkin-authoring` | Writing or reviewing behavioral scenarios | Gherkin syntax and scenario best practice |
| `acceptance-test-authoring` | Specifications and tasks are approved | Turn scenarios into traceable acceptance checks |
| `spec-analysis` | Ingesting source documents for a change | Extract traceable requirements, conflicts, scope, gaps without inventing behaviour |
| `clarification-management` | Ambiguous or conflicting decisions surface | Maintain a prioritized clarification log |
| `test-driven-development` | Writing or changing production code | Red–Green–Refactor discipline |
| `test-strategy` | Planning verification; specs/tasks mention testing | Test layers and boundaries, coverage expectations, tooling decisions, requirement-ID traceability, server-boundary authorization and `errors[]` principles |
| `test-debugging` | Any automated check fails or flakes | Evidence-based diagnosis; product vs test vs environment vs flake |
| `code-reviewer` | Before considering a change complete | Correctness, regressions, security, scope, tests |
| `architecture-review` | Change affects architecture or interfaces | Component boundaries, data flow, quality attributes |
| `architectural-decision-records` | A durable architectural decision is (or isn't) introduced | Write/review ADRs; record explicitly when none is needed |
| `c4-diagrams` | Diagrams materially clarify boundaries or data flow | Produce C4 context/container/component diagrams |
| `tdd` | TDD detail is needed for a change | Reference detail — `test-driven-development` governs the practice |

### Optional

| Skill | Responsibility |
|---|---|
| `ponytail` | Minimal-solution discipline (YAGNI, ladder of simplicity) applied to code and design |

## `skills/frontend/`

Frontend team skills. Named by the `frontend` schema
(`openspec/schemas/frontend/`).

| Skill | Stack / discipline | Responsibility |
|---|---|---|
| `ui-ux-pro-max` | UI/UX design intelligence | Searchable design system: styles, palettes, typography pairings, UX rules, stack-specific UI guidance (see Precedence) |
| `huashu-design` | Design exploration / prototyping | Creative artifacts: HTML prototypes, slide decks, animations, mockups, visual directions (see Precedence) |
| `frontend-design` | Production SaaS UI | Restrained production interface design: hierarchy, states, spacing, copy, usability review (see Precedence) |
| `ui-design` | UI/UX practices (reference) | UI/UX, accessibility, responsive rules — reference; the design quad owns decisions |
| `web-design-guidelines` | UI review (reference) | Pinned Vercel Web Interface Guidelines checklist for reviewing UI code |
| `react-best-practices` | React/Next.js performance | Vercel's 70 performance rules: waterfalls, bundle size, data fetching, rerenders, rendering (authoritative — see Precedence) |
| `vercel-react-best-practices` | React performance (mirror) | Maintained mirror of the Vercel rule set — supplementary to `react-best-practices` |
| `vercel-composition-patterns` | React composition (reference) | React composition patterns — reference; `react-best-practices` owns performance |
| `react` | React 19 | React 19 patterns: concurrent rendering, Server Components, hook optimization |
| `react-hook-form` | React Hook Form | Form validation, field arrays, form performance |
| `react-testing` | React frontend | Component, hook, and form tests (Vitest + React Testing Library by default) |
| `tanstack-query` | TanStack Query v5 | Data fetching, caching, mutations, optimistic updates |
| `feature-arch` | Frontend architecture | Feature-based architecture and module organization |
| `msw` | MSW | API mocking at the network boundary for component tests |
| `zod` | Zod | Schema validation, type inference, error handling |
| `typescript` | TypeScript | Type safety, async patterns, compiler configuration |
| `playwright-testing` | Browser automation | End-to-end journeys, fixtures, storage-state auth, test data, suite maintenance |
| `playwright` | Playwright (reference) | E2E detail — reference; `playwright-testing` governs browser-automation practice |
| `vitest` | Vitest 5 (reference) | Vitest setup/mocking detail — reference; `react-testing` governs component-test practice |
| `accessibility-testing` | UI quality | Automated scans, keyboard navigation, focus management |
| `localization-accessibility-review` | UI or message scope changes | English/Spanish coverage and basic accessibility checks |
| `nextjs` | Next.js 16 — deferred | App Router, caching, routing — applies only if the project adopts Next.js |
| `nuqs` | URL query state — deferred | Type-safe URL query state — applies only if the project adopts Next.js + nuqs |
| `tailwind` | Tailwind CSS v4 — deferred | Utility CSS and theming — applies only if the project adopts Tailwind (stack undecided) |
| `shadcn` | shadcn/ui — deferred | Component library patterns — applies only if the project adopts shadcn/ui (stack undecided) |

## `skills/backend/`

Backend team skills. Named by the `backend` schema
(`openspec/schemas/backend/`).

| Skill | Stack / discipline | Responsibility |
|---|---|---|
| `graphql-testing` | GraphQL API / NestJS backend | Contract tests (`errors[]`, shapes), provider units, authorization at the server boundary |
| `api-contract-testing` | An API or schema changes | Contract checks from approved schemas; flag gaps, invent nothing |
| `database-integration-testing` | PostgreSQL persistence | Constraints, transactions, queries, migrations on a disposable database |
| `security-and-privacy-review` | Access, uploads, sessions, secrets, or sensitive data are affected | Authorized security/privacy review without claiming compliance |
| `nestjs-architecture-principles` | Designing or changing NestJS module boundaries, DI, layering, or services | Cohesive feature modules, dependency inversion, ports and adapters; calls out when CQRS or microservices are not justified |
| `nestjs-professional-software-engineering` | Implementing, refactoring, or debugging NestJS feature code | Idiomatic, version-aware NestJS/TypeScript engineering that preserves existing project conventions and public behavior |
| `nestjs-features-performance` | Choosing NestJS runtime primitives or diagnosing server performance | Middleware, guards, pipes, interceptors, filters, error mapping, caching, queues, scaling, observability |
| `graphql-schema` | Creating or changing GraphQL SDL — types, fields, nullability, pagination, errors | Apollo GraphQL schema design guidance; schema design only — execution testing stays with `graphql-testing` |
| `postgresql-best-practices` | Designing or changing relational schema, indexes, queries, transactions, or migrations | PostgreSQL engineering with reference material per topic; Azure-specific references apply only on Azure |

## `skills/qa/`

QA team skills. Named by the `qa` schema (`openspec/schemas/qa/`).

| Skill | Required when | Responsibility |
|---|---|---|
| `user-story-design` | Breaking requirements into deliverables | Small, traceable stories with testable acceptance criteria |
| `test-design` | Designing verification from requirements | Risk-aware test cases from approved requirements and criteria |
| `test-case-design` | Specs and acceptance criteria are approved | Complete, structured, traceable test cases |
| `test-data-design` | Tests need fixtures or import scenarios | Synthetic, consistent test data and import validation |
| `traceability-and-coverage` | Mapping verification to requirements | Requirement → story → test → evidence → defect maps; coverage gaps |
| `defect-reporting` | A defect is found | Reproducible, evidence-based reports with expected vs actual |
| `test-execution-review` | Reporting verification results | Honest execution summaries: passes, failures, blockers, not-run, evidence |
| `test-maintenance` | Suites age or flake | Reliability, flake reduction, coverage protection as the product evolves |

## Team routing

Proposals are typed by proposing team: change IDs carry the `fe-`, `be-`, or
`qa-` prefix (framework/process changes keep `openspec-`), and each team
selects its own schema when the change is created. The mapping between a team,
its schema, and its skill home lives in `openspec/config.yaml` (`teams:`).

| Team | Schema | Skill home | Team artifacts |
|---|---|---|---|
| `fe` | `frontend` | `skills/frontend/` | `ui-spec` — screens, states, interaction, accessibility, localization |
| `be` | `backend` | `skills/backend/` | `api-contract` — operations, payloads, errors, authorization, data model, migration |
| `qa` | `qa` | `skills/qa/` | `testplan` — layers, coverage matrix, test data, gates |
| framework | project default (`schema:` in `openspec/config.yaml`) | `skills/shared/` | — (shared spine; used for framework and process changes) |

Routing is a starting point, not a ceiling: the per-skill "Required when"
condition still decides for each individual change — a change outside a team's
usual focus applies whatever skills its actual impact triggers. Every team may
also use the `skills/shared/` skills.

## Precedence for overlapping skills

Several intake skills touch the same territory. One skill owns each concern;
the others stay available as reference. Project-specific overrides always
live in `.agents/rules/`, never in a skill body.

- **Design quad** (all three are intake skills with distinct jobs):
  - `ui-ux-pro-max` owns **design-system decisions** — styles, color
    palettes, typography pairings, UX rules, stack UI guidance.
  - `huashu-design` owns **creative artifacts** — prototypes, slide decks,
    animations, mockups, visual directions for exploration.
  - `frontend-design` owns **production SaaS UI restraint** — hierarchy,
    states, spacing, copy, and usability review of implemented screens.
  - `ui-design` and `web-design-guidelines` are review reference only;
    they do not decide design-system choices.
- **React performance:** `react-best-practices` (Vercel direct intake) is
  **authoritative**; PyModel's `vercel-react-best-practices` is a
  supplementary mirror of the same upstream rules.
- **Testing practice:** house skills govern — `react-testing` over PyModel
  `vitest`, `playwright-testing` over PyModel `playwright`,
  `test-driven-development` over PyModel `tdd`; the PyModel skills supply
  tool-level reference detail only.
- **Composition:** `vercel-composition-patterns` supplies composition
  patterns; performance rules belong to `react-best-practices`.
- **Backend stack intake** (vendored, unmodified except frontmatter):
  `nestjs-architecture-principles`, `nestjs-professional-software-engineering`,
  and `nestjs-features-performance` come from
  `github.com/amirtaherkhani/nestjs-skills` (MIT); `graphql-schema` from
  `github.com/apollographql/skills` (MIT); `postgresql-best-practices` from
  `github.com/microsoft/postgres-skills` (MIT). Each skill directory carries
  its upstream `LICENSE`.
  - **NestJS:** `nestjs-professional-software-engineering` owns day-to-day
    implementation; `nestjs-architecture-principles` owns module-boundary and
    dependency decisions; `nestjs-features-performance` owns runtime
    primitives and performance. Upstream's `nestjs-oop-design-patterns`,
    `nestjs-code-audit`, `nestjs-feature-audit`, and
    `nestjs-git-commit-pr-message` are **not** installed: they overlap
    `nestjs-architecture-principles` and the shared `code-reviewer`,
    `architecture-review`, and `git-commit` skills.
  - **GraphQL:** `graphql-schema` owns SDL design; `graphql-testing` owns
    executable contract tests. They are separate responsibilities.
  - **PostgreSQL:** `postgresql-best-practices` owns relational design,
    indexing, transactions, and migrations; `database-integration-testing`
    owns proving them against a disposable database. Neon's alternative
    collection is not installed to avoid two competing sources.

## Rules for maintainers

- Skills stay **generic** (technology- and project-agnostic). Project-specific
  context — product domain, data sources, priority areas, open decisions — is
  injected through config/rules, not skill bodies: see `.agents/rules/`
  (`qa-invariants.md`, `staffing-platform-context.md`, contributed by the QA
  team).
- A skill has exactly one home: `skills/shared/`, `skills/frontend/`,
  `skills/backend/`, or `skills/qa/`. Two categories may not claim the same
  skill name — the flat agent directories could not link it. `sync_skills.py`
  fails on a duplicate name.
- Adding a skill requires a catalog entry here and a link in all five agent
  skills directories (`.agents/`, `.opencode/`, `.claude/`, `.codex/`,
  `.github/skills/`) — run `python3 scripts/sync_skills.py` to create or refresh
  references, `--verify` to check them, `--prune` to drop stale ones.
  Verification checks enforce both the catalog entry and the references.
- `openspec/config.yaml` may name only skills homed in `skills/shared/`. Every
  schema may name shared skills; a team schema
  (`openspec/schemas/frontend|backend|qa/`) may also name the skills of its
  own team home.


## Staffing project adapters (retained integration contracts)

# Shared Skills Catalog

`skills/` is the single source of truth. Agent-specific skill directories are references generated by `scripts/sync_skills.py`; edit the shared skill, never an agent-local copy.

## Scope and naming

- **Shared skills** are discipline-neutral and keep unprefixed names. Use them across frontend, backend, QA, and other work only when relevant.
- Project-authored adapters declare `metadata.scope`: `shared`, `backend`, `frontend`, or `fullstack`. The sync script checks declared scope against the skill home before it changes any agent references.
- **Discipline-specific extensions** use the matching prefix: `backend-`, `frontend-`, or `fullstack-`. A skill's description must make its scope clear. Shared skills remain unprefixed.
- Use `shared` for reusable process, review, and tooling guidance that applies across disciplines. Use `fullstack` for a skill whose workflow coordinates a frontend change with a backend change; don't combine independent frontend and backend specialist instructions into one skill.
- Keep project adapters in their team home under `skills/frontend/` or `skills/backend/`, and cross-team adapters under `skills/shared/`. Agent references remain flat.
- Do not create placeholder frontend or fullstack skills. Add them when the relevant conventions and requirements are known, using `<scope>-<technology-or-concern>-<capability>` names.
- The script syncs every scope to every configured agent. Agent integrations are not discipline-specific; the scope metadata tells the agent when a skill applies.

Frontmatter example:

```yaml
name: backend-nestjs-code-quality
description: >-
  Reviews NestJS backend implementation quality. Use for backend code changes.
metadata:
  scope: backend
```

## Backend extension skills

These are conditional extensions for the Staffing backend. Select only the skills relevant to a backend change; do not apply them to frontend-only, mobile, or QA work. They complement shared skills such as `architecture-review`, `code-reviewer`, `test-driven-development`, and `neat-freak`.

| Skill | Use when |
|---|---|
| [`backend-nestjs-architecture-review`](backend/backend-nestjs-architecture-review/SKILL.md) | A backend change affects Nest modules, DDD boundaries, application/domain layers, repositories, or cross-module transactions. |
| [`backend-nestjs-code-quality`](backend/backend-nestjs-code-quality/SKILL.md) | Implementing, refactoring, or reviewing TypeScript/NestJS backend code. |
| [`backend-security-review`](backend/backend-security-review/SKILL.md) | A backend change touches auth, RBAC, GraphQL exposure, sensitive data, imports, SMTP, or abuse controls. |
| [`backend-graphql-api-contract-review`](backend/backend-graphql-api-contract-review/SKILL.md) | Adding or changing backend GraphQL operations, schema types, validation, authorization, or Postman requests. |
| [`backend-prisma-postgresql-integrity-review`](backend/backend-prisma-postgresql-integrity-review/SKILL.md) | Changing backend Prisma models, PostgreSQL migrations/constraints, transactions, seeds, or imports. |
| [`backend-documentation-correctness`](backend/backend-documentation-correctness/SKILL.md) | Any backend change requiring document-first planning or updates to specs, API examples, README, environment, Docker, Makefile, or Postman docs. |
| [`backend-nestjs-test-verification`](backend/backend-nestjs-test-verification/SKILL.md) | An approved backend task asks for tests or verification of NestJS, GraphQL, Prisma, migration, seed, or email behavior. |

## Synchronize agent references

```sh
python scripts/sync_skills.py
python scripts/sync_skills.py --verify
```

The script supports OpenCode, Antigravity/Gemini, Claude Code, GitHub Copilot, and Codex. Synchronization and `--verify` validate declared scope against category ownership. Imported skills without scope retain their upstream frontmatter and names. Use `--prune` when skills are renamed or deleted. Use `--force` only after confirming a real directory contains no unique content.

## Frontend extension skills

Frontend work reads `frontend/DESIGN.md` and `frontend/ARCHITECTURE.md`. Apply only relevant extensions:

| Skill | Trigger |
| --- | --- |
| [frontend-ui-design](frontend/frontend-ui-design/SKILL.md) | Reference-led frontend screen design and visual review |
| [frontend-design-system-maintenance](frontend/frontend-design-system-maintenance/SKILL.md) | Shared frontend component and pattern changes |
| [frontend-design-token-maintenance](frontend/frontend-design-token-maintenance/SKILL.md) | Canonical frontend token/build/migration changes |
| [frontend-react-architecture-review](frontend/frontend-react-architecture-review/SKILL.md) | Frontend layers, routing and state ownership |
| [frontend-accessibility-review](frontend/frontend-accessibility-review/SKILL.md) | Frontend semantics, keyboard, contrast and reflow |
| [frontend-test-verification](frontend/frontend-test-verification/SKILL.md) | Frontend checks, browser evidence and baseline review |

On Windows with `core.symlinks=false`, Git may check out references as relative-path files. Normal sync safely hydrates exact expected references as symlinks/junctions and refuses unrelated files. Verify hydrated references with `python scripts/sync_skills.py --verify`. Junctions can appear as deleted symlinks to Git: before staging, use `python scripts/sync_skills.py --mode portable` and `python scripts/sync_skills.py --verify --mode portable` to restore/validate Git's relative-path representation. Portable verification checks target provenance; it does not claim a native directory link. Run normal sync again before agent use. Canonical skill content is never copied.

### Component implementation and documentation extensions

| Skill | Trigger |
| --- | --- |
| [frontend-shadcn-workflow](frontend/frontend-shadcn-workflow/SKILL.md) | Frontend primitive creation, source migration and registry updates |
| [frontend-storybook-documentation](frontend/frontend-storybook-documentation/SKILL.md) | Frontend public component/pattern documentation and coverage |

The eight frontend adapters use selected established guidance described in [frontend UI skill adoption](../docs/frontend-ui-skill-adoption.md). Four workflows are incorporated through local supporting checklists; upstream packages are not installed or vendored skills. Product defaults and the missing-component roadmap live in [COMPONENTS.md](../frontend/COMPONENTS.md).

### Adopted design workflows

Use frontend-design-system-maintenance for component audit and extension; frontend-ui-design for design preparation and rendered critique; frontend-react-architecture-review for composition and state contracts. Each entrypoint links its local checklist. These adaptations incorporate the selected Anthropic and Vercel workflows while preserving the existing eight-skill catalog and OpenSpec artifact lifecycle. See the adoption register above for official attribution and authority limits.
