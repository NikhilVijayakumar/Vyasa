---
type: Architecture
title: "Security and Privacy — Vyasa (व्यास)"
description: Trust boundaries, threat model, and security and privacy controls across all phases.
tags: [security, privacy, trust-boundary]
status: draft
generated: { by: human:nikhil-vijayakumar, at: 2026-10-26T00:00:00Z }
---
# Security and Privacy — Vyasa (व्यास)

## Summary

This document describes the security and privacy model of Vyasa: a local-first workspace intelligence system that discovers software projects, extracts deterministic metadata, indexes evidence, and exposes project knowledge to coding agents through MCP.

## Parts

This concept is split into parts so each can be read on its own. Section numbers in the table are those of the original document, so references such as "§9.11" resolve to the part that contains them.

| Part | Sections | What it answers |
|---|---|---|
| [Objectives, Scope, and Threat Model](security-and-privacy/objectives-scope-threats.md) | §1–3 | Security objectives, posture, assets, threat actors, trust boundaries, and the limits of the model. |
| [Data Classification, Filesystem, and Local Storage](security-and-privacy/data-and-boundaries.md) | §4–6 | Classification and minimization, filesystem and repository boundaries, and local database security. |
| [MCP Security and Credential Management](security-and-privacy/mcp-and-credentials.md) | §7–8 | What MCP clients may do and receive, and how secrets are stored and rotated. |
| [Google Sheets and Remote Repository Security](security-and-privacy/sheets-and-remote.md) | §9–10 | Security of the shared registry and of provider access. |
| [Logging, Configuration, Incident Response, and References](security-and-privacy/operations-and-response.md) | §11– | Safe logging, secure defaults, incident response, and references. |
