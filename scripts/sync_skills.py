#!/usr/bin/env python3
"""Sync shared skills into each coding agent's skills directory as references.

The single source of truth is ``<repo>/skills/<category>/<skill>/``. Every
agent, however, reads skills from its own directory, so this script creates
one directory link per skill inside each agent directory, pointing back at
the skill's home folder. Edit a skill once and every agent sees the change.

Skill homes are grouped by team scope::

    skills/shared      lifecycle spine and cross-cutting quality skills
    skills/backend     scanner, MCP contract, data-ownership, SQLite, phase-gate skills

Agent directories stay **flat**: one link per skill name, whatever its
category. Skill discovery expects ``<skills-dir>/<name>/SKILL.md``, so
nesting skills under their category inside the agent directory would hide
them from the agent.

Targets (override with --agents):

    opencode     .opencode/skills      OpenCode
    antigravity  .agents/skills        Antigravity default, also the open
                                       SKILL.md standard read by Codex, Gemini
                                       CLI and GitHub Copilot
    claude       .claude/skills        Claude Code
    github       .github/skills        GitHub Copilot
    codex        .codex/skills         Codex (legacy path)

Usage::

    python3 scripts/sync_skills.py            # create/refresh references
    python3 scripts/sync_skills.py --verify   # check every reference resolves
    python3 scripts/sync_skills.py --prune    # drop references to deleted skills
    python3 scripts/sync_skills.py --dry-run  # show what would change
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO / "skills"

# Category directories in the order they are reported; any other category
# directory found on disk is reported after these, alphabetically.
CATEGORY_ORDER = ("shared", "frontend", "backend", "qa")

AGENT_DIRS = {
    "opencode": ".opencode/skills",
    "antigravity": ".agents/skills",
    "claude": ".claude/skills",
    "github": ".github/skills",
    "codex": ".codex/skills",
}

SCOPE_PREFIXES = {
    "backend": "backend-",
    "frontend": "frontend-",
    "fullstack": "fullstack-",
}
SHARED_PREFIX = "shared-"
SUPPORTED_SCOPES = {"shared", "qa", *SCOPE_PREFIXES}


def validate_skills(skills: list[Path]) -> list[str]:
    """Validate each skill's minimal frontmatter contract before any sync."""
    errors: list[str] = []

    for skill in skills:
        path = skill / "SKILL.md"
        if not path.is_file():
            errors.append(f"{skill.name}: missing SKILL.md")
            continue

        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            errors.append(f"{skill.name}: cannot read SKILL.md ({exc})")
            continue

        if not lines or lines[0] != "---":
            errors.append(f"{skill.name}: frontmatter must start with ---")
            continue
        try:
            end = lines.index("---", 1)
        except ValueError:
            errors.append(f"{skill.name}: frontmatter is missing its closing ---")
            continue

        header = lines[1:end]
        names = [
            match.group(1).strip().strip("\"'")
            for line in header
            if (match := re.match(r"^name:\s*(.+?)\s*$", line))
        ]
        if len(names) != 1:
            errors.append(f"{skill.name}: frontmatter must define exactly one name")
            continue
        name = names[0]
        if name != skill.name:
            errors.append(
                f"{skill.name}: frontmatter name {name!r} must match the directory name"
            )

        descriptions = [
            (index, match.group(1).strip())
            for index, line in enumerate(header)
            if (match := re.match(r"^description:\s*(.*?)\s*$", line))
        ]
        if len(descriptions) != 1:
            errors.append(f"{skill.name}: frontmatter must define exactly one description")
            description = ""
        else:
            desc_index, first_line = descriptions[0]
            if first_line in {">", ">-", ">+", "|", "|-", "|+"}:
                description_lines: list[str] = []
                for line in header[desc_index + 1 :]:
                    if line.strip() and not line[0].isspace():
                        break
                    description_lines.append(line.strip())
                description = " ".join(description_lines)
            else:
                description = first_line.strip("\"'")
            if not description:
                errors.append(f"{skill.name}: description must not be empty")

        metadata_indices = [
            index for index, line in enumerate(header) if re.match(r"^metadata:\s*$", line)
        ]
        categorized = skill.parent.name in CATEGORY_ORDER
        if categorized and not any(re.match(r"^\s+scope:", line) for line in header):
            continue
        if len(metadata_indices) != 1:
            errors.append(
                f"{skill.name}: frontmatter must define exactly one metadata.scope"
            )
            continue

        metadata_index = metadata_indices[0]
        scope_values: list[str] = []
        for line in header[metadata_index + 1 :]:
            if line.strip() and not line[0].isspace():
                break
            match = re.match(r"^\s+scope:\s*([A-Za-z_-]+)\s*$", line)
            if match:
                scope_values.append(match.group(1))
        if len(scope_values) != 1:
            errors.append(f"{skill.name}: metadata must define exactly one scope")
            continue

        scope = scope_values[0]
        if scope not in SUPPORTED_SCOPES:
            errors.append(
                f"{skill.name}: unsupported scope {scope!r}; expected one of "
                f"{', '.join(sorted(SUPPORTED_SCOPES))}"
            )
            continue

        if categorized:
            if scope != skill.parent.name:
                errors.append(f"{skill.name}: declared scope {scope!r} conflicts with home {skill.parent.name!r}")
            continue

        if scope == "shared":
            if name.startswith((SHARED_PREFIX, *SCOPE_PREFIXES.values())):
                errors.append(f"{skill.name}: shared skills must use an unprefixed name")
        else:
            prefix = SCOPE_PREFIXES[scope]
            if not name.startswith(prefix) or len(name) == len(prefix):
                errors.append(
                    f"{skill.name}: scope {scope!r} requires the {prefix!r} name prefix"
                )

        normalized_description = description.lower()
        if scope == "backend" and not re.search(r"\bbackend\b", normalized_description):
            errors.append(f"{skill.name}: backend-scoped description must say backend")
        elif scope == "frontend" and not re.search(
            r"\bfront(?:end|-end)\b", normalized_description
        ):
            errors.append(f"{skill.name}: frontend-scoped description must say frontend")
        elif scope == "fullstack" and not (
            re.search(r"\bfull[- ]?stack\b", normalized_description)
            or (
                re.search(r"\bfrontend\b", normalized_description)
                and re.search(r"\bbackend\b", normalized_description)
            )
        ):
            errors.append(
                f"{skill.name}: fullstack-scoped description must identify full-stack "
                "or frontend and backend work"
            )

    return errors


def _is_link(path: Path) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction and is_junction())


def _is_serialized_reference(path: Path, target: Path) -> bool:
    """Recognize Git symlink stubs from Windows core.symlinks=false checkouts."""
    if not path.is_file() or path.is_symlink():
        return False
    try:
        value = path.read_text(encoding="utf-8").strip().replace("\\", "/")
    except (OSError, UnicodeError):
        return False
    return value == os.path.relpath(target, path.parent).replace("\\", "/")


def _exists(path: Path) -> bool:
    return os.path.lexists(path)


def _remove_link(path: Path) -> None:
    if path.is_symlink():
        path.unlink()
    else:
        os.rmdir(path)  # Windows junction: removes the link, not the target


def _junction(link: Path, target: Path) -> None:
    subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link.absolute()), str(target.absolute())],
        check=True,
        capture_output=True,
        text=True,
    )


def create_link(link: Path, target: Path, mode: str) -> str:
    if mode == "portable":
        link.write_text(os.path.relpath(target, link.parent).replace("\\", "/"), encoding="utf-8")
        return "portable Git reference (run sync to hydrate)"
    if mode == "copy":
        shutil.copytree(target, link)
        return "copy"
    if mode == "junction":
        _junction(link, target)
        return "junction"
    rel = os.path.relpath(target, link.parent)
    try:
        os.symlink(rel, link, target_is_directory=True)
        return f"symlink -> {rel}"
    except OSError:
        if mode == "symlink" or os.name != "nt":
            raise
        _junction(link, target)  # symlink privilege unavailable; junction fallback
        return "junction (auto fallback)"


def _is_skill_dir(path: Path) -> bool:
    return path.is_dir() and (path / "SKILL.md").is_file()


def discover_skills() -> tuple[dict[str, list[Path]], list[Path]]:
    """Map category directory to its skill folders.

    Returns the mapping and any legacy flat skill folder found directly under
    ``skills/`` (a skill without a category home).
    """
    categories: dict[str, list[Path]] = {}
    legacy: list[Path] = []
    if not SKILLS_ROOT.is_dir():
        return categories, legacy

    for entry in sorted(SKILLS_ROOT.iterdir(), key=lambda p: p.name.lower()):
        if not entry.is_dir():
            continue
        if _is_skill_dir(entry):
            legacy.append(entry)
            continue
        skills = sorted((p for p in entry.iterdir() if _is_skill_dir(p)), key=lambda p: p.name.lower())
        if skills:
            categories[entry.name] = skills

    ordered: dict[str, list[Path]] = {}
    for name in CATEGORY_ORDER:
        if name in categories:
            ordered[name] = categories.pop(name)
    for name in sorted(categories):
        ordered[name] = categories[name]
    return ordered, legacy


def find_collisions(categories: dict[str, list[Path]]) -> dict[str, list[str]]:
    """Skill names claimed by more than one category (cannot be linked flat)."""
    homes: dict[str, list[str]] = {}
    for category, skills in categories.items():
        for skill in skills:
            homes.setdefault(skill.name, []).append(category)
    return {name: cats for name, cats in homes.items() if len(cats) > 1}


def sync_agent(name: str, rel: str, skills: list[Path], args) -> list[str]:
    agent_dir = REPO / rel
    log: list[str] = []
    if not args.dry_run:
        agent_dir.mkdir(parents=True, exist_ok=True)

    wanted = {s.name for s in skills}
    for skill in skills:
        link = agent_dir / skill.name
        state = "missing" if not _exists(link) else ("link" if _is_link(link) else "stub" if _is_serialized_reference(link, skill) else "dir" if link.is_dir() else "file")
        if state == "link" and os.path.realpath(link) == os.path.realpath(skill) and args.mode != "portable":
            log.append(f"  = {name}: {skill.name} (already linked)")
            continue
        if state in ("link", "missing", "stub") or (state == "dir" and args.force):
            if _exists(link):
                if args.dry_run:
                    log.append(f"  ~ {name}: would replace {skill.name} ({state})")
                    continue
                link.unlink() if state == "stub" else _remove_link(link) if state == "link" else shutil.rmtree(link)
            else:
                if args.dry_run:
                    log.append(f"  + {name}: {skill.name}")
                    continue
            if not args.dry_run:
                how = create_link(link, skill, args.mode)
                log.append(f"  + {name}: {skill.name} ({how})")
        elif state == "file":
            log.append(f"  ! {name}: {skill.name} is an unrelated file; refusing replacement")
        else:  # real directory, not forced
            log.append(f"  ! {name}: {skill.name} exists as a real dir - use --force to replace")

    if args.prune:
        for entry in sorted(agent_dir.iterdir()) if agent_dir.is_dir() else []:
            if entry.name not in wanted and _is_link(entry):
                action = "would remove" if args.dry_run else "removed"
                if not args.dry_run:
                    _remove_link(entry)
                log.append(f"  - {name}: {action} stale link {entry.name}")
    return log


def verify(categories: dict[str, list[Path]], skills: list[Path], legacy: list[Path], portable: bool = False) -> int:
    failures = 0
    for legacy_skill in legacy:
        print(f"[FAIL] {legacy_skill.relative_to(REPO)} has no category home")
        failures += 1
    for name, cats in sorted(find_collisions(categories).items()):
        print(f"[FAIL] skill '{name}' exists in multiple categories: {', '.join(cats)}")
        failures += 1
    for name, rel in AGENT_DIRS.items():
        agent_dir = REPO / rel
        if not agent_dir.is_dir():
            print(f"[FAIL] {name}: {rel} does not exist")
            failures += 1
            continue
        for skill in skills:
            link = agent_dir / skill.name
            native_ok = _is_link(link) and os.path.realpath(link) == os.path.realpath(skill)
            portable_ok = portable and skill.is_dir() and _is_serialized_reference(link, skill)
            if not (native_ok or portable_ok):
                print(f"[FAIL] {name}: {rel}/{skill.name} is not a valid reference")
                failures += 1
    print(f"verify ({'portable' if portable else 'native'}): {len(skills)} skills x {len(AGENT_DIRS)} agents, {failures} failure(s)")
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--verify",
        action="store_true",
        help="validate skill scopes and check every reference, then exit",
    )
    parser.add_argument("--dry-run", action="store_true", help="show planned changes without writing")
    parser.add_argument("--prune", action="store_true", help="remove references to skills no longer in skills/")
    parser.add_argument("--force", action="store_true", help="replace a real directory with a reference")
    parser.add_argument("--mode", choices=["auto", "symlink", "junction", "copy", "portable"], default="auto",
                        help="link strategy (default: auto - symlink, junction fallback on Windows)")
    parser.add_argument("--agents", nargs="*", choices=list(AGENT_DIRS), default=list(AGENT_DIRS),
                        help="subset of agents to sync (default: all)")
    args = parser.parse_args(argv)

    categories, legacy = discover_skills()
    skills = [skill for group in categories.values() for skill in group]
    if not skills:
        print(f"no skills found under {SKILLS_ROOT}", file=sys.stderr)
        return 1

    for legacy_skill in legacy:
        print(f"[warn] {legacy_skill.relative_to(REPO)} has no category home - move it under a category directory",
              file=sys.stderr)

    collisions = find_collisions(categories)
    if collisions:
        for name, cats in sorted(collisions.items()):
            print(f"[error] skill '{name}' exists in multiple categories: {', '.join(cats)}", file=sys.stderr)
        return 1

    validation_errors = validate_skills(skills)
    if legacy:
        validation_errors.extend(f"{skill.name}: missing category home" for skill in legacy)
    if validation_errors:
        for error in validation_errors:
            print(f"[FAIL] {error}", file=sys.stderr)
        return 1

    if args.verify:
        return verify(categories, skills, legacy, portable=args.mode == "portable")

    print(f"skill home: {SKILLS_ROOT} ({len(skills)})")
    for category, group in categories.items():
        print(f"  {category}: {len(group)}")
    for name in args.agents:
        for line in sync_agent(name, AGENT_DIRS[name], skills, args):
            print(line)
    if args.dry_run:
        print("(dry run - nothing written)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
