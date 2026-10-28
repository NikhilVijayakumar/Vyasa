"""Direct dependencies and dependents of a project, read from the current observations. Every value is a bound parameter.

A dependency is internal only when its name equals a package another indexed project declares in the same ecosystem
(see knowledge/decisions/internal-dependencies-by-declared-package-name.md).
"""

from __future__ import annotations

import sqlite3

DEPENDENTS_LIMIT = 100

# The current observation of every active checkout: the one `checkout_frameworks` reads, so both views agree.
_CURRENT = (
    "SELECT c.project_id, c.checkout_id, o.observation_id, o.status, o.frameworks_version, o.names_recorded"
    " FROM checkouts c JOIN language_observations o ON o.observation_id ="
    " (SELECT MAX(observation_id) FROM language_observations WHERE checkout_id = c.checkout_id)"
    " WHERE c.state = 'active'"
)

Candidates = dict[tuple[str, str], dict[str, str]]


def _candidates(connection: sqlite3.Connection) -> Candidates:
    """Who declares each (ecosystem, package name): parsed manifests of assessed, active checkouts."""
    found: Candidates = {}
    # ponytail: the portfolio's declared names are held in memory; add a per-name query if portfolios outgrow that
    for row in connection.execute(
        f"SELECT m.ecosystem, m.declared_name, p.project_id, p.display_name FROM ({_CURRENT}) cur"
        " JOIN checkout_manifests m ON m.observation_id = cur.observation_id AND m.status = 'parsed'"
        " JOIN projects p ON p.project_id = cur.project_id"
        " WHERE cur.frameworks_version IS NOT NULL AND m.declared_name IS NOT NULL"
    ):
        found.setdefault((row["ecosystem"], row["declared_name"]), {})[row["project_id"]] = row["display_name"]
    return found


def _resolve(candidates: Candidates, ecosystem: str, name: str, owner: str) -> tuple[str, list[dict]]:
    """internal, ambiguous, or external for one dependency of ``owner``; a project is never its own dependency."""
    others = {pid: shown for pid, shown in candidates.get((ecosystem, name.lower()), {}).items() if pid != owner}
    matched = [{"project_id": pid, "display_name": shown} for pid, shown in sorted(others.items(), key=lambda i: (i[1], i[0]))]
    return ("external" if not matched else "internal" if len(matched) == 1 else "ambiguous"), matched


def project_dependencies(connection: sqlite3.Connection, project_id: str) -> dict:
    """Dependencies, dependents, and coverage of one project from the current observations of its active checkouts."""
    own = connection.execute(f"SELECT * FROM ({_CURRENT}) WHERE project_id = ?", (project_id,)).fetchall()
    assessed = [r for r in own if r["frameworks_version"] is not None]
    candidates = _candidates(connection)
    manifests, dependencies, nested, declared = [], set(), 0, set()
    for cur in assessed:
        observation, recorded = cur["observation_id"], cur["names_recorded"] == 1
        nested += sum(r[0] for r in connection.execute("SELECT count FROM checkout_nested_manifests WHERE observation_id = ?", (observation,)))
        for m in connection.execute(
            "SELECT path, ecosystem, status, reason, declared_name FROM checkout_manifests WHERE observation_id = ?", (observation,)
        ):
            manifests.append((m["ecosystem"], m["path"], m["status"], m["reason"], recorded))
            if m["status"] == "parsed" and m["declared_name"] is not None:
                declared.add((m["ecosystem"], m["declared_name"]))
        for d in connection.execute(
            "SELECT m.ecosystem, d.name, d.constraint_text, d.scope, d.path FROM checkout_dependencies d"
            " JOIN checkout_manifests m ON m.observation_id = d.observation_id AND m.path = d.path"
            " WHERE d.observation_id = ? AND m.status = 'parsed'", (observation,),
        ):
            dependencies.add((d["ecosystem"], d["name"], d["scope"], d["path"], d["constraint_text"]))
    listed = []
    for ecosystem, name, scope, source, constraint in sorted(dependencies, key=lambda d: (d[0], d[1], d[2], d[3], d[4] or "")):
        resolution, matched = _resolve(candidates, ecosystem, name, project_id)
        listed.append({"name": name, "ecosystem": ecosystem, "constraint": constraint, "scope": scope, "source": source,
                       "resolution": resolution, "projects": matched})
    dependents = set()
    for ecosystem, package in declared:
        for row in connection.execute(
            f"SELECT cur.project_id, p.display_name, d.name, d.constraint_text, d.scope, d.path FROM ({_CURRENT}) cur"
            " JOIN projects p ON p.project_id = cur.project_id"
            " JOIN checkout_manifests m ON m.observation_id = cur.observation_id AND m.status = 'parsed'"
            " JOIN checkout_dependencies d ON d.observation_id = m.observation_id AND d.path = m.path"
            " WHERE cur.frameworks_version IS NOT NULL AND cur.project_id != ? AND m.ecosystem = ? AND lower(d.name) = ?",
            (project_id, ecosystem, package),
        ):
            resolution, _ = _resolve(candidates, ecosystem, row["name"], row["project_id"])
            dependents.add((row["display_name"], row["project_id"], ecosystem, row["scope"], row["path"], row["name"],
                            row["constraint_text"], resolution))
    ordered = [
        {"project_id": pid, "display_name": shown, "ecosystem": e, "name": n, "constraint": c, "scope": s, "source": src,
         "resolution": r}
        for shown, pid, e, s, src, n, c, r in sorted(dependents, key=lambda d: (*d[:6], d[6] or ""))
    ]
    unchecked = connection.execute(
        f"SELECT COUNT(DISTINCT project_id) FROM ({_CURRENT}) WHERE project_id != ?"
        " AND (frameworks_version IS NULL OR status != 'complete' OR names_recorded IS NULL)", (project_id,)
    ).fetchone()[0]
    if not assessed:
        status = "not_assessed"
    elif len(assessed) < len(own) or any(r["status"] != "complete" for r in assessed):
        status = "partial"
    else:
        status = "complete"
    return {
        "coverage": {
            "status": status,
            "manifests": [{"path": p, "ecosystem": e, "status": s, "reason": r, "declared_name_recorded": rec}
                          for e, p, s, r, rec in sorted(manifests)],
            "nested_not_parsed": nested,
            "declared_names_recorded": bool(assessed) and all(r["names_recorded"] == 1 for r in assessed),
            "other_projects_unchecked": unchecked,
        },
        "dependencies": listed,
        "dependents": ordered[:DEPENDENTS_LIMIT],
        "dependents_total": len(ordered),
        "dependents_truncated": len(ordered) > DEPENDENTS_LIMIT,
    }
