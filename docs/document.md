Vyasa/
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── docs/                          # delivery track: requirements
│   └── requirements/
│       ├── README.md              # requirement-package flow
│       ├── _template/             # requirement.md + grill-log.md
│       ├── functional-requirements.md
│       ├── non-functional-requirements.md
│       ├── data-ownership.md
│       ├── security-and-privacy-requirements.md
│       ├── phase-acceptance-criteria.md
│       └── <package>/             # one grilled package per epic-level requirement
├── knowledge/                     # knowledge track: OKF v0.2 bundle, independent of delivery
│   ├── index.md                   # okf_version, section listing
│   ├── log.md
│   ├── profile.json               # Vyasa OKF profile (types, folders, required fields, independence)
│   ├── product/                   # vision, scope and roadmap
│   ├── architecture/              # system, data model, scanning, MCP, storage, sync, remote, security model
│   ├── concepts/                  # domain concepts and glossary-level ideas
│   ├── decisions/                 # ADRs (type: Decision)
│   ├── practices/                 # engineering practices, test strategy
│   ├── technologies/              # technology guidance (added when needed)
│   ├── runbooks/                  # setup, troubleshooting, recovery (added when needed)
│   └── glossary/                  # terms (added when needed)
├── openspec/                      # agreed behaviour and change workflow
│   ├── config.yaml
│   ├── schemas/backend/
│   ├── specs/
│   └── changes/
├── src/
└── tests/
