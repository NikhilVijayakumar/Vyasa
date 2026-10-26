#!/usr/bin/env python3
"""Verify that this repository matches the contract the OpenSpec CLI parses.

Checks, in order:

1. Every schema in ``openspec/schemas/`` passes ``openspec schema validate``.
2. For every schema: a scratch change reports that schema's artifact chain, every
   artifact of the chain resolves to an instruction and a template, and a
   specification written from that schema's own template validates and parses as
   change deltas.
3. Every change in ``openspec/changes/`` validates, parses, and reports exactly
   as many deltas as it has requirements.
4. Every skill reference in every agent skills directory resolves.

Usage:
    python3 scripts/verify_workflows.py

Exit status is 0 when every check passes and 1 when any check fails. Standard
library only, like ``scripts/sync_skills.py``. Paths are resolved relative to this
file and every file is read as UTF-8, so the script runs from any clone on Linux,
macOS, and Windows. ``scripts/smoke_team_schemas.py`` exercises each team schema end
to end; this script checks the contract every change and schema must satisfy.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHANGES_DIR = REPO_ROOT / "openspec" / "changes"
SCHEMAS_DIR = REPO_ROOT / "openspec" / "schemas"
SCRATCH_ID = "zz-verify-scratch"
SCRATCH_PREFIX = "zz-verify-"

def read_text(path: Path) -> str:
    """Read UTF-8 on every platform; the templates and specs contain non-ASCII text."""
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    """Write UTF-8 with LF newlines, so line endings do not depend on the platform."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def openspec_binary() -> str | None:
    """Resolve the CLI on PATH; on Windows this finds openspec.cmd via PATHEXT."""
    return shutil.which("openspec")


def configure_stdout() -> None:
    """Never crash on a console that cannot encode a character."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass


ARTIFACT_ID_RE = re.compile(r"^  - id:\s*(\S+)\s*$", re.MULTILINE)
REQUIREMENT_RE = re.compile(r"^###\s+Requirement:", re.MULTILINE)
STATUS_ARTIFACT_RE = re.compile(r"^\s*\[[ x-]\]\s+(\S+)", re.MULTILINE)


class Report:
    """Collects check results and prints one line per check."""

    def __init__(self) -> None:
        self.failures = 0

    def ok(self, message: str) -> None:
        print(f"PASS  {message}")

    def fail(self, message: str, detail: str = "") -> None:
        self.failures += 1
        print(f"FAIL  {message}")
        for line in detail.strip().splitlines():
            print(f"      {line}")

    def run(self, message: str, command: list[str]) -> subprocess.CompletedProcess:
        result = subprocess.run(
            [openspec_binary() or command[0], *command[1:]],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode == 0:
            self.ok(message)
        else:
            self.fail(message, result.stdout + result.stderr)
        return result

    def check(self, message: str, condition: bool, detail: str = "") -> bool:
        if condition:
            self.ok(message)
        else:
            self.fail(message, detail)
        return condition


def cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [openspec_binary() or "openspec", *args],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def schema_artifact_ids(schema_file: Path) -> list[str]:
    """Artifact ids of a schema, in order, read without a YAML dependency."""
    text = read_text(schema_file)
    artifacts_block = text.split("artifacts:", 1)[-1].split("\napply:", 1)[0]
    return ARTIFACT_ID_RE.findall(artifacts_block)


def scratch_change_dir() -> Path:
    return CHANGES_DIR / SCRATCH_ID


def remove_scratch_changes() -> None:
    for path in CHANGES_DIR.glob(f"{SCRATCH_PREFIX}*"):
        if path.is_dir():
            shutil.rmtree(path)


def check_schemas(report: Report) -> list[str]:
    names = sorted(path.parent.name for path in SCHEMAS_DIR.glob("*/schema.yaml"))
    for name in names:
        report.run(f"schema '{name}' validates", ["openspec", "schema", "validate", name])
    return names


def check_scratch_change(report: Report, schema: str) -> None:
    """Create a scratch change for a schema and exercise its whole chain."""
    change_id = f"{SCRATCH_PREFIX}{schema}"
    created = cli("new", "change", change_id, "--schema", schema)
    if created.returncode != 0:
        report.fail(
            f"scratch change for schema '{schema}' is created",
            created.stdout + created.stderr,
        )
        return

    try:
        expected = schema_artifact_ids(SCHEMAS_DIR / schema / "schema.yaml")
        status = cli("status", "--change", change_id)
        reported = STATUS_ARTIFACT_RE.findall(status.stdout)
        report.check(
            f"schema '{schema}' reports its artifact chain ({', '.join(expected)})",
            reported == expected,
            f"expected {expected}\nreported {reported}\n{status.stdout}",
        )

        for artifact in expected:
            instructions = cli("instructions", artifact, "--change", change_id, "--json")
            if instructions.returncode != 0:
                report.fail(
                    f"artifact '{artifact}' of schema '{schema}' resolves",
                    instructions.stdout + instructions.stderr,
                )
                continue
            try:
                payload = json.loads(instructions.stdout[instructions.stdout.find("{") :])
            except json.JSONDecodeError as error:
                report.fail(f"artifact '{artifact}' of schema '{schema}' resolves", str(error))
                continue
            report.check(
                f"artifact '{artifact}' of schema '{schema}' has an instruction and a template",
                bool(payload.get("instruction")) and bool(payload.get("template")),
                "instruction or template is empty",
            )

        template = SCHEMAS_DIR / schema / "templates" / "specs.md"
        change_dir = CHANGES_DIR / change_id
        write_text(
            change_dir / "proposal.md",
            read_text(SCHEMAS_DIR / schema / "templates" / "proposal.md"),
        )
        spec_dir = change_dir / "specs" / "template-shape"
        spec_dir.mkdir(parents=True, exist_ok=True)
        write_text(spec_dir / "spec.md", read_text(template))

        validated = cli("validate", change_id)
        report.check(
            f"a specification written from the '{schema}' template validates",
            validated.returncode == 0,
            validated.stdout + validated.stderr,
        )

        shown = cli("show", change_id, "--json", "--deltas-only")
        if shown.returncode != 0:
            report.fail(
                f"a specification written from the '{schema}' template parses as deltas",
                shown.stdout + shown.stderr,
            )
            return
        payload = json.loads(shown.stdout[shown.stdout.find("{") :])
        deltas = payload.get("deltas", [])
        template_requirements = REQUIREMENT_RE.findall(read_text(template))
        report.check(
            f"a specification written from the '{schema}' template yields "
            f"{len(template_requirements)} delta(s)",
            len(deltas) == len(template_requirements),
            f"template declares {len(template_requirements)} requirement(s), "
            f"the CLI read {len(deltas)}",
        )
    finally:
        shutil.rmtree(scratch_change_dir(), ignore_errors=True)


def check_changes(report: Report) -> None:
    for change_dir in sorted(path for path in CHANGES_DIR.iterdir() if path.is_dir()):
        if change_dir.name == "archive" or change_dir.name.startswith(SCRATCH_PREFIX):
            continue
        change_id = change_dir.name

        validated = cli("validate", change_id)
        report.check(
            f"change '{change_id}' validates",
            validated.returncode == 0,
            validated.stdout + validated.stderr,
        )

        shown = cli("show", change_id, "--json", "--deltas-only")
        if shown.returncode != 0:
            report.fail(
                f"change '{change_id}' parses",
                shown.stdout + shown.stderr,
            )
            continue
        payload = json.loads(shown.stdout[shown.stdout.find("{") :])
        deltas = payload.get("deltas", [])

        declared = 0
        for spec_file in change_dir.glob("specs/**/spec.md"):
            declared += len(REQUIREMENT_RE.findall(read_text(spec_file)))
        report.check(
            f"change '{change_id}' parses {len(deltas)} delta(s) matching its requirements",
            len(deltas) == declared,
            f"specification files declare {declared} requirement(s), the CLI read {len(deltas)}",
        )


def check_skill_references(report: Report) -> None:
    script = REPO_ROOT / "scripts" / "sync_skills.py"
    result = subprocess.run(
        [sys.executable, str(script), "--verify"], cwd=REPO_ROOT, capture_output=True, text=True
    )
    report.check(
        "every skill reference in every agent skills directory resolves",
        result.returncode == 0,
        result.stdout + result.stderr,
    )


def check_knowledge(report: Report) -> None:
    script = REPO_ROOT / "scripts" / "verify_knowledge.py"
    result = subprocess.run(
        [sys.executable, str(script)], cwd=REPO_ROOT, capture_output=True, text=True
    )
    report.check(
        "the knowledge bundle conforms to knowledge/profile.json",
        result.returncode == 0,
        result.stdout + result.stderr,
    )


def skill_homes() -> dict[str, str]:
    """Skill name to its home category, read from the skill homes on disk."""
    return {
        path.parent.name: path.parent.parent.name
        for path in (REPO_ROOT / "skills").glob("*/*/SKILL.md")
    }


def mentioned_skills(text: str, homes: dict[str, str]) -> list[str]:
    return sorted(
        name
        for name in homes
        if re.search(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])", text)
    )


def team_schema_homes() -> dict[str, str]:
    """Map each schema named by ``teams:`` to that team's skill-home directory name.

    Read from the configuration rather than assumed, so a schema that no team owns
    (the shared spine) is treated as shared-only without naming it here.
    """
    homes: dict[str, str] = {}
    team: str | None = None
    in_teams = False
    for raw in read_text(REPO_ROOT / "openspec" / "config.yaml").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith(" "):
            in_teams = line.strip() == "teams:"
            team = None
            continue
        if not in_teams:
            continue
        indent = len(line) - len(line.lstrip(" "))
        body = line.strip()
        if indent == 2 and body.endswith(":"):
            team = body[:-1].strip()
        elif indent >= 4 and team and body.startswith(("schema:", "skills:")):
            key, value = body.split(":", 1)
            value = value.strip().strip("'\"")
            if key.strip() == "schema":
                homes.setdefault(value, "")
            elif key.strip() == "skills" and value:
                schema = next((name for name, home in homes.items() if home == ""), None)
                if schema is not None:
                    homes[schema] = Path(value).name
    return {schema: home for schema, home in homes.items() if home}


def check_skill_scoping(report: Report) -> None:
    """The shared core may only name shared skills; a team schema may also name its own."""
    homes = skill_homes()
    owned = team_schema_homes()
    scoping = {"openspec/config.yaml": {"shared"}}
    for schema_dir in sorted(SCHEMAS_DIR.iterdir()):
        if not (schema_dir / "schema.yaml").exists():
            continue
        home = schema_dir.name
        allowed = {"shared", owned[home]} if home in owned else {"shared"}
        scoping[f"openspec/schemas/{home}/schema.yaml"] = allowed
    for relative, allowed in scoping.items():
        path = REPO_ROOT / relative
        if not path.exists():
            report.fail(f"'{relative}' exists", "file is missing")
            continue
        named = mentioned_skills(read_text(path), homes)
        offending = sorted({name for name in named if homes[name] not in allowed})
        report.check(
            f"'{relative}' names only skills homed in {', '.join(sorted(allowed))}",
            not offending,
            f"out-of-home skills: {offending}",
        )


def available_schemas() -> list[str]:
    result = cli("schemas", "--json")
    if result.returncode != 0:
        return []
    payload = json.loads(result.stdout[result.stdout.find("[") :])
    return [entry["name"] for entry in payload]


def default_schema() -> str:
    """The project default schema declared by `schema:` in openspec/config.yaml."""
    match = re.search(
        r"^schema:\s*(\S+)\s*$", read_text(REPO_ROOT / "openspec" / "config.yaml"), re.MULTILINE
    )
    return match.group(1) if match else ""


def check_schema_resolution(report: Report) -> None:
    """The default schema and every change's schema must exist."""
    available = available_schemas()
    report.check(
        "the CLI reports the available schemas",
        bool(available),
        "openspec schemas --json returned nothing",
    )
    if not available:
        return

    default = default_schema()
    report.check(
        f"the configured default schema '{default}' resolves",
        default in available,
        f"available schemas: {', '.join(available)}",
    )

    for change_dir in sorted(path for path in CHANGES_DIR.iterdir() if path.is_dir()):
        if change_dir.name == "archive" or change_dir.name.startswith(SCRATCH_PREFIX):
            continue
        metadata = change_dir / ".openspec.yaml"
        pinned = ""
        if metadata.exists():
            match = re.search(r"^schema:\s*(\S+)\s*$", read_text(metadata), re.MULTILINE)
            pinned = match.group(1) if match else ""
        schema = pinned or default
        report.check(
            f"change '{change_dir.name}' uses an available schema ('{schema}')",
            schema in available,
            f"available schemas: {', '.join(available)}",
        )


def check_project_config(report: Report) -> None:
    """The CLI ignores a config it cannot parse, so the config must parse."""
    config = REPO_ROOT / "openspec" / "config.yaml"
    keys = re.findall(r"^([A-Za-z_][A-Za-z0-9_-]*):", read_text(config), re.MULTILINE)
    duplicates = sorted({key for key in keys if keys.count(key) > 1})
    report.check(
        "'openspec/config.yaml' declares no duplicate top-level key",
        not duplicates,
        f"duplicated keys: {duplicates}",
    )

    result = cli("context", "--json")
    warnings = [
        line
        for line in (result.stdout + result.stderr).splitlines()
        if "could not parse" in line
    ]
    report.check(
        "the OpenSpec CLI reads 'openspec/config.yaml' without a parse warning",
        not warnings,
        "\n".join(warnings),
    )


def main() -> int:
    configure_stdout()
    report = Report()
    if openspec_binary() is None:
        print("FAIL  the 'openspec' CLI is on PATH")
        print()
        return 1
    print(f"repository: {REPO_ROOT}")
    print()
    remove_scratch_changes()

    check_project_config(report)

    schemas = check_schemas(report)
    for schema in schemas:
        check_scratch_change(report, schema)

    check_changes(report)
    check_skill_references(report)
    check_knowledge(report)
    check_schema_resolution(report)
    check_skill_scoping(report)

    remove_scratch_changes()
    leftover = sorted(path.name for path in CHANGES_DIR.glob(f"{SCRATCH_PREFIX}*"))
    report.check("no scratch change is left behind", not leftover, f"leftover: {leftover}")

    print()
    if report.failures:
        print(f"{report.failures} check(s) failed")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
