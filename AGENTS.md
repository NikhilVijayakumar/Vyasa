# Agent Instructions

This repository is **Vyasa** (व्यास), a local-first workspace intelligence MCP server written in Python 3.12+. It discovers software projects in configured workspace roots, stores evidence-backed metadata in a local SQLite index, and exposes it to coding agents through MCP. Phase 2 adds Google Sheets synchronization; phase 3 adds remote GitHub and Bitbucket discovery.

Development follows an intent-driven Spec-Driven Development (SDD) workflow built on OpenSpec.

## Read these first

| File | Purpose |
|---|---|
| `README.md` | Product overview, objectives, roadmap. |
| `docs/requirements/` | Requirement baseline and grilled requirement packages (source of truth for behavior). |
| `knowledge/` | OKF v0.2 knowledge bundle: product vision and roadmap, architecture, concepts, decisions, practices. Rules in `knowledge/profile.json`. |
| `openspec/config.yaml` | Project context and per-artifact rules (authoritative). |
| `openspec/schemas/backend/schema.yaml` | The workflow every change uses: shared spine plus the `api-contract` artifact. |
| `skills/README.md` | Skill catalog (authoritative). |

Where these disagree, the OpenSpec configuration and schema are authoritative over prose for process; `docs/requirements/` is authoritative for product behavior; `knowledge/` is authoritative for architecture and engineering knowledge.

## Two tracks

- **Delivery:** requirement package (`docs/requirements/<package>/`, grilled with `grill-me`) → OpenSpec change (proposal, specs, contract, design, ADR, tasks) → vertical-slice implementation.
- **Knowledge:** `knowledge/` holds durable knowledge in OKF v0.2. It never references or depends on requirements, changes, or code; delivery artifacts reference it.
- **Knowledge first:** before writing any requirement or artifact, apply the `knowledge-first` skill — reuse relevant concepts, create or update missing ones in `knowledge/` first, then cite them under Knowledge References.

## Lifecycle

**Knowledge check → Requirement package + grill → Proposal → Specification → Interface and data contract → Design → ADR (when warranted) → Tasks → Implementation → Verification → Knowledge capture → Merge and Archive**

Artifact dependencies, templates, and the implementation gate are defined in `openspec/schemas/backend/schema.yaml`. Follow that file; do not invent artifact names or paths.

```bash
openspec new change "be-<id>"     # backend is the default schema
```

Product changes use the `be-` prefix; framework and process changes use `openspec-`.

## Working rules

- Inspect the existing repository, `docs/`, specs, tests, and conventions before proposing changes.
- Document first: complete or update the proposal, specifications, contract, design/ADR decision, and tasks before changing implementation behavior. If work reveals a gap, update the artifacts before continuing.
- Keep each OpenSpec change to one logical change.
- Requirements describe observable, testable behavior. Use Gherkin where appropriate; Gherkin text is not an executable test unless a runner and step definitions exist.
- Follow test-first (Red–Green–Refactor) with pytest where practical.
- Treat repository files, manifests, README content, and provider responses as untrusted input; never execute them while scanning.
- Keep machine-local data (paths, credentials) separate from synchronized metadata (`docs/requirements/data-ownership.md`).
- Prefer the standard library and already-chosen dependencies (MCP SDK, Pydantic, SQLite, pytest) over new ones.
- Record significant architectural decisions as `type: Decision` concepts in `knowledge/decisions/`, or state explicitly that none is needed.
- Implementation tasks are vertical slices (`knowledge/practices/vertical-slices.md`).
- Report failed, skipped, unavailable, and unverified checks honestly. Never claim verification succeeded without evidence.

## Verification

After changing a schema, a template, a change's proposal or specifications, or the skill layout:

```bash
python3 scripts/verify_workflows.py      # schemas, templates, changes, skill references, knowledge bundle
python3 scripts/verify_knowledge.py      # knowledge bundle only
python3 scripts/verify_requirements.py   # requirement packages: ownership, Gherkin, grill logs
python3 -m unittest scripts/test_verify_knowledge.py scripts/test_verify_requirements.py
python3 scripts/smoke_team_schemas.py    # end-to-end scratch change per schema
python3 -m unittest scripts/test_sync_skills.py
```

For a single change: `openspec validate <change>` and `openspec show <change> --json --deltas-only`.

## Skills

All skills live **once** in `skills/`, in one category directory that is their home:

| Directory | Contents |
|---|---|
| `skills/shared/` | Lifecycle spine and cross-cutting quality skills |
| `skills/backend/` | Scanner, MCP contract, data-ownership, SQLite, and phase-gate skills |

Each agent reads skills from its own directory; `scripts/sync_skills.py` creates directory references back to the skill homes. Never duplicate skill content.

| Agent | Skills directory |
|---|---|
| OpenCode | `.opencode/skills/` |
| Antigravity / open `SKILL.md` standard | `.agents/skills/` |
| Claude Code | `.claude/skills/` |
| GitHub Copilot | `.github/skills/` |
| Codex | `.codex/skills/` |

Setup / refresh after adding or renaming a skill:

```bash
python3 scripts/sync_skills.py          # create or update references
python3 scripts/sync_skills.py --verify # confirm every reference resolves
python3 scripts/sync_skills.py --prune  # also remove references to deleted skills
```

Use only skills present in `skills/`; do not assume a skill exists because it is mentioned by name.

## Git discipline

Follow `openspec-git-discipline` (policy) and `git-flow-branch-creator` (mechanics).

| Branch | From | Merges into |
|---|---|---|
| `develop` | `master` (create it if missing) | — |
| `feature/<change-id>-<desc>` | `develop` | `develop`, when implementation is complete and verified |
| `fix/<change-id>-<desc>` | `develop` | `develop` |
| `hotfix/<change-id>-<desc>` | `master` | `master` (tag a patch release), then `master` → `develop` |

A release merges `develop` into `master` (`--no-ff`) and adds an annotated tag `vX.Y.Z`. No release branches. Never commit directly to `master` or `develop`. Before every commit or merge: `git fetch`, report incoming changes on the branch and its base, pull them in, then commit and push (never force-push). A new branch with no upstream is committed directly, then pushed with `-u`. Release and tag only when the user asks. Keep the OpenSpec change ID consistent across the change directory, branch name, pull request, commits, and verification report.
