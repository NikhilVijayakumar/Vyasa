---
type: Technology
title: "Google Sheets API for the Registry"
description: What the Sheets API offers and lacks for a shared registry: batching, quotas, identities, scopes, and the absence of transactions.
tags: [google-sheets, api, quotas, service-account]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
stale_after: 2027-01-26T00:00:00Z
sources:
  - id: sy
    resource: /architecture/synchronization.md
    title: Synchronization
  - id: auth
    resource: /architecture/synchronization/auth-limits-and-devices.md
    title: Authentication, API Limits, and Cross-Device Behaviour
---

# What it offers

- Batch reads and writes of cell ranges in A1 notation, so a run can send many rows in few requests.
- Structure changes (tabs, columns) through a separate batch call.
- Two kinds of identity: a person authorizing through an OAuth consent flow, or a service account that acts as its own
  user.[^sy]

# What to plan for

| Topic | Consequence |
|---|---|
| Quotas | Requests are limited per minute per project and per user. Batch, back off with jitter, and honour any retry hint. Confirm current values in the provider documentation. |
| No transactions | A run can fail half-way. Make writes idempotent and keyed by project id so a rerun converges. |
| No locking | People can edit cells while a run is in progress. Compare against the last synced value before writing a field the sheet may own. |
| Service accounts | The spreadsheet must be shared with the account's email address. Access is then limited to sheets shared with it. |
| Scopes | A narrow scope that only touches files the application created or opened cannot reach a pre-existing shared sheet; the broader spreadsheet scope can. Pick deliberately. |
| Blank cells | A blank can mean unknown, cleared on purpose, or never written. Define the meaning per field. |
| Sharing | Anyone with edit access can change portfolio fields. Vyasa cannot tell who is a legitimate editor. |

# Related

- [Synchronization](/architecture/synchronization.md)
- [Synchronization Views](/architecture/views/sync-views.md)

[^sy]: Synchronization
