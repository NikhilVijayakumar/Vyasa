"""The ``vyasa`` command line: ``scan`` updates the index, ``profile-context`` prints what is known about one repository."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
from importlib.metadata import PackageNotFoundError, version
from dataclasses import replace
from pathlib import Path
import os
import sys
from collections.abc import Mapping, Sequence
from typing import TextIO

from vyasa.adapters.sqlite.database import open_index
from vyasa.application import profile_context
from vyasa.application import query as queries
from vyasa.application.configuration.workspace import load_workspace_config, check_roots, data_directory
from vyasa.application.configuration.workspace_names import read_name, write_name
from vyasa.application.indexing.scan import RootResult, scan_workspace
from vyasa.application.indexing.project_scan import scan_project
from vyasa.application.scanning.frameworks import default_registry
from vyasa.application.indexing.store import index_path
from vyasa.domain.index import IN_PROGRESS, INTERNAL_ERROR, UNAVAILABLE, INVALID_INPUT, IndexStoreError
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


def selected_root(config, requested: str) -> Path:
    key = os.path.normcase(os.path.normpath(requested))
    root = next ( (r for r in config.roots if os.path.normcase(os.path.normpath(str(r))) == key), None )
    if root is None:
        raise IndexStoreError(INVALID_INPUT, "The workspace is not a configured root.")
    return root


def scan(config_path: str | None, environ: Mapping[str, str], out: TextIO, err: TextIO, workspace: str | None = None) -> int:
    try:
        config = load_workspace_config(config_path, environ)
    except ConfigError as error:
        err.write("The configuration is invalid:\n" + "".join(f"  {problem}\n" for problem in error.problems))
        return USAGE
    if isinstance(config, NotConfigured):
        err.write(f"Nothing to scan: {config.reason}.\nList your workspace roots in config.toml, for example:\n{EXAMPLE}\n")
        return USAGE

    if workspace is not None:
        try:
            config = replace(config, roots=(selected_root(config, workspace),))
        except IndexStoreError as error:
            err.write(f"{error}\n")
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


def project_scan_command(project_id: str, config_path: str | None, environ: Mapping[str, str], out: TextIO) -> int:
    def error(code: str, message: str, exit_code: int) -> int:
        out.write(json.dumps({"error": {"code": code, "message": message}}) + "\n")
        return exit_code

    if not project_id or len(project_id) > 200:
        return error("INVALID_INPUT", "Invalid project identifier.", USAGE)
    try:
        config = load_workspace_config(config_path, environ)
    except ConfigError:
        return error("CONFIG_INVALID", "The workspace configuration is invalid.", USAGE)
    if isinstance(config, NotConfigured):
        return error("CONFIG_NOT_FOUND", "The workspace configuration is unavailable.", USAGE)
    path = index_path(environ)
    if not path.is_file():
        return error(UNAVAILABLE, "The index is unavailable.", INDEX)
    try:
        connection = open_index(path)
        try:
            result = scan_project(config, connection, project_id, owner=f"cli-{os.getpid()}")
        finally:
            connection.close()
    except IndexStoreError as exc:
        exit_code = BUSY if exc.code == IN_PROGRESS else USAGE if exc.code in (INVALID_INPUT, "PROJECT_NOT_FOUND") else INDEX
        return error(exc.code, "The project scan could not be completed.", exit_code)
    except Exception:
        return error(INTERNAL_ERROR, "The project scan could not be completed.", INDEX)
    out.write(json.dumps({"schema_version": "1", "data": result}) + "\n")
    return OK if result["status"] == "completed" else PARTIAL


def profile_context_command(path: str, out: TextIO, err: TextIO) -> int:
    """Print the context bundle of one repository from a live read-only scan. Nothing is written anywhere."""
    try:
        bundle = profile_context.live_context(path)
    except profile_context.NotAProject as error:
        err.write(f"{error}\n")
        return USAGE
    except Exception:  # noqa: BLE001 - never show repository text
        err.write("The profile context could not be produced because of an internal error.\n")
        return INDEX
    out.write(json.dumps(bundle, indent=2, sort_keys=True) + "\n")
    return OK


def indexed_query(args: argparse.Namespace, environ: Mapping[str, str], out: TextIO) -> int:
    """Run one fixed indexed query; never create or update the index."""
    if args.operation == "capabilities":
        out.write(json.dumps({"schema_version": "1", "data": {"capabilities": {"project_scan": 1}}}) + "\n")
        return OK
    if args.operation == "version":
        try:
            package_version = version("vyasa")
        except PackageNotFoundError:
            out.write(json.dumps({"error": {"code": INTERNAL_ERROR, "message": "Backend version metadata is unavailable."}}) + "\n")
            return INDEX
        out.write(json.dumps({"schema_version": "1", "data": {"version": package_version}}) + "\n")
        return OK
    if args.operation == "technologies":
        try:
            registry = default_registry()
            entries = [{"key": e.key, "name": e.name, "category": e.category, "ecosystem": e.ecosystem}
                       for e in sorted(registry.entries, key=lambda e: (e.name.casefold(), e.key))]
            out.write(json.dumps({"schema_version": "1", "data": {"registry_version": registry.version,
                                                                      "technologies": entries}}) + "\n")
            return OK
        except Exception:  # noqa: BLE001 - avoid exposing internal paths
            out.write(json.dumps({"error": {"code": INTERNAL_ERROR, "message": "The technology catalog is unavailable."}}) + "\n")
            return INDEX
    workspace = None
    if args.operation == "workspaces" or (args.operation == "search" and args.workspace is not None):
        try:
            config = load_workspace_config(None, environ)
            if isinstance(config, NotConfigured):
                raise IndexStoreError(UNAVAILABLE, config.reason)
            if args.operation == "workspaces":
                out.write(json.dumps({"schema_version": "1", "data": {"workspaces": [
                    {"root": str(item.root), "status": item.status, "name": read_name(data_directory(environ), item.root)} for item in check_roots(config)
                ]}}) + "\n")
                return OK
            workspace = str(selected_root(config, args.workspace))
        except (IndexStoreError, ConfigError) as error:
            out.write(json.dumps({"error": {"code": INVALID_INPUT, "message": str(error)}}) + "\n")
            return INDEX
    path = index_path(environ)
    try:
        if not path.is_file():
            raise IndexStoreError(UNAVAILABLE, "The index is not available. Run a scan first.")
        connection = open_index(path, read_only=True)
        try:
            if args.operation == "status":
                result = queries.get_index_status(connection)
            elif args.operation == "search":
                result = queries.search_projects(connection, query=args.query, technology=args.technology,
                                                 limit=args.limit, cursor=args.cursor, workspace=workspace)
            elif args.operation == "project":
                result = queries.get_project(connection, args.project_id)
            elif args.operation == "dependencies":
                result = queries.get_project_dependencies(connection, args.project_id)
            elif args.operation == "context":
                result = profile_context.profile_context(connection, args.project_id)
            else:
                result = queries.get_project_report(connection, args.project_id)
        finally:
            connection.close()
    except IndexStoreError as error:
        out.write(json.dumps({"error": {"code": error.code, "message": str(error).split(": ", 1)[-1]}}) + "\n")
        return INDEX
    except Exception:  # noqa: BLE001 - do not expose untrusted data or internal exceptions
        out.write(json.dumps({"error": {"code": INTERNAL_ERROR, "message": "The query could not be completed."}}) + "\n")
        return INDEX
    out.write(json.dumps(result, ensure_ascii=True) + "\n")
    return OK


def name_workspace(root: str, name: str, environ: Mapping[str, str], out: TextIO) -> int:
    try:
        config = load_workspace_config(None, environ)
        if isinstance(config, NotConfigured):
            raise IndexStoreError(UNAVAILABLE, config.reason)
        configured = selected_root(config, root)
        value = write_name(data_directory(environ), configured, name)
        out.write(json.dumps({"schema_version": "1", "data": {"root": str(configured), "name": value}}) + "\n")
        return OK
    except (IndexStoreError, ConfigError) as error:
        code = error.code if isinstance(error, IndexStoreError) else INVALID_INPUT
        out.write(json.dumps({"error": {"code": code, "message": str(error)}}) + "\n")
        return INDEX


def main(argv: Sequence[str] | None = None, environ: Mapping[str, str] | None = None, out: TextIO | None = None, err: TextIO | None = None) -> int:
    out, err = out or sys.stdout, err or sys.stderr
    parser = argparse.ArgumentParser(prog="vyasa", description="Local-first workspace intelligence.")
    commands = parser.add_subparsers(dest="command", required=True)
    scan_parser = commands.add_parser("scan", help="scan the configured workspace roots and update the index")
    scan_parser.add_argument("--workspace", help="scan only this configured workspace root")
    scan_parser.add_argument("--project", help="scan one indexed project")
    scan_parser.add_argument("--json", action="store_true", help="return structured project scan results")
    scan_parser.add_argument("--config", help="path to a configuration file (default: config.toml in the data directory)")
    workspace_parser = commands.add_parser("workspace", help="manage local workspace metadata")
    workspace_commands = workspace_parser.add_subparsers(dest="workspace_operation", required=True)
    set_name_parser = workspace_commands.add_parser("set-name")
    set_name_parser.add_argument("--root", required=True)
    set_name_parser.add_argument("--name", required=True)
    query_parser = commands.add_parser("query", help="query the existing index as JSON without scanning")
    operations = query_parser.add_subparsers(dest="operation", required=True)
    operations.add_parser("version", help="report the installed backend version")
    operations.add_parser("capabilities", help="report supported backend capabilities")
    operations.add_parser("status", help="report index status")
    operations.add_parser("workspaces", help="list configured workspace roots")
    operations.add_parser("technologies", help="list supported technology filters")
    search_parser = operations.add_parser("search", help="search indexed projects")
    search_parser.add_argument("--query")
    search_parser.add_argument("--technology")
    search_parser.add_argument("--workspace")
    search_parser.add_argument("--limit", type=int, default=20)
    search_parser.add_argument("--cursor")
    for name in ("project", "dependencies", "context", "report"):
        operation = operations.add_parser(name)
        operation.add_argument("project_id")
    context_parser = commands.add_parser(
        "profile-context", help="print what Vyasa observes about one repository, for a coding agent writing its profile"
    )
    context_parser.add_argument("path", nargs="?", default=".", help="the repository root (default: the current directory)")
    arguments = list(sys.argv[1:] if argv is None else argv)
    project_request = any(arg == "--project" or arg.startswith("--project=") for arg in arguments)
    try:
        if project_request:
            with contextlib.redirect_stderr(io.StringIO()):
                args = parser.parse_args(arguments)
        else:
            args = parser.parse_args(arguments)
    except SystemExit as exit_:
        if exit_.code and project_request:
            out.write(json.dumps({"error": {"code": "INVALID_INPUT", "message": "Invalid project scan arguments."}}) + "\n")
        return USAGE if exit_.code else OK
    if args.command == "scan" and args.json and args.project is None:
        out.write(json.dumps({"error": {"code": "INVALID_INPUT", "message": "Invalid project scan arguments."}}) + "\n")
        return USAGE
    if args.command == "scan" and args.project is not None:
        if not args.json or args.workspace is not None:
            out.write(json.dumps({"error": {"code": "INVALID_INPUT", "message": "Invalid project scan arguments."}}) + "\n")
            return USAGE
        return project_scan_command(args.project, args.config, os.environ if environ is None else environ, out)
    if args.command == "workspace":
        return name_workspace(args.root, args.name, os.environ if environ is None else environ, out)
    if args.command == "profile-context":
        return profile_context_command(args.path, out, err)
    if args.command == "query":
        return indexed_query(args, os.environ if environ is None else environ, out)
    return scan(args.config, os.environ if environ is None else environ, out, err, args.workspace)


def run() -> None:
    raise SystemExit(main())
