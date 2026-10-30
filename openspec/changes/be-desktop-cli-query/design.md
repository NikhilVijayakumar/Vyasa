# Design

## Context

The CLI has scan and live profile-context; application query services already own index semantics.

## Goals / Non-Goals

Add a bounded read-only JSON adapter. Do not duplicate query or persistence logic, add network access, modify scan semantics, or expose local paths.

## Decisions

Dispatch a fixed command set to existing query functions; open the index using the existing read-only adapter and map IndexStoreError to the structured error envelope. Keep scan untouched. A missing index is detected before opening. CLI argument parsing uses argparse and no shell.

## Risks / Trade-offs

The existing service envelope defines the public result contract; tests must cover successful queries, missing indexes and invalid input and confirm no writes.
