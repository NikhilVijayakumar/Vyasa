# Requirements

Requirements are organized as **requirement packages**: one per logical part, each with its intent, its scenarios
as Gherkin, a grill log, and diagrams. The baseline documents (`functional-requirements.md`,
`non-functional-requirements.md`, `data-ownership.md`, `security-and-privacy-requirements.md`,
`phase-acceptance-criteria.md`) hold the product-wide statements, tables, and gates that the packages refer to.

## Packages

| Package | Owns | Phase |
|---|---|---|
| [workspace-discovery](workspace-discovery/requirement.md) | FR-001, FR-002, FR-015, FR-022 | P1 |
| [project-identity](project-identity/requirement.md) | FR-003, FR-020, NFR-004 | P1 |
| [metadata-and-evidence](metadata-and-evidence/requirement.md) | FR-004–006, NFR-001, 002, 005 | P1 |
| [file-composition](file-composition/requirement.md) | FR-021 | P1 |
| [language-detection](language-detection/requirement.md) | FR-023 | P1 |
| [project-markers](project-markers/requirement.md) | FR-024 | P1 |
| [framework-detection](framework-detection/requirement.md) | FR-025 | P1 |
| [local-index](local-index/requirement.md) | FR-007, FR-008, NFR-003 | P1 |
| [project-query](project-query/requirement.md) | FR-009–012 | P1 |
| [mcp-server](mcp-server/requirement.md) | FR-013, NFR-021, 038, 039 | P1 |
| [project-profile](project-profile/requirement.md) | FR-014 | P1 |
| [shared-registry](shared-registry/requirement.md) | FR-016, FR-017, NFR-018, 035 | P2 |
| [remote-discovery](remote-discovery/requirement.md) | FR-018, FR-019, NFR-022, 036, 037 | P3 |
| [data-ownership](data-ownership/requirement.md) | DOR-001–012 | P1–P3 |
| [security-and-privacy](security-and-privacy/requirement.md) | NFR-016, 017, 019, 020, SEC-001–052 | P1–P3 |
| [quality-attributes](quality-attributes/requirement.md) | NFR-006–015, 023–034, 040–043 | P1–P3 |

Every FR and NFR is owned by exactly one package. **Start with [decisions-for-review.md](decisions-for-review.md)**:
it lists the choices the grill could not settle, each with a recommended answer.

## A package

```
docs/requirements/<package>/
├── requirement.md   # owns, knowledge references, intent, scope, statements, behaviour, constraints,
│                    # acceptance, open decisions, proposed slices
├── grill-log.md     # the grill across eight dimensions; every question has a recommendation and a status
├── diagrams.md      # C4 and dynamic views that answer package-specific questions
└── features/        # Gherkin: fr-NNN-*.feature (from the baseline) and grill-additions.feature (@proposed)
```

Scenarios tagged `@proposed` come from grill recommendations and become normative when the recommendation is
confirmed. Status of a grill answer: *Settled* (existing documents decide), *Recommended* (low risk), or
*Decision needed* (a real trade-off).

## Flow

1. **Knowledge first.** Apply the `knowledge-first` skill: find the relevant concepts in `knowledge/`, create
   missing ones there first, and list them under Knowledge References. Requirements link to knowledge, never the
   reverse.
2. **Grill.** Run `grill-me` across the eight dimensions in `_template/grill-log.md` until each is resolved or
   recorded as an accepted open decision.
3. **Specify.** Create the OpenSpec change (`openspec new change "be-<id>"`), citing the package and the same
   knowledge concepts; scenarios become the change's behavioural specification.
4. **Slice.** Tasks are vertical slices (`knowledge/practices/vertical-slices.md`); the package's Delivery section
   proposes the first ones.

A requirement may span several changes; a change may need several slices.

## Verification

```bash
python3 scripts/verify_requirements.py                  # structure, Gherkin, grill logs, ownership of every FR and NFR
python3 scripts/verify_requirements.py --decisions > docs/requirements/decisions-for-review.md
```

`decisions-for-review.md` is generated; change the answer in the grill log, then regenerate it.
