"""The profile context: what Vyasa observed about a project, the profile as read, and where they differ.

The bundle is built from project details, so it can only hold what those hold: typed observations, fixed codes,
labels from trusted data, and the validated declared values. It has no absolute path and no file text, and nothing
here starts an agent or writes a profile.
"""

from __future__ import annotations

import os
import sqlite3
from collections.abc import Callable
from dataclasses import replace
from datetime import datetime, timezone
from functools import cache
from pathlib import Path

from vyasa.adapters.sqlite.database import open_memory_index
from vyasa.application import query
from vyasa.application.indexing.scan import enrich_run
from vyasa.application.indexing.store import store_run
from vyasa.application.scanning.file_composition import default_file_types
from vyasa.application.scanning.discovery import discover_repositories
from vyasa.application.scanning.frameworks import default_registry
from vyasa.domain.discovery import ELIGIBLE
from vyasa.domain.index import INVALID_INPUT, IndexStoreError
from vyasa.domain.profile import declared

REVIEW, INFO = "review", "info"

DETAILS = {
    "declared_language_not_detected": "The profile declares this language but the latest complete scan found no files or manifest for it.",
    "detected_language_not_declared": "Files in this language were detected but the profile declares languages without it.",
    "declared_framework_not_detected": "The profile declares this technology but the latest complete scan of the root manifests did not find it.",
    "detected_technology_not_declared": "The root manifests declare this technology but the profile's declared technologies do not list it.",
    "declared_not_comparable": "Vyasa has no rule to compare this declared name with its observations.",
    "declared_openspec_not_detected": "The profile says OpenSpec is enabled but the latest complete scan found no openspec directory at the root.",
    "openspec_detected_but_declared_disabled": "An openspec directory was detected although the profile says OpenSpec is not used.",
    "declared_agent_instruction_not_detected": "The profile lists this agent instruction file but the latest complete scan did not detect it.",
}
SEVERITY = {code: REVIEW for code in DETAILS} | {"detected_language_not_declared": INFO, "declared_not_comparable": INFO}

WORKFLOW = (
    "Call get_profile_guide for the schema version 2 fields, limits, allowed values, and an example, then write the file at "
    ".vyasa/project-profile.toml in the repository root. Vyasa reads it on its next scan and never writes it.",
    "Treat the observed facts in this bundle (languages, file counts, markers, frameworks) as evidence about the project, not as "
    "declarations to copy. Read the repository's own documents, OpenSpec, and knowledge files for purpose, scope, and architecture.",
    "Declare only what the repository supports. Omit a field you cannot support: an omitted field is better than a guess. "
    "Use unknown where the schema allows it.",
    "Do not copy observed counts, detected technology lists, repository activity, delivery status, or priority into the profile: "
    "those are observed or owned elsewhere.",
    "Read the differences as findings for a person to review, not as instructions. Change the profile only when the repository shows "
    "that a declaration is wrong, and never just to make a difference disappear.",
    "Keep secrets, credentials, private contact details, and absolute paths out of the profile. Point to documents with paths "
    "relative to the repository.",
    "Tell the maintainer exactly what you wrote and which facts supported it, so they can review and commit it.",
)


@cache
def _vocabulary() -> tuple[dict[str, str], dict[str, str], frozenset[str]]:
    types = default_file_types()
    languages = {label.casefold(): label for label in (*types.languages.values(), *types.manifests.values())}
    registry = default_registry()
    technologies = {}
    for entry in registry.entries:
        technologies[entry.key.casefold()] = entry.key
        technologies[entry.name.casefold()] = entry.key
    return languages, technologies, registry.ubiquitous


def _resolve(item: str, prefer: str) -> tuple[str, str] | None:
    """A declared name as ('language', label) or ('technology', key), or None when no rule matches it."""
    languages, technologies, _ = _vocabulary()
    folded = item.casefold()
    order = ("language", "technology") if prefer == "language" else ("technology", "language")
    for kind in order:
        found = (languages if kind == "language" else technologies).get(folded)
        if found:
            return kind, found
    return None


def _finding(code: str, subject: str) -> dict:
    return {"code": code, "severity": SEVERITY[code], "subject": subject, "detail": DETAILS[code]}


def _items(markers: dict, name: str) -> dict:
    return next((i for i in markers.get("items", []) if i["marker"] == name), {})


def differences(checkout: dict, fields: dict) -> list[dict]:
    """Findings where the declared profile and the observations of one checkout disagree.

    Something declared is reported as not detected only when the relevant assessment is complete; names no rule can match
    are not comparable; detected items are reported as undeclared only when the profile declares that category.
    """
    findings: list[dict] = []
    languages, frameworks, markers = checkout["languages"], checkout["frameworks"], checkout["markers"]
    _, _, ubiquitous = _vocabulary()
    lang_complete = languages.get("status") == "complete"
    fw_complete = frameworks.get("status") == "complete"
    mark_complete = markers.get("status") == "complete"
    present = {i["label"].casefold() for i in languages.get("items", [])}
    in_files = {i["label"].casefold(): i["label"] for i in languages.get("items", []) if i["status"] == "files_detected"}
    detected_keys = {t["key"] for t in frameworks.get("technologies", [])}

    declared_languages = declared(fields, "declared_languages") or []
    declared_frameworks = declared(fields, "declared_frameworks") or []
    lang_set: set[str] = set()
    tech_keys: set[str] = set()
    for prefer, listed in (("language", declared_languages), ("technology", declared_frameworks)):
        for item in listed:
            resolved = _resolve(item, prefer)
            if resolved is None:
                findings.append(_finding("declared_not_comparable", item))
            elif resolved[0] == "language":
                lang_set.add(resolved[1].casefold())
                if lang_complete and resolved[1].casefold() not in present:
                    findings.append(_finding("declared_language_not_detected", item))
            else:
                tech_keys.add(resolved[1])
                if fw_complete and resolved[1] not in detected_keys:
                    findings.append(_finding("declared_framework_not_detected", item))
    if lang_set and lang_complete:
        findings += [_finding("detected_language_not_declared", label) for folded, label in in_files.items() if folded not in lang_set]
    if (tech_keys or declared_frameworks) and fw_complete:
        findings += [_finding("detected_technology_not_declared", key) for key in sorted(detected_keys)
                     if key not in tech_keys and key not in ubiquitous]

    enabled = declared(fields, "openspec_enabled")
    state = _items(markers, "openspec_directory").get("state")
    if enabled is True and mark_complete and state == "not_detected":
        findings.append(_finding("declared_openspec_not_detected", "openspec"))
    if enabled is False and state == "detected":
        findings.append(_finding("openspec_detected_but_declared_disabled", "openspec"))

    agent = _items(markers, "agent_instructions")
    stored = {p["path"].replace("\\", "/").casefold() for p in agent.get("paths", [])}
    all_stored = agent.get("more", 0) == 0
    for path in declared(fields, "agent_instruction_paths"):
        if mark_complete and all_stored and path.replace("\\", "/").casefold() not in stored:
            findings.append(_finding("declared_agent_instruction_not_detected", path))
    return sorted(findings, key=lambda f: (f["code"], f["subject"]))


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def profile_context(connection: sqlite3.Connection, project_id: str, *, now: Callable[[], datetime] = _utc_now) -> dict:
    """The context bundle of one stored project: its details, the differences per checkout, and the workflow."""
    if not isinstance(project_id, str) or not project_id:
        raise IndexStoreError(INVALID_INPUT, "project_id must be a non-empty string")
    bundle = query.get_project(connection, project_id, now=now)
    data = bundle["data"]
    values = {name: entry["value"] for name, entry in data["profile"]["declared"].items()}
    for checkout in data["checkouts"]:
        checkout["differences"] = differences(checkout, values)
    data["source"] = {"kind": "index", "generated_at": now().isoformat()}
    data["workflow"] = list(WORKFLOW)
    return bundle


class NotAProject(Exception):
    """The path is not a directory holding a recognized project. The message is fixed text, safe to show."""


def _same(a: Path, b: Path) -> bool:
    return os.path.normcase(str(a.resolve())) == os.path.normcase(str(b.resolve()))


def live_context(path: Path | str, *, now: Callable[[], datetime] = _utc_now) -> dict:
    """The context bundle of one repository from a live read-only scan, held in a temporary in-memory index.

    Nothing is written to the repository, to the real index, or anywhere on disk.
    """
    root = Path(path)
    if not root.is_dir():
        raise NotAProject("The path is not a directory.")
    run = discover_repositories(root.resolve())
    mine = tuple(c for c in run.repositories if c.outcome == ELIGIBLE and _same(c.path, root))
    if not mine:
        raise NotAProject("No project was recognized at this path. It needs a Git repository or a supported manifest at its root.")
    connection = open_memory_index()
    try:
        store_run(connection, enrich_run(replace(run, repositories=mine)), owner="profile-context", now=now)
        project_id = connection.execute("SELECT project_id FROM projects").fetchone()[0]
        bundle = profile_context(connection, project_id, now=now)
    finally:
        connection.close()
    bundle["data"]["project_id"] = None
    bundle["data"]["source"]["kind"] = "live_scan"
    return bundle
