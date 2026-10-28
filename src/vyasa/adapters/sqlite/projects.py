"""Project and checkout rows. Every value is a bound parameter."""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

from vyasa.adapters.sqlite import reports
from vyasa.domain.discovery import Candidate
from vyasa.domain.file_composition import documentation_only
from vyasa.domain.frameworks import ECOSYSTEMS, Dependency, FrameworkReport
from vyasa.domain.languages import LanguageOutcome
from vyasa.domain.markers import MARKERS
from vyasa.domain.profile import ABSENT, PROFILE_PATH, ProfileResult
from vyasa.domain.index import (
    ACTIVE,
    DUPLICATE_CHECKOUT,
    FLAG_CLEARED,
    FLAG_OPEN,
    IDENTITY_UNRESOLVED,
    INACCESSIBLE,
    MISSING,
)

ADDED, ATTACHED, UPDATED, UNCHANGED, RESTORED, CONFLICT = "added", "attached", "updated", "unchanged", "restored", "conflicts"
REMOTE = "remote"


def path_key(path: Path) -> str:
    return os.path.normcase(str(path))


def _fields(candidate: Candidate) -> tuple:
    remote = candidate.remote
    return (
        candidate.kind,
        json.dumps(list(candidate.markers)),
        candidate.git,
        remote.provider if remote else None,
        remote.host if remote else None,
        remote.identity if remote else None,
        candidate.remote_status,
    )


def _event(connection: sqlite3.Connection, project_id: str, kind: str, detail: dict, run_id: str | None, stamp: str) -> None:
    connection.execute(
        "INSERT INTO identity_events (project_id, kind, detail, run_id, at) VALUES (?, ?, ?, ?, ?)",
        (project_id, kind, json.dumps(detail, sort_keys=True), run_id, stamp),
    )


def _alias_owner(connection: sqlite3.Connection, identity: str | None) -> str | None:
    if identity is None:
        return None
    row = connection.execute(
        "SELECT project_id FROM project_aliases WHERE alias_kind = ? AND alias_value = ?", (REMOTE, identity)
    ).fetchone()
    return row[0] if row else None


def _add_alias(connection: sqlite3.Connection, project_id: str, identity: str, stamp: str) -> None:
    connection.execute(
        "INSERT INTO project_aliases (alias_kind, alias_value, project_id, first_seen_at) VALUES (?, ?, ?, ?)",
        (REMOTE, identity, project_id, stamp),
    )


def _raise(connection: sqlite3.Connection, project_id: str, kind: str, evidence: dict, run_id: str | None, stamp: str) -> None:
    """Open the flag, or keep it open. A `flagged` event is written when it was absent or cleared."""
    row = connection.execute(
        "SELECT flag_id, state, evidence FROM review_flags WHERE project_id = ? AND kind = ?", (project_id, kind)
    ).fetchone()
    text = json.dumps(evidence, sort_keys=True)
    if row is None:
        connection.execute(
            "INSERT INTO review_flags (project_id, kind, state, evidence, raised_at, run_id) VALUES (?, ?, ?, ?, ?, ?)",
            (project_id, kind, FLAG_OPEN, text, stamp, run_id),
        )
    elif row["state"] == FLAG_CLEARED:
        connection.execute(
            "UPDATE review_flags SET state = ?, evidence = ?, raised_at = ?, cleared_at = NULL, run_id = ? WHERE flag_id = ?",
            (FLAG_OPEN, text, stamp, run_id, row["flag_id"]),
        )
    else:
        if json.loads(row["evidence"]) != evidence:
            connection.execute("UPDATE review_flags SET evidence = ?, run_id = ? WHERE flag_id = ?", (text, run_id, row["flag_id"]))
        return
    _event(connection, project_id, "flagged", {"flag": kind}, run_id, stamp)


def _clear(connection: sqlite3.Connection, project_id: str, kind: str, run_id: str | None, stamp: str) -> None:
    cleared = connection.execute(
        "UPDATE review_flags SET state = ?, cleared_at = ?, run_id = ? WHERE project_id = ? AND kind = ? AND state = ?",
        (FLAG_CLEARED, stamp, run_id, project_id, kind, FLAG_OPEN),
    ).rowcount
    if cleared:
        _event(connection, project_id, "resolved", {"flag": kind}, run_id, stamp)


def _sync_duplicate(connection: sqlite3.Connection, project_id: str, run_id: str | None, stamp: str) -> None:
    active = connection.execute(
        "SELECT COUNT(*) FROM checkouts WHERE project_id = ? AND state = ?", (project_id, ACTIVE)
    ).fetchone()[0]
    if active > 1:
        aliases = sorted(r[0] for r in connection.execute("SELECT alias_value FROM project_aliases WHERE project_id = ?", (project_id,)))
        evidence = {"rule": "same_remote_identity", "aliases": aliases, "active_checkouts": active}
        _raise(connection, project_id, DUPLICATE_CHECKOUT, evidence, run_id, stamp)
    else:
        _clear(connection, project_id, DUPLICATE_CHECKOUT, run_id, stamp)


def _settle(connection: sqlite3.Connection, project_id: str, run_id: str, stamp: str) -> None:
    """The evidence no longer conflicts: an ambiguous project takes the status its aliases support."""
    row = connection.execute("SELECT identity_status FROM projects WHERE project_id = ?", (project_id,)).fetchone()
    if row["identity_status"] != "ambiguous":
        return
    has_alias = connection.execute("SELECT 1 FROM project_aliases WHERE project_id = ?", (project_id,)).fetchone()
    connection.execute(
        "UPDATE projects SET identity_status = ?, identity_source = ?, updated_at = ? WHERE project_id = ?",
        ("resolved" if has_alias else "provisional", REMOTE if has_alias else "path", stamp, project_id),
    )
    _clear(connection, project_id, IDENTITY_UNRESOLVED, run_id, stamp)


def refresh_state(connection: sqlite3.Connection, project_id: str, stamp: str) -> None:
    """A project is active while any checkout is, else inaccessible while any is, else missing."""
    states = {r[0] for r in connection.execute("SELECT state FROM checkouts WHERE project_id = ?", (project_id,))}
    state = ACTIVE if ACTIVE in states else INACCESSIBLE if INACCESSIBLE in states else MISSING
    connection.execute(
        "UPDATE projects SET state = ?, updated_at = CASE WHEN state = ? THEN updated_at ELSE ? END WHERE project_id = ?",
        (state, state, stamp, project_id),
    )


def _store_profile(connection: sqlite3.Connection, checkout_id: int, profile: ProfileResult | None, run_id: str, stamp: str) -> None:
    profile = profile or ProfileResult(ABSENT)
    connection.execute(
        "INSERT INTO checkout_profiles (checkout_id, status, fields, problems, read_at, run_id) VALUES (?, ?, ?, ?, ?, ?)"
        " ON CONFLICT (checkout_id) DO UPDATE SET status = excluded.status, fields = excluded.fields,"
        " problems = excluded.problems, read_at = excluded.read_at, run_id = excluded.run_id",
        (checkout_id, profile.status, json.dumps(profile.fields, sort_keys=True),
         json.dumps([{"field": f, "reason": r} for f, r in profile.problems]), stamp, run_id),
    )


KEPT_OBSERVATIONS = 2


def _store_languages(connection: sqlite3.Connection, checkout_id: int, outcome: LanguageOutcome | None, run_id: str, stamp: str) -> None:
    """Add one observation and keep the newest two. No outcome means the checkout was not assessed: nothing changes."""
    if outcome is None:
        return
    report = outcome.report
    if report is None:
        status, stopped, reason, version = "failed", None, outcome.failed, 0
    else:
        status = "complete" if report.complete else "partial"
        stopped, reason, version = report.stopped_by, None, report.evidence.types_version
    counts = outcome.composition
    observation = connection.execute(
        "INSERT INTO language_observations (checkout_id, run_id, observed_at, status, stopped_by, types_version, reason, duration_ms,"
        " code_files, documentation_files, other_files, markers_version, frameworks_version)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (checkout_id, run_id, stamp, status, stopped, version, reason, round(outcome.seconds * 1000),
         *((counts.code, counts.documentation, counts.other) if counts and report else (None, None, None)),
         outcome.markers.rules_version if outcome.markers and report else None,
         outcome.frameworks.registry_version if outcome.frameworks and report else None),
    ).lastrowid
    if report is not None and outcome.frameworks is not None:
        _store_frameworks(connection, observation, outcome.frameworks)
    if report is not None and outcome.markers is not None:
        connection.executemany(
            "INSERT INTO checkout_markers (observation_id, marker, total, rules, paths) VALUES (?, ?, ?, ?, ?)",
            [(observation, f.marker, f.total, json.dumps(list(f.rules)),
              json.dumps([{"path": p, **({"scope": s} if s else {})} for p, s in f.paths])) for f in outcome.markers.found],
        )
    if report is not None:
        connection.executemany(
            "INSERT INTO checkout_languages (observation_id, label, status, files) VALUES (?, ?, ?, ?)",
            [(observation, label, "files_detected", count) for label, count in report.files_detected]
            + [(observation, label, "declared", None) for label in report.declared],
        )
    connection.execute(
        "DELETE FROM language_observations WHERE checkout_id = ? AND observation_id NOT IN"
        " (SELECT observation_id FROM language_observations WHERE checkout_id = ? ORDER BY observation_id DESC LIMIT ?)",
        (checkout_id, checkout_id, KEPT_OBSERVATIONS),
    )


_CURRENT = "(SELECT MAX(observation_id) FROM language_observations WHERE checkout_id = c.checkout_id)"


def present_languages(connection: sqlite3.Connection, project_id: str) -> list[tuple[str, str]]:
    """(label, status) pairs from the current observation of each active checkout of a project."""
    return [
        (r[0], r[1])
        for r in connection.execute(
            "SELECT l.label, l.status FROM checkouts c JOIN checkout_languages l ON l.observation_id = " + _CURRENT +
            " WHERE c.project_id = ? AND c.state = 'active'",
            (project_id,),
        )
    ]


def checkout_composition(connection: sqlite3.Connection, checkout_id: int) -> dict:
    """The counts of the current observation of one checkout, or not_counted. Never summed across checkouts."""
    row = connection.execute(
        "SELECT status, stopped_by, observed_at, code_files, documentation_files, other_files FROM language_observations"
        " WHERE checkout_id = ? ORDER BY observation_id DESC LIMIT 1",
        (checkout_id,),
    ).fetchone()
    if row is None or row["code_files"] is None:
        return {"status": "not_counted", "stopped_by": None, "observed_at": None, "code": None, "documentation": None,
                "other": None, "total": None, "documentation_only": None}
    code, docs, other = row["code_files"], row["documentation_files"], row["other_files"]
    return {"status": row["status"], "stopped_by": row["stopped_by"], "observed_at": row["observed_at"], "code": code,
            "documentation": docs, "other": other, "total": code + docs + other,
            "documentation_only": documentation_only(code, docs, row["status"] == "complete")}


def _store_frameworks(connection: sqlite3.Connection, observation: int, found: FrameworkReport) -> None:
    connection.execute("UPDATE language_observations SET names_recorded = 1 WHERE observation_id = ?", (observation,))
    for manifest in found.manifests:
        connection.execute(
            "INSERT INTO checkout_manifests (observation_id, path, ecosystem, status, reason, total_dependencies, skipped, workspace,"
            " declared_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (observation, manifest.path, manifest.ecosystem, manifest.status, manifest.reason, manifest.total_dependencies,
             manifest.skipped, int(manifest.workspace), manifest.declared_name),
        )
        unique: dict[tuple[str, str], Dependency] = {}
        for dependency in manifest.dependencies:  # one row per name and scope; a manifest may declare both twice
            unique.setdefault((dependency.name, dependency.scope), dependency)
        connection.executemany(
            "INSERT INTO checkout_dependencies (observation_id, path, name, constraint_text, scope) VALUES (?, ?, ?, ?, ?)",
            [(observation, manifest.path, d.name, d.constraint, d.scope) for d in unique.values()],
        )
    connection.executemany(
        "INSERT INTO checkout_technologies (observation_id, key, scopes, manifests) VALUES (?, ?, ?, ?)",
        [(observation, t.key, json.dumps(list(t.scopes)), json.dumps(list(t.manifests))) for t in found.technologies],
    )
    connection.executemany(
        "INSERT INTO checkout_nested_manifests (observation_id, ecosystem, count) VALUES (?, ?, ?)",
        [(observation, ecosystem, count) for ecosystem, count in found.nested],
    )


def checkout_frameworks(connection: sqlite3.Connection, checkout_id: int) -> dict:
    """The frameworks of the current observation of one checkout. Absence is only claimed after a complete assessment."""
    row = connection.execute(
        "SELECT observation_id, status, stopped_by, observed_at, frameworks_version FROM language_observations"
        " WHERE checkout_id = ? ORDER BY observation_id DESC LIMIT 1",
        (checkout_id,),
    ).fetchone()
    if row is None or row["frameworks_version"] is None:
        return {"status": "not_assessed", "registry_version": None, "stopped_by": None, "observed_at": None,
                "ecosystems": [], "technologies": []}
    observation = row["observation_id"]
    manifests: dict[str, list[dict]] = {e: [] for e in ECOSYSTEMS}
    for m in connection.execute(
        "SELECT path, ecosystem, status, reason, total_dependencies, skipped, workspace FROM checkout_manifests"
        " WHERE observation_id = ? ORDER BY path", (observation,)
    ):
        dependencies = [
            {"name": d["name"], "constraint": d["constraint_text"], "scope": d["scope"]}
            for d in connection.execute(
                "SELECT name, constraint_text, scope FROM checkout_dependencies WHERE observation_id = ? AND path = ?"
                " ORDER BY name, scope", (observation, m["path"]))
        ]
        manifests[m["ecosystem"]].append({
            "path": m["path"], "status": m["status"], "reason": m["reason"], "total_dependencies": m["total_dependencies"],
            "skipped": m["skipped"], "workspace": bool(m["workspace"]), "dependencies": dependencies,
        })
    nested = dict(connection.execute("SELECT ecosystem, count FROM checkout_nested_manifests WHERE observation_id = ?", (observation,)))
    missing = "not_detected" if row["status"] == "complete" else "unknown"
    ecosystems = [
        {"ecosystem": e, "state": "detected" if manifests[e] else missing, "manifests": manifests[e], "nested_not_parsed": nested.get(e, 0)}
        for e in ECOSYSTEMS
    ]
    technologies = [
        {"key": t["key"], "scopes": json.loads(t["scopes"]), "manifests": json.loads(t["manifests"])}
        for t in connection.execute("SELECT key, scopes, manifests FROM checkout_technologies WHERE observation_id = ? ORDER BY key", (observation,))
    ]
    return {"status": row["status"], "registry_version": row["frameworks_version"], "stopped_by": row["stopped_by"],
            "observed_at": row["observed_at"], "ecosystems": ecosystems, "technologies": technologies}


def checkout_markers(connection: sqlite3.Connection, checkout_id: int) -> dict:
    """The markers of the current observation of one checkout. Absence is only claimed after a complete assessment."""
    row = connection.execute(
        "SELECT observation_id, status, stopped_by, observed_at, markers_version FROM language_observations"
        " WHERE checkout_id = ? ORDER BY observation_id DESC LIMIT 1",
        (checkout_id,),
    ).fetchone()
    if row is None or row["markers_version"] is None:
        return {"status": "not_assessed", "rules_version": None, "stopped_by": None, "observed_at": None, "items": []}
    detected = {
        r["marker"]: r
        for r in connection.execute("SELECT marker, total, rules, paths FROM checkout_markers WHERE observation_id = ?", (row["observation_id"],))
    }
    missing = "not_detected" if row["status"] == "complete" else "unknown"
    items = []
    for marker in MARKERS:
        hit = detected.get(marker)
        if hit is None:
            items.append({"marker": marker, "state": missing})
            continue
        paths = json.loads(hit["paths"])
        items.append({"marker": marker, "state": "detected", "total": hit["total"], "rules": json.loads(hit["rules"]),
                      "paths": paths, "more": hit["total"] - len(paths)})
    return {"status": row["status"], "rules_version": row["markers_version"], "stopped_by": row["stopped_by"],
            "observed_at": row["observed_at"], "items": items}


def checkout_languages(connection: sqlite3.Connection, checkout_id: int) -> dict:
    """The current language observation of one checkout, or not_observed. Counts are never summed across checkouts."""
    row = connection.execute(
        "SELECT observation_id, status, stopped_by, observed_at, types_version, reason FROM language_observations"
        " WHERE checkout_id = ? ORDER BY observation_id DESC LIMIT 1",
        (checkout_id,),
    ).fetchone()
    if row is None:
        return {"status": "not_observed", "stopped_by": None, "observed_at": None, "types_version": None, "items": []}
    items = [
        {"label": r[0], "status": r[1], "files": r[2]}
        for r in connection.execute(
            "SELECT label, status, files FROM checkout_languages WHERE observation_id = ? ORDER BY label, status",
            (row["observation_id"],),
        )
    ]
    result = {"status": row["status"], "stopped_by": row["stopped_by"], "observed_at": row["observed_at"],
              "types_version": row["types_version"], "items": items}
    if row["reason"]:
        result["reason"] = row["reason"]
    return result


def project_profile(connection: sqlite3.Connection, project_id: str) -> dict:
    """The profile shown for a project: an active checkout first, readable before not, then the earliest seen."""
    row = connection.execute(
        "SELECT p.status, p.fields, p.problems FROM checkouts c LEFT JOIN checkout_profiles p USING (checkout_id)"
        " WHERE c.project_id = ? ORDER BY (c.state = 'active') DESC, (p.status IN ('valid', 'invalid')) DESC,"
        " c.first_seen_at, c.checkout_id LIMIT 1",
        (project_id,),
    ).fetchone()
    if row is None or row["status"] is None:
        return {"status": ABSENT, "source": PROFILE_PATH, "declared": {}, "problems": []}
    return {
        "status": row["status"],
        "source": PROFILE_PATH,
        "declared": {k: {"value": v, "status": "declared"} for k, v in json.loads(row["fields"]).items()},
        "problems": json.loads(row["problems"]),
    }


def upsert(connection: sqlite3.Connection, candidate: Candidate, root: Path, run_id: str, now: datetime) -> str:
    """Store one eligible repository in its own transaction. Returns what happened to it.

    The project is found by its remote identity alias, then by checkout path. When the two
    point at different projects nothing is merged or moved; the conflict is recorded.
    """
    stamp = now.isoformat()
    key = path_key(candidate.path)
    fields = _fields(candidate)
    identity = candidate.remote.identity if candidate.remote else None
    connection.execute("BEGIN IMMEDIATE")
    try:
        row = connection.execute(
            "SELECT checkout_id, project_id, state, kind, markers, git, remote_provider, remote_host,"
            " remote_identity, remote_status FROM checkouts WHERE path_key = ?",
            (key,),
        ).fetchone()
        owner = _alias_owner(connection, identity)
        if row is None:
            if owner is None:
                project_id = uuid.uuid4().hex
                connection.execute(
                    "INSERT INTO projects (project_id, display_name, state, identity_status, identity_source,"
                    " created_at, updated_at, last_seen_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (project_id, candidate.path.name or str(candidate.path), ACTIVE,
                     "resolved" if identity else "provisional", REMOTE if identity else "path", stamp, stamp, stamp),
                )
                if identity:
                    _add_alias(connection, project_id, identity, stamp)
                _event(connection, project_id, "created", {"alias": identity}, run_id, stamp)
                outcome = ADDED
            else:
                project_id, outcome = owner, ATTACHED
            checkout_id = connection.execute(
                "INSERT INTO checkouts (project_id, path, path_key, root, kind, markers, git, remote_provider,"
                " remote_host, remote_identity, remote_status, state, first_seen_at, last_seen_at, last_run_id)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (project_id, str(candidate.path), key, str(root), *fields, ACTIVE, stamp, stamp, run_id),
            ).lastrowid
        else:
            project_id = row["project_id"]
            checkout_id = row["checkout_id"]
            if owner is not None and owner != project_id:
                detail = json.dumps({"alias": identity, "owner": owner}, sort_keys=True)
                if not connection.execute(
                    "SELECT 1 FROM identity_events WHERE project_id = ? AND kind = 'identity_conflict' AND detail = ?",
                    (project_id, detail),
                ).fetchone():
                    _event(connection, project_id, "identity_conflict", {"alias": identity, "owner": owner}, run_id, stamp)
                connection.execute(
                    "UPDATE checkouts SET last_seen_at = ?, last_run_id = ? WHERE checkout_id = ?",
                    (stamp, run_id, row["checkout_id"]),
                )
                connection.execute(
                    "UPDATE projects SET identity_status = 'ambiguous', updated_at = CASE WHEN identity_status = 'ambiguous'"
                    " THEN updated_at ELSE ? END WHERE project_id = ?",
                    (stamp, project_id),
                )
                _raise(
                    connection, project_id, IDENTITY_UNRESOLVED,
                    {"alias": identity, "alias_owner": owner, "path_project": project_id}, run_id, stamp,
                )
                connection.execute("COMMIT")
                return CONFLICT
            same = tuple(row[name] for name in (
                "kind", "markers", "git", "remote_provider", "remote_host", "remote_identity", "remote_status",
            )) == fields
            outcome = RESTORED if row["state"] != ACTIVE else UNCHANGED if same else UPDATED
            if identity and owner is None:
                _add_alias(connection, project_id, identity, stamp)
                _event(connection, project_id, "alias_added", {"alias": identity}, run_id, stamp)
                connection.execute(
                    "UPDATE projects SET identity_status = 'resolved', identity_source = 'remote' WHERE project_id = ?"
                    " AND identity_status = 'provisional'",
                    (project_id,),
                )
                outcome = UPDATED if outcome == UNCHANGED else outcome
            _settle(connection, project_id, run_id, stamp)
            connection.execute(
                "UPDATE checkouts SET root = ?, kind = ?, markers = ?, git = ?, remote_provider = ?, remote_host = ?,"
                " remote_identity = ?, remote_status = ?, state = ?, last_seen_at = ?, last_run_id = ?"
                " WHERE checkout_id = ?",
                (str(root), *fields, ACTIVE, stamp, run_id, row["checkout_id"]),
            )
        _store_profile(connection, checkout_id, candidate.profile, run_id, stamp)
        reports.store(connection, checkout_id, candidate.report, run_id, stamp)
        _store_languages(connection, checkout_id, candidate.languages, run_id, stamp)
        refresh_state(connection, project_id, stamp)
        connection.execute("UPDATE projects SET last_seen_at = ? WHERE project_id = ?", (stamp, project_id))
        connection.execute("COMMIT")
        return outcome
    except BaseException:
        if connection.in_transaction:
            connection.execute("ROLLBACK")
        raise


def mark_inaccessible(connection: sqlite3.Connection, path: Path, run_id: str, now: datetime) -> bool:
    """The run saw this stored path and could not read it."""
    return _set_state(connection, "path_key = ?", (path_key(path),), INACCESSIBLE, run_id, now) > 0


def mark_absent(connection: sqlite3.Connection, root: Path, run_id: str, now: datetime) -> int:
    """Checkouts of ``root`` that a complete run did not see become missing."""
    return _set_state(
        connection, "root = ? AND state != 'missing' AND COALESCE(last_run_id, '') != ?", (str(root), run_id), MISSING, None, now
    )


def _set_state(connection: sqlite3.Connection, where: str, args: tuple, state: str, run_id: str | None, now: datetime) -> int:
    """``where`` is one of the fixed clauses above; values are always bound."""
    stamp = now.isoformat()
    connection.execute("BEGIN IMMEDIATE")
    try:
        ids = [r[0] for r in connection.execute(f"SELECT project_id FROM checkouts WHERE {where}", args)]
        connection.execute(
            f"UPDATE checkouts SET state = ?, last_run_id = COALESCE(?, last_run_id) WHERE {where}", (state, run_id, *args)
        )
        for project_id in dict.fromkeys(ids):
            refresh_state(connection, project_id, stamp)
        connection.execute("COMMIT")
        return len(ids)
    except BaseException:
        if connection.in_transaction:
            connection.execute("ROLLBACK")
        raise


def sync_duplicates(connection: sqlite3.Connection, run_id: str, now: datetime) -> None:
    """At the end of a run, once absent checkouts are marked: flag projects with several active checkouts."""
    stamp = now.isoformat()
    connection.execute("BEGIN IMMEDIATE")
    try:
        ids = [r[0] for r in connection.execute(
            "SELECT project_id FROM checkouts WHERE last_run_id = ?"
            " UNION SELECT project_id FROM review_flags WHERE kind = ? AND state = ?",
            (run_id, DUPLICATE_CHECKOUT, FLAG_OPEN),
        )]
        for project_id in sorted(ids):
            _sync_duplicate(connection, project_id, run_id, stamp)
        connection.execute("COMMIT")
    except BaseException:
        if connection.in_transaction:
            connection.execute("ROLLBACK")
        raise


def list_projects(connection: sqlite3.Connection, state: str | None = None) -> list[sqlite3.Row]:
    query = (
        "SELECT p.project_id, p.display_name, p.state, p.identity_status, p.identity_source, c.path, c.root, c.kind, c.remote_provider, c.remote_host,"
        " c.remote_identity, c.remote_status, c.last_seen_at FROM projects p JOIN checkouts c USING (project_id)"
    )
    if state is None:
        return connection.execute(query + " ORDER BY c.path_key").fetchall()
    return connection.execute(query + " WHERE p.state = ? ORDER BY c.path_key", (state,)).fetchall()


def list_aliases(connection: sqlite3.Connection, project_id: str) -> list[str]:
    rows = connection.execute(
        "SELECT alias_value FROM project_aliases WHERE project_id = ? ORDER BY first_seen_at, alias_value", (project_id,)
    )
    return [r[0] for r in rows]


def list_events(connection: sqlite3.Connection, project_id: str) -> list[sqlite3.Row]:
    return connection.execute(
        "SELECT kind, detail, run_id, at FROM identity_events WHERE project_id = ? ORDER BY event_id", (project_id,)
    ).fetchall()


def list_flags(connection: sqlite3.Connection, state: str | None = FLAG_OPEN) -> list[sqlite3.Row]:
    query = "SELECT project_id, kind, state, evidence, raised_at, cleared_at FROM review_flags"
    if state is None:
        return connection.execute(query + " ORDER BY project_id, kind").fetchall()
    return connection.execute(query + " WHERE state = ? ORDER BY project_id, kind", (state,)).fetchall()
