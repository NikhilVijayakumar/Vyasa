# Diagrams: Security and Privacy

C4 vocabulary: `knowledge/architecture/c4-system-views.md`. The question here is where the trust boundaries lie
and which way data may cross them.

## Where are the trust boundaries? (container view with boundaries)

```mermaid
flowchart TB
  subgraph U["Untrusted input"]
    REPO[Repository files and manifests]
    PROVC[Provider responses and remote files]
    SHEETC[Spreadsheet cell values]
  end
  subgraph L["Trusted local zone (current user)"]
    SCAN[Scanner<br/>read-only, bounded, no execution]
    IDX[(Index<br/>0600, no credentials)]
    MCP[MCP server<br/>stdio, validated, read-only DB]
    CRED[OS credential store]
    LOG[Logs<br/>redacted]
  end
  subgraph A["Agent boundary"]
    AG[Coding agent]
  end
  subgraph C["Cloud boundary (phases 2 and 3)"]
    GS[Google Sheets]
    API[GitHub and Bitbucket APIs]
  end
  REPO -->|bounded reads| SCAN
  PROVC -->|size-capped| SCAN
  SHEETC -->|schema-validated| SCAN
  SCAN --> IDX
  IDX --> MCP
  MCP -->|typed, sanitized, capped| AG
  CRED -->|token at call time| SCAN
  SCAN -->|allowlist only| GS
  SCAN -->|read-only requests| API
  SCAN --> LOG
```

Everything entering the trusted zone is treated as data. Everything leaving it is minimized, allowlisted, or
sanitized.
