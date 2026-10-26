# Requirements

Requirement packages: the grilled, reviewed intent that OpenSpec changes
implement. The existing documents here (`functional-requirements.md`,
`non-functional-requirements.md`, `data-ownership.md`,
`security-and-privacy-requirements.md`, `phase-acceptance-criteria.md`) are the product-wide
baseline; new work adds one package per epic-level requirement.

```
docs/requirements/<package>/
├── requirement.md   # intent, scope, behaviour, constraints, acceptance, open decisions
└── grill-log.md     # grill-me review across the eight dimensions, with decisions
```

Copy `_template/` to start a package.

## Flow

1. **Knowledge first.** Apply the `knowledge-first` skill: find the relevant
   concepts in `knowledge/`; create missing ones there first; list them under
   Knowledge References. Requirements link to knowledge, never the reverse.
2. **Grill.** Run `grill-me` until each dimension in `grill-log.md` is
   resolved or recorded as an accepted open decision.
3. **Specify.** Create the OpenSpec change (`openspec new change "be-<id>"`),
   citing the package and the same knowledge concepts.
4. **Slice.** Tasks are vertical slices (`knowledge/practices/vertical-slices.md`).

A requirement may span several changes; a change may need several slices.
