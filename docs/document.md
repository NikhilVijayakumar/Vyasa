Vyasa/
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── docs/                          # delivery track: requirements
│   └── requirements/
│       ├── README.md              # package index and flow
│       ├── decisions-for-review.md  # generated: every decision still needed, with a recommendation
│       ├── _template/             # requirement.md + grill-log.md
│       ├── functional-requirements.md
│       ├── non-functional-requirements.md
│       ├── data-ownership.md
│       ├── security-and-privacy-requirements.md
│       ├── phase-acceptance-criteria.md
│       └── <package>/             # 12 grilled packages
│           ├── requirement.md
│           ├── grill-log.md
│           ├── diagrams.md
│           └── features/*.feature
├── knowledge/                     # knowledge track: OKF v0.2 bundle, independent of delivery
│   ├── index.md                   # okf_version, section listing
│   ├── log.md
│   ├── profile.json               # Vyasa OKF profile (types, folders, required fields, independence)
│   ├── product/                   # vision, scope and roadmap (overview + parts)
│   ├── architecture/              # 8 overviews, each with a folder of parts, plus c4-system-views and views/
│   │   └── views/                 # deployment, scan pipeline, data model, MCP, storage, sync, remote, security
│   ├── concepts/                  # principles, identity, ownership, evidence, glossary
│   ├── decisions/                 # 18 draft ADRs (type: Decision)
│   ├── practices/                 # testing, errors, logging, configuration, dependencies, vertical slices
│   ├── technologies/              # SQLite, MCP, Sheets API, GitHub/Bitbucket, Git metadata, Python, OKF
│   └── runbooks/                  # credential leak, data leak, index recovery, conflict review
├── docs/reviews/                  # grill records for the knowledge bundle
├── openspec/                      # agreed behaviour and change workflow
│   ├── config.yaml
│   ├── schemas/backend/
│   ├── specs/
│   └── changes/
├── src/
└── tests/
