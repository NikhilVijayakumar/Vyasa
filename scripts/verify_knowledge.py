#!/usr/bin/env python3
"""Verify the OKF knowledge bundle against its profile.

The bundle lives in ``<repo>/knowledge/`` and follows Open Knowledge Format
v0.2. OKF itself requires only a ``type`` per concept; ``knowledge/profile.json``
adds this repository's stricter rules, which this script enforces:

- every concept has the profile's required frontmatter fields, stays within ``max_lines``, a known
  ``type`` stored in that type's folder, a valid ``status``, and a
  ``generated`` actor and timestamp;
- every concept is listed in its folder's ``index.md`` and every folder in
  its parent's index; the root index declares ``okf_version``;
- ``log.md`` date headings are ``YYYY-MM-DD``;
- independence: links and ``sources`` may point only inside the bundle or to
  external URLs, and the profile's forbidden paths never appear. Knowledge
  never depends on requirements, changes, or implementation.

A concept whose ``stale_after`` date has passed is a warning. Broken links inside the bundle are warnings, not errors: OKF treats them as
not-yet-written knowledge.

Usage::

    python3 scripts/verify_knowledge.py            # verify knowledge/
    python3 scripts/verify_knowledge.py <bundle>   # verify another bundle
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RESERVED = {"index.md", "log.md"}
ISO_DATETIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:\d{2})$")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
TOP_KEY = re.compile(r"^([A-Za-z_][\w-]*):\s*(.*)$")


def split_frontmatter(text: str) -> tuple[dict[str, str], str] | None:
    """Return (top-level key -> raw value, body), or None without frontmatter.

    ponytail: minimal YAML reader for top-level keys only (stdlib, no PyYAML);
    nested values stay raw text and are matched with regexes below.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = lines.index("---", 1)
    except ValueError:
        return None
    fields: dict[str, str] = {}
    key = None
    for line in lines[1:end]:
        match = TOP_KEY.match(line)
        if match:
            key = match.group(1)
            fields[key] = match.group(2).strip()
        elif key and line.strip():
            fields[key] += "\n" + line
    return fields, "\n".join(lines[end + 1 :])


def unquote(value: str) -> str:
    return value.strip().strip("\"'")


def link_targets(text: str) -> list[str]:
    return [target for target in LINK.findall(text) if not target.startswith("[^")]


def check_path(bundle: Path, origin: Path, target: str, what: str, errors: list[str], warnings: list[str]) -> None:
    if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
        return  # external URL, mailto:, or in-page anchor
    target = target.split("#", 1)[0]
    if not target:
        return
    resolved = (bundle / target.lstrip("/")) if target.startswith("/") else (origin.parent / target)
    resolved = resolved.resolve()
    rel = origin.relative_to(bundle)
    if bundle != resolved and bundle not in resolved.parents:
        errors.append(f"{rel}: {what} '{target}' points outside the knowledge bundle")
    elif not resolved.exists():
        warnings.append(f"{rel}: {what} '{target}' does not exist yet")


def check_concept(bundle: Path, path: Path, profile: dict, errors: list[str], warnings: list[str], now: datetime) -> None:
    rel = path.relative_to(bundle)
    parsed = split_frontmatter(path.read_text(encoding="utf-8"))
    if parsed is None:
        errors.append(f"{rel}: missing YAML frontmatter")
        return
    fields, body = parsed

    for name in profile["required_fields"]:
        if not unquote(fields.get(name, "")):
            errors.append(f"{rel}: missing required field '{name}'")

    limit = profile.get("max_lines")
    if limit and len(path.read_text(encoding="utf-8").splitlines()) > limit:
        errors.append(f"{rel}: longer than {limit} lines; split it into parts")

    stale_after = unquote(fields.get("stale_after", ""))
    if stale_after:
        try:
            if now >= datetime.fromisoformat(stale_after.replace("Z", "+00:00")):
                warnings.append(f"{rel}: stale since {stale_after}; review it or move stale_after")
        except ValueError:
            errors.append(f"{rel}: stale_after '{stale_after}' is not an ISO 8601 datetime with offset")

    kind = unquote(fields.get("type", ""))
    folder = profile["types"].get(kind)
    if kind and folder is None:
        errors.append(f"{rel}: type '{kind}' is not in the profile ({', '.join(profile['types'])})")
    elif folder and rel.parts[0] != folder:
        errors.append(f"{rel}: type '{kind}' belongs in '{folder}/'")

    status = unquote(fields.get("status", ""))
    if status and status not in profile["status_values"]:
        errors.append(f"{rel}: status '{status}' is not one of {profile['status_values']}")

    actor = re.compile(profile["actor_pattern"])
    for key in ("generated", "verified"):
        raw = fields.get(key, "")
        for by in re.findall(r"by:\s*([^,}\s]+)", raw):
            if not actor.match(unquote(by)):
                errors.append(f"{rel}: {key}.by '{by}' does not follow the actor convention")
        for at in re.findall(r"at:\s*([^,}\s]+)", raw):
            if not ISO_DATETIME.match(unquote(at)):
                errors.append(f"{rel}: {key}.at '{at}' is not an ISO 8601 datetime with offset")
    if fields.get("generated") and "by:" not in fields["generated"]:
        errors.append(f"{rel}: generated must record 'by'")

    resources = re.findall(r"resource:\s*(\S+)", fields.get("sources", ""))
    if fields.get("resource"):
        resources.append(fields["resource"])
    for resource in map(unquote, resources):
        if resource.startswith(("/", ".")) or re.match(r"^[a-z][a-z0-9+.-]*:", resource):
            check_path(bundle, path, resource, "source", errors, warnings)
        # anything else is an OKF scope descriptor, not a path

    for target in link_targets(body):
        check_path(bundle, path, target, "link", errors, warnings)


def check_indexes(bundle: Path, profile: dict, errors: list[str], warnings: list[str]) -> None:
    for directory in [bundle, *sorted(p for p in bundle.rglob("*") if p.is_dir())]:
        entries = [p for p in directory.iterdir() if (p.suffix == ".md" and p.name not in RESERVED) or (p.is_dir() and any(p.rglob("*.md")))]
        index = directory / "index.md"
        rel = index.relative_to(bundle)
        if not index.is_file():
            if entries:
                errors.append(f"{rel}: missing (directory has concepts)")
            continue
        text = index.read_text(encoding="utf-8")
        parsed = split_frontmatter(text)
        if directory == bundle:
            declared = unquote(parsed[0].get("okf_version", "")) if parsed else ""
            if declared != profile["okf_version"]:
                errors.append(f"{rel}: root index must declare okf_version: \"{profile['okf_version']}\"")
        elif parsed is not None:
            errors.append(f"{rel}: only the root index may carry frontmatter")
        targets = {t.split("#", 1)[0].removeprefix("./") for t in link_targets(text)}
        for entry in entries:
            name = entry.name + ("/" if entry.is_dir() else "")
            if name not in targets and entry.name not in targets:
                errors.append(f"{rel}: does not list '{name}'")
        for target in link_targets(text):
            check_path(bundle, index, target, "link", errors, warnings)


def check_logs(bundle: Path, errors: list[str]) -> None:
    for log in bundle.rglob("log.md"):
        for line in log.read_text(encoding="utf-8").splitlines():
            if line.startswith("## ") and not re.match(r"^## \d{4}-\d{2}-\d{2}\s*$", line):
                errors.append(f"{log.relative_to(bundle)}: date heading '{line}' is not YYYY-MM-DD")


def verify(bundle: Path, now: datetime | None = None) -> tuple[list[str], list[str]]:
    now = now or datetime.now(timezone.utc)
    bundle = bundle.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    profile_path = bundle / "profile.json"
    if not profile_path.is_file():
        return [f"{profile_path}: missing"], warnings
    profile = json.loads(profile_path.read_text(encoding="utf-8"))

    for path in sorted(bundle.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for forbidden in profile["forbidden_text"]:
            if forbidden in text:
                errors.append(f"{path.relative_to(bundle)}: mentions '{forbidden}' (knowledge must not depend on it)")
        if path.name not in RESERVED:
            check_concept(bundle, path, profile, errors, warnings, now)
    check_indexes(bundle, profile, errors, warnings)
    check_logs(bundle, errors)
    return errors, warnings


def main() -> int:
    bundle = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "knowledge"
    errors, warnings = verify(bundle)
    for warning in warnings:
        print(f"WARN  {warning}")
    for error in errors:
        print(f"FAIL  {error}")
    concepts = sum(1 for p in bundle.rglob("*.md") if p.name not in RESERVED)
    print(f"knowledge: {concepts} concept(s), {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
