#!/usr/bin/env python3
"""Verify the requirement packages under docs/requirements/.

A package is a directory with ``requirement.md``, ``grill-log.md``, ``diagrams.md`` and
``features/*.feature``. This script checks that:

- every package has those files and an ``Owns:`` line in ``requirement.md``;
- every FR and NFR listed in the baseline documents is owned by exactly one package,
  and every owned FR has a feature file tagged with its id;
- feature files are well-formed Gherkin: Feature, Given/When/Then in order, unique
  scenario titles, and Examples for every Scenario Outline;
- every grill log covers the eight dimensions and each question carries a recommendation,
  a reason, a valid status, and a ``Feeds`` line;
- every ``knowledge/...`` path cited under Knowledge References exists.

Usage::

    python3 scripts/verify_requirements.py            # verify docs/requirements/
    python3 scripts/verify_requirements.py <dir>      # verify another requirements directory
    python3 scripts/verify_requirements.py --decisions > docs/requirements/decisions-for-review.md
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DIMENSIONS = ["Intent", "Scope", "Behaviour", "Data", "Integration", "Architecture", "Acceptance", "Ambiguity"]
STATUSES = {"Settled", "Recommended", "Decision needed"}
PACKAGE_FILES = ("requirement.md", "grill-log.md", "diagrams.md")
STEP = re.compile(r"^(Given|When|Then|And|But)\s+\S")


def packages(root: Path) -> list[Path]:
    return sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith("_") and (p / "requirement.md").is_file())


def owned_ids(requirement: Path) -> set[str]:
    match = re.search(r"(?m)^- \*\*Owns:\*\* (.+)$", requirement.read_text(encoding="utf-8"))
    return set(re.findall(r"\b(?:FR|NFR)-\d{3}\b", match.group(1))) if match else set()


def baseline_ids(root: Path) -> tuple[set[str], set[str]]:
    fr = root / "functional-requirements.md"
    nfr = root / "non-functional-requirements.md"
    frs = set(re.findall(r"(?m)^\| (FR-\d{3}) \|", fr.read_text(encoding="utf-8"))) if fr.is_file() else set()
    nfrs = set(re.findall(r"(?m)^## (NFR-\d{3}) ", nfr.read_text(encoding="utf-8"))) if nfr.is_file() else set()
    return frs, nfrs


def check_feature(path: Path, rel: str, errors: list[str]) -> set[str]:
    """Lint one feature file; return the tags found at feature level."""
    lines = [line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()]
    feature_tags: set[str] = set()
    pending: list[str] = []
    seen_feature = False
    titles: set[str] = set()
    scenario = None  # (title, kind, steps, has_examples)

    def close() -> None:
        nonlocal scenario
        if scenario is None:
            return
        title, kind, steps, has_examples = scenario
        kinds = [k for k, _ in steps]
        if not steps or kinds[0] not in ("Given", "When"):
            errors.append(f"{rel}: scenario '{title}' must start with Given or When")
        if "Then" not in kinds:
            errors.append(f"{rel}: scenario '{title}' has no Then")
        elif "When" not in kinds:
            errors.append(f"{rel}: scenario '{title}' has no When")
        elif kinds.index("Then") < kinds.index("When"):
            errors.append(f"{rel}: scenario '{title}' has Then before When")
        if kind == "Scenario Outline":
            if not has_examples:
                errors.append(f"{rel}: outline '{title}' has no Examples")
            if not any("<" in text for _, text in steps):
                errors.append(f"{rel}: outline '{title}' uses no <parameter>")
        scenario = None

    for number, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("@"):
            pending += line.split()
            continue
        if line.startswith("Feature:"):
            if seen_feature:
                errors.append(f"{rel}:{number}: more than one Feature")
            seen_feature = True
            feature_tags = {t.lstrip("@") for t in pending}
            pending = []
            continue
        kind = "Scenario Outline" if line.startswith("Scenario Outline:") else "Scenario" if line.startswith("Scenario:") else None
        if kind:
            close()
            title = line.split(":", 1)[1].strip()
            if not title:
                errors.append(f"{rel}:{number}: scenario without a title")
            elif title in titles:
                errors.append(f"{rel}:{number}: duplicate scenario title '{title}'")
            titles.add(title)
            scenario = (title, kind, [], False)
            pending = []
            continue
        if line.startswith("Examples:") and scenario:
            scenario = (scenario[0], scenario[1], scenario[2], True)
            continue
        step = STEP.match(line)
        if step and scenario:
            word = step.group(1)
            kinds = [k for k, _ in scenario[2]]
            effective = word if word not in ("And", "But") else (kinds[-1] if kinds else "Given")
            scenario[2].append((effective, line))
        elif line.startswith("|") or not scenario:
            continue  # table row, or feature description text
    close()
    if not seen_feature:
        errors.append(f"{rel}: no Feature")
    return feature_tags


def check_grill(path: Path, rel: str, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    sections = {m.group(1): m.end() for m in re.finditer(r"(?m)^## (\w+)\s*$", text)}
    for dimension in DIMENSIONS:
        if dimension not in sections:
            errors.append(f"{rel}: missing dimension '{dimension}'")
    questions = re.split(r"(?m)^\*\*Q\d+\. ", text)[1:]
    if len(questions) < len(DIMENSIONS):
        errors.append(f"{rel}: only {len(questions)} question(s)")
    for block in questions:
        head = block.splitlines()[0]
        for label in ("Recommendation", "Why", "Status", "Feeds"):
            if f"- **{label}:**" not in block:
                errors.append(f"{rel}: question '{head[:50]}' lacks {label}")
        status = re.search(r"- \*\*Status:\*\* (.+)", block)
        if status and status.group(1).strip() not in STATUSES:
            errors.append(f"{rel}: question '{head[:50]}' has status '{status.group(1).strip()}'")


def verify(root: Path) -> tuple[list[str], dict]:
    root = root.resolve()
    errors: list[str] = []
    stats = {"packages": 0, "features": 0, "scenarios": 0, "questions": 0, "decisions": 0}
    pkgs = packages(root)
    stats["packages"] = len(pkgs)
    owners: dict[str, list[str]] = {}
    feature_tags: dict[str, set[str]] = {}
    repo = next((p for p in [root, *root.parents] if (p / "knowledge").is_dir()), None)

    for pkg in pkgs:
        for name in PACKAGE_FILES:
            if not (pkg / name).is_file():
                errors.append(f"{pkg.name}/{name}: missing")
        features = sorted((pkg / "features").glob("*.feature"))
        if not features:
            errors.append(f"{pkg.name}/features: no .feature files")
        requirement = pkg / "requirement.md"
        text = requirement.read_text(encoding="utf-8")
        ids = owned_ids(requirement)
        if not ids and "**Owns:**" not in text:
            errors.append(f"{pkg.name}/requirement.md: no Owns line")
        for ident in ids:
            owners.setdefault(ident, []).append(pkg.name)
        if repo is not None:
            for cited in re.findall(r"`(knowledge/[^`]+\.md)`", text):
                if not (repo / cited).is_file():
                    errors.append(f"{pkg.name}/requirement.md: knowledge reference '{cited}' does not exist")
        for feature in features:
            stats["features"] += 1
            tags = check_feature(feature, f"{pkg.name}/features/{feature.name}", errors)
            stats["scenarios"] += len(re.findall(r"(?m)^\s*Scenario(?: Outline)?:", feature.read_text(encoding="utf-8")))
            for tag in tags:
                feature_tags.setdefault(tag, set()).add(pkg.name)
        grill = pkg / "grill-log.md"
        if grill.is_file():
            check_grill(grill, f"{pkg.name}/grill-log.md", errors)
            body = grill.read_text(encoding="utf-8")
            stats["questions"] += len(re.findall(r"(?m)^\*\*Q\d+\. ", body))
            stats["decisions"] += len(re.findall(r"(?m)^- \*\*Status:\*\* Decision needed", body))

    frs, nfrs = baseline_ids(root)
    for ident in sorted(frs | nfrs):
        found = owners.get(ident, [])
        if not found:
            errors.append(f"{ident}: not owned by any package")
        elif len(found) > 1:
            errors.append(f"{ident}: owned by several packages ({', '.join(found)})")
    for ident in sorted(set(owners) - frs - nfrs):
        errors.append(f"{ident}: owned by {owners[ident][0]} but not in the baseline documents")
    for ident in sorted(i for i in frs if owners.get(i)):
        if ident not in feature_tags or owners[ident][0] not in feature_tags[ident]:
            errors.append(f"{ident}: no feature file tagged @{ident} in package {owners[ident][0]}")
    return errors, stats


def decisions_markdown(root: Path) -> str:
    """Every 'Decision needed' question across the grill logs, with the recommended answer."""
    out = [
        "# Decisions for Review", "",
        "Generated by `python3 scripts/verify_requirements.py --decisions`. Do not edit by hand: change the answer in the "
        "package's grill log and regenerate.", "",
        "Each row is a trade-off the grill could not settle from existing documents. The recommendation is my answer; "
        "confirm it, or change the grill log.", "",
    ]
    for pkg in packages(root):
        text = (pkg / "grill-log.md").read_text(encoding="utf-8")
        rows = []
        for block in re.split(r"(?m)^\*\*(?=Q\d+\. )", text)[1:]:
            if "- **Status:** Decision needed" not in block:
                continue
            head, rest = block.split("**", 1)[0], block
            number, question = re.match(r"(Q\d+)\. (.+?)\*\*", block, re.S).groups()
            recommendation = re.search(r"- \*\*Recommendation:\*\* (.+)", block).group(1)
            rows.append((number, " ".join(question.split()), recommendation))
        if rows:
            out += [f"## {pkg.name}", "", "| Q | Question | Recommended answer |", "|---|---|---|"]
            out += [f"| {n} | {q} | {r.replace('|', '/')} |" for n, q, r in rows]
            out.append("")
    return "\n".join(out)


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else REPO / "docs" / "requirements"
    if "--decisions" in sys.argv:
        print(decisions_markdown(root))
        return 0
    errors, stats = verify(root)
    for error in errors:
        print(f"FAIL  {error}")
    print(
        f"requirements: {stats['packages']} package(s), {stats['features']} feature file(s), "
        f"{stats['scenarios']} scenario(s), {stats['questions']} grill question(s) "
        f"({stats['decisions']} need your decision), {len(errors)} error(s)"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
