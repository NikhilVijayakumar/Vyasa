"""The ``vyasa`` command line. Only ``scan`` exists so far."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Mapping, Sequence
from typing import TextIO

from vyasa.adapters.sqlite.database import open_index
from vyasa.application.configuration.workspace import load_workspace_config
from vyasa.application.indexing.scan import RootResult, scan_workspace
from vyasa.application.indexing.store import index_path
from vyasa.domain.index import IN_PROGRESS, IndexStoreError
from vyasa.domain.workspace_config import ConfigError, NotConfigured

OK, PARTIAL, USAGE, BUSY, INDEX = 0, 1, 2, 3, 4
EXAMPLE = '[workspace]\nroots = ["~/work", "/data/projects"]'
COUNT_ORDER = ("added", "attached", "updated", "unchanged", "restored", "missing", "inaccessible", "conflicts")


def _counts(result: RootResult) -> str:
    counts = result.stored.counts
    parts = [f"{counts[key]} {key}" for key in COUNT_ORDER if counts.get(key)]
    return ", ".join(parts) or "nothing to store"


def _root_lines(result: RootResult) -> list[str]:
    run = result.run
    found = len(run.repositories)
    head = f"{result.root}: {result.stored.status} - {found} repositories ({_counts(result)})"
    lines = [head]
    if run.status == "failed" and run.issues:
        lines.append(f"  could not scan: {run.issues[0].reason}")
    elif run.issues:
        lines.append(f"  {len(run.issues) + run.issues_omitted} directories could not be read")
    lines += [f"  skipped {w.reason} x{w.count}: {w.advice}" for w in run.warnings]
    return lines


def scan(config_path: str | None, environ: Mapping[str, str], out: TextIO, err: TextIO) -> int:
    try:
        config = load_workspace_config(config_path, environ)
    except ConfigError as error:
        err.write("The configuration is invalid:\n" + "".join(f"  {problem}\n" for problem in error.problems))
        return USAGE
    if isinstance(config, NotConfigured):
        err.write(f"Nothing to scan: {config.reason}.\nList your workspace roots in config.toml, for example:\n{EXAMPLE}\n")
        return USAGE

    index_file = index_path(environ)
    created = not index_file.exists()
    try:
        connection = open_index(index_file)
    except IndexStoreError as error:
        err.write(f"{error}\n")
        return INDEX
    try:
        out.write(f"Scanning {len(config.roots)} workspace root(s) from {config.source}\n")
        for warning in config.warnings:
            out.write(f"  note: {warning}\n")
        try:
            results = scan_workspace(config, connection, owner=f"cli-{os.getpid()}")
        except IndexStoreError as error:
            err.write(f"{error}\n")
            return BUSY if error.code == IN_PROGRESS else INDEX
        for result in results:
            out.write("\n".join(_root_lines(result)) + "\n")
        total = connection.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    finally:
        connection.close()
    if created:
        out.write("Created the index.\n")
    out.write(f"Indexed {total} projects in {index_file}.\n")
    return OK if all(r.stored.status == "completed" for r in results) else PARTIAL


def main(argv: Sequence[str] | None = None, environ: Mapping[str, str] | None = None, out: TextIO | None = None, err: TextIO | None = None) -> int:
    out, err = out or sys.stdout, err or sys.stderr
    parser = argparse.ArgumentParser(prog="vyasa", description="Local-first workspace intelligence.")
    commands = parser.add_subparsers(dest="command", required=True)
    scan_parser = commands.add_parser("scan", help="scan the configured workspace roots and update the index")
    scan_parser.add_argument("--config", help="path to a configuration file (default: config.toml in the data directory)")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exit_:
        return USAGE if exit_.code else OK
    return scan(args.config, os.environ if environ is None else environ, out, err)


def run() -> None:
    raise SystemExit(main())
