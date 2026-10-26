#!/usr/bin/env python3
"""Smoke test: every team schema in this repository can drive a complete change.

For each team declared in ``openspec/config.yaml`` (``teams:``), this script creates a
scratch change with that team's schema, checks the recorded schema and the artifact
chain against the schema itself, resolves every artifact's instruction and template,
checks that every skill the schema names lives in the team's own skill home or in
``skills/shared``, fills every artifact from that schema's own templates, then runs
``openspec validate`` and ``openspec show --deltas-only``. All scratch changes are
removed afterwards.

Nothing about a specific team, schema, artifact, skill, or machine is hard-coded: the
teams come from the configuration, the artifact chains from each ``schema.yaml``, and
the skill homes from the ``skills/`` tree. Paths are resolved relative to this file, so
the script works from any clone on Linux, macOS, and Windows, and every file is read
and written as UTF-8 with LF newlines regardless of the platform default.

Standard library only, like ``scripts/verify_workflows.py``.

Usage:

    python3 scripts/smoke_team_schemas.py [--verbose]
"""

from __future__ import annotations

import atexit
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OPENSPEC_CONFIG = REPO_ROOT / "openspec" / "config.yaml"
CHANGES_DIR = REPO_ROOT / "openspec" / "changes"
SCHEMAS_DIR = REPO_ROOT / "openspec" / "schemas"
SKILLS_DIR = REPO_ROOT / "skills"

SCRATCH_PREFIX = "zz-smoke-"
ARTIFACT_ID_RE = re.compile(r"^  - id:\s*(\S+)\s*$", re.MULTILINE)
STATUS_ARTIFACT_RE = re.compile(r"^\s*\[[ x-]\]\s+(\S+)", re.MULTILINE)
PLACEHOLDER_RE = re.compile(r"\{\{([^{}]+)\}\}")

VERBOSE = False


# --------------------------------------------------------------------------- io


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    """Write UTF-8 with LF newlines on every platform."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def configure_stdout() -> None:
    """Never crash on a console that cannot encode a character."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass


# ------------------------------------------------------------------- openspec cli


def openspec_binary() -> str | None:
    """Resolve the CLI on PATH; on Windows this finds openspec.cmd via PATHEXT."""
    return shutil.which("openspec")


def cli(*args: str) -> subprocess.CompletedProcess:
    binary = openspec_binary()
    if binary is None:
        raise FileNotFoundError("the 'openspec' CLI is not on PATH")
    return subprocess.run(
        [binary, *args],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def json_payload(result: subprocess.CompletedProcess) -> dict:
    text = result.stdout or ""
    start = min(
        (index for index in (text.find("{"), text.find("[")) if index >= 0),
        default=-1,
    )
    if start < 0:
        raise ValueError(f"no JSON in CLI output: {(text or result.stderr).strip()[:200]}")
    return json.loads(text[start:])


# ------------------------------------------------------------------ repo reading


def parse_teams(path: Path) -> dict[str, dict[str, str]]:
    """Read the ``teams:`` block without a YAML dependency.

    Returns ``{team: {"schema": ..., "skills": ...}}`` for every team that maps to a
    schema. Only the two keys this script needs are read.
    """
    teams: dict[str, dict[str, str]] = {}
    in_teams = False
    current: str | None = None
    for raw in read_text(path).splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith(" "):
            in_teams = line.strip() == "teams:"
            current = None
            continue
        if not in_teams:
            continue
        indent = len(line) - len(line.lstrip(" "))
        body = line.strip()
        if indent == 2 and body.endswith(":"):
            current = body[:-1].strip()
            teams[current] = {}
        elif indent >= 4 and current and ":" in body:
            key, value = body.split(":", 1)
            key = key.strip()
            if key in ("schema", "skills"):
                teams[current][key] = value.strip().strip("'\"")
    return {team: values for team, values in teams.items() if values.get("schema")}


def schema_artifact_ids(schema: str) -> list[str]:
    text = read_text(SCHEMAS_DIR / schema / "schema.yaml")
    block = text.split("artifacts:", 1)[-1].split("\napply:", 1)[0]
    return ARTIFACT_ID_RE.findall(block)


def available_schemas() -> set[str]:
    return {path.parent.name for path in SCHEMAS_DIR.glob("*/schema.yaml")}


def skill_homes() -> dict[str, str]:
    """Skill name to the directory under ``skills/`` that homes it."""
    return {
        path.parent.name: path.parent.parent.name
        for path in SKILLS_DIR.glob("*/*/SKILL.md")
    }


def spine_artifacts(schemas: list[str]) -> set[str]:
    """Artifacts every schema has: the shared spine, whatever it is called."""
    chains = [set(schema_artifact_ids(schema)) for schema in schemas]
    return set.intersection(*chains) if chains else set()


def template(schema: str, artifact: str) -> str:
    return read_text(SCHEMAS_DIR / schema / "templates" / f"{artifact}.md")


# -------------------------------------------------------------- placeholder filling

FIXED = {
    "change-name": "smoke",
    "change-id": "zz-smoke",
    "capability-name": "capability-under-test",
    "short-description": "smoke test",
    "capability-or-behavior": "the capability",
    "requirement-name": "SMOKE-001 — The capability records a request",
    "another-requirement-name": "SMOKE-002 — The capability rejects an empty request",
    "requirement-reference": "SMOKE-001",
    "chosen-option": "Option A",
    "option-name": "Option",
    "specific, observable behavior": "record the request",
    "initial context or precondition": "a client is connected",
    "additional context, if needed": "the client is authenticated",
    "action or event occurs": "the client sends a request",
    "additional action, if needed": "the request is well formed",
    "expected observable outcome": "the request is recorded",
    "additional expected outcome, if needed": "the response reports success",
    "boundary condition or failure context": "the request is empty",
    "required behavior under that condition": "reject the request",
    "action or event": "the client sends a request",
    "expected outcome": "the request is recorded",
    "context": "a client is connected",
    "id": "PRJ-1",
    "name": "Example",
    "field": "value",
}

# Keys that must stay unique when a template repeats them.
UNIQUE = {"scenario-name", "context", "option-name", "requirement-name", "another-requirement-name"}


def generic_value(key: str) -> str:
    """A neutral, heading-safe value for a placeholder this script does not know."""
    words = re.sub(r"[^0-9A-Za-z]+", " ", key).strip()
    return words[:1].upper() + words[1:] if words else "value"


def fill_placeholders(text: str, change_id: str) -> str:
    """Replace every ``{{placeholder}}`` so the artifact validates as real content."""
    used: dict[str, int] = {}

    def replace(match: re.Match) -> str:
        key = match.group(1)
        used[key] = used.get(key, 0) + 1
        if key not in FIXED and key not in UNIQUE and key.startswith("requirement"):
            value = f"{change_id.upper()}-{used[key]:03d} — {generic_value(key)}"
        else:
            value = FIXED.get(key, generic_value(key))
        if key in UNIQUE and used[key] > 1:
            value = f"{value} {used[key]}"
        return value.replace("zz-smoke", change_id)

    filled = PLACEHOLDER_RE.sub(replace, text)
    leftover = sorted(set(PLACEHOLDER_RE.findall(filled)))
    if leftover:
        raise ValueError(f"unfilled placeholders: {leftover}")
    return filled


# ---------------------------------------------------------------------- cleanup

_SCRATCH: set[Path] = set()


def remove_scratch() -> None:
    for path in list(_SCRATCH):
        shutil.rmtree(path, ignore_errors=True)
        _SCRATCH.discard(path)


atexit.register(remove_scratch)


def remove_stale_scratch() -> list[str]:
    """Remove scratch changes left by an interrupted run; return what was removed."""
    stale = sorted(CHANGES_DIR.glob(f"{SCRATCH_PREFIX}*"))
    removed = [path.name for path in stale]
    for path in stale:
        shutil.rmtree(path, ignore_errors=True)
    return removed


# ------------------------------------------------------------------------ checks


def smoke_team(team: str, definition: dict[str, str], spine: set[str]) -> list[str]:
    """Run the full smoke test for one team; return a list of failures."""
    failures: list[str] = []
    schema = definition["schema"]
    change_id = f"{SCRATCH_PREFIX}{team}"
    change_dir = CHANGES_DIR / change_id
    _SCRATCH.add(change_dir)

    def note(line: str) -> None:
        if VERBOSE:
            print(f"   {line}")

    print(f"== team '{team}' (schema '{schema}')")

    created = cli("new", "change", change_id, "--schema", schema)
    if created.returncode != 0:
        detail = (created.stdout + created.stderr).strip().splitlines()
        print(f"   FAIL create: {detail[-1] if detail else 'no output'}")
        return [f"team '{team}': creating a change failed"]

    metadata = change_dir / ".openspec.yaml"
    recorded = re.search(r"^schema:\s*(\S+)", read_text(metadata), re.MULTILINE)
    recorded = recorded.group(1) if recorded else ""
    print(f"   recorded schema: {recorded or '?'}")
    if recorded != schema:
        failures.append(f"team '{team}': recorded schema '{recorded}' != '{schema}'")

    expected_chain = schema_artifact_ids(schema)
    reported_chain = STATUS_ARTIFACT_RE.findall(cli("status", "--change", change_id).stdout)
    print(f"   chain: {' -> '.join(reported_chain)}")
    if reported_chain != expected_chain:
        failures.append(f"team '{team}': chain {reported_chain} != {expected_chain}")

    team_artifacts = [artifact for artifact in expected_chain if artifact not in spine]
    if len(team_artifacts) != 1:
        failures.append(
            f"team '{team}': expected one team-specific artifact, found {team_artifacts}"
        )
    team_artifact = team_artifacts[0] if team_artifacts else None
    print(f"   team artifact: {team_artifact or 'MISSING'}")

    homes = skill_homes()
    schema_text = read_text(SCHEMAS_DIR / schema / "schema.yaml")
    named = sorted(name for name in homes if name in schema_text)
    own_home = Path(definition.get("skills", f"skills/{schema}")).name
    allowed = {"shared", own_home}
    out_of_home = sorted(name for name in named if homes[name] not in allowed)
    own = [name for name in named if homes[name] == own_home]
    print(f"   skills named: {len(named)} ({len(own)} from skills/{own_home}/, rest shared)")
    if out_of_home:
        print(f"   FAIL out-of-home skills: {out_of_home}")
        failures.append(f"team '{team}': skills outside '{own_home}' or shared: {out_of_home}")

    instructions_ok = True
    for artifact in expected_chain:
        result = cli("instructions", artifact, "--change", change_id, "--json")
        if result.returncode != 0:
            print(f"   FAIL instructions for '{artifact}': {result.stderr.strip()[:160]}")
            instructions_ok = False
            continue
        if not json_payload(result).get("instruction", "").strip():
            print(f"   FAIL empty instruction for '{artifact}'")
            instructions_ok = False
        template_path = SCHEMAS_DIR / schema / "templates" / f"{artifact}.md"
        if not template_path.exists() or not read_text(template_path).strip():
            print(f"   FAIL missing or empty template for '{artifact}'")
            instructions_ok = False
    print(f"   instructions and templates resolve: {instructions_ok}")
    if not instructions_ok:
        failures.append(f"team '{team}': an instruction or template did not resolve")

    if team_artifact:
        result = cli("instructions", team_artifact, "--change", change_id, "--json")
        instruction = json_payload(result).get("instruction", "") if result.returncode == 0 else ""
        routed = [name for name in named if name in instruction]
        own_routed = [name for name in routed if homes[name] == own_home]
        print(f"   '{team_artifact}' routes to {len(routed)} skills, own-home: {own_routed or 'NONE'}")
        if not own_routed:
            failures.append(f"team '{team}': '{team_artifact}' names no skill from skills/{own_home}/")

    try:
        for artifact in expected_chain:
            write_text(change_dir / f"{artifact}.md", fill_placeholders(template(schema, artifact), change_id))
        spec_path = change_dir / "specs" / "capability-under-test" / "spec.md"
        write_text(spec_path, fill_placeholders(template(schema, "specs"), change_id))
        (change_dir / "specs.md").unlink(missing_ok=True)
    except ValueError as error:
        print(f"   FAIL fill: {error}")
        failures.append(f"team '{team}': {error}")
        return failures

    validated = cli("validate", change_id)
    print(f"   openspec validate: {'PASS' if validated.returncode == 0 else 'FAIL'}")
    if validated.returncode != 0:
        print("   ", (validated.stdout + validated.stderr).strip()[:400])
        failures.append(f"team '{team}': validation failed")

    shown = cli("show", change_id, "--json", "--deltas-only")
    if shown.returncode != 0:
        print(f"   FAIL show: {(shown.stdout + shown.stderr).strip()[:200]}")
        failures.append(f"team '{team}': show --deltas-only failed")
    else:
        deltas = json_payload(shown).get("deltas", [])
        names = [delta.get("requirement", {}).get("name", "?") for delta in deltas]
        print(f"   deltas parsed: {len(deltas)} -> {names}")
        if not deltas or any("{{" in name for name in names):
            failures.append(f"team '{team}': unexpected deltas {names}")

    note("files: " + ", ".join(sorted(path.name for path in change_dir.glob("*.md"))))
    print()
    return failures


def main(argv: list[str]) -> int:
    global VERBOSE
    VERBOSE = "--verbose" in argv or "-v" in argv

    configure_stdout()
    print(f"repository: {REPO_ROOT}")
    print(f"openspec CLI: {openspec_binary() or 'NOT FOUND'}")
    if openspec_binary() is None:
        print("\nRESULT: FAIL — the 'openspec' CLI is not on PATH")
        return 1
    if not OPENSPEC_CONFIG.is_file():
        print(f"\nRESULT: FAIL — missing {OPENSPEC_CONFIG.relative_to(REPO_ROOT)}")
        return 1

    teams = parse_teams(OPENSPEC_CONFIG)
    if not teams:
        print("\nRESULT: FAIL — 'teams:' in openspec/config.yaml declares no schema")
        return 1

    schemas = available_schemas()
    missing = sorted({definition["schema"] for definition in teams.values()} - schemas)
    if missing:
        print(f"\nRESULT: FAIL — team schemas missing from openspec/schemas: {missing}")
        return 1

    spine = spine_artifacts(sorted(schemas))
    print(f"spine artifacts: {', '.join(sorted(spine)) or 'none'}")
    summary = ", ".join(f"{team}->{definition['schema']}" for team, definition in teams.items())
    print(f"teams: {summary}")
    print()

    stale = remove_stale_scratch()
    if stale:
        print(f"removed stale scratch changes: {stale}\n")

    failures: list[str] = []
    try:
        for team, definition in teams.items():
            failures.extend(smoke_team(team, definition, spine))
    except FileNotFoundError as error:
        failures.append(str(error))
    finally:
        remove_scratch()

    leftover = sorted(path.name for path in CHANGES_DIR.glob(f"{SCRATCH_PREFIX}*"))
    print(f"scratch changes left behind: {leftover or 'none'}")
    print()
    if failures or leftover:
        print("RESULT: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        if leftover:
            print(f"  - leftover scratch changes: {leftover}")
        return 1

    print(f"RESULT: PASS — {len(teams)} team schema(s) each drive a complete, valid change")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
