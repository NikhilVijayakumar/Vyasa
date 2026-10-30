"""Refresh only the indexed checkouts of one project."""
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from vyasa import __version__
from vyasa.adapters.sqlite import lock, projects
from vyasa.application.indexing.scan import enrich_run
from vyasa.adapters.filesystem.repository_walk import classify_git_entry, _markers
from vyasa.adapters.filesystem.git_config import read_remote
from vyasa.adapters.filesystem.profile_file import read_profile
from vyasa.adapters.filesystem.report_file import read_report_file
from vyasa.domain.discovery import COMPLETE, ELIGIBLE, KIND_PROJECT, Candidate, DiscoveryOptions, DiscoveryRun
from vyasa.domain.index import INVALID_INPUT, PROJECT_NOT_FOUND, IndexStoreError


def _now():
    return datetime.now(timezone.utc)


def _eligible(path: Path, roots: tuple[Path, ...]) -> Path | None:
    """Reject links and junctions along a checkout's path from a configured root."""
    for root in roots:
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        current = root
        for part in rel.parts:
            current = current / part
            if current.is_symlink() or os.path.isjunction(current):
                return None
        try:
            if not path.resolve().is_relative_to(root.resolve()):
                return None
        except OSError:
            return None
        return root
    return None


def _inspect_selected(path: Path, options: DiscoveryOptions, git: str | None) -> Candidate | None:
    """Classify the indexed directory itself without discovering nested projects."""
    with os.scandir(path) as entries:
        names = [entry.name for entry in entries if entry.is_file(follow_symlinks=False)]
    markers = _markers(names, options)
    if os.path.lexists(path / '.git'):
        return classify_git_entry(str(path), markers, options.report_limits)
    if not markers:
        return None
    remote, remote_status = None, None
    if git and git != '.':
        child = path / git
        if Path(git).name != git or child.is_symlink() or os.path.isjunction(child):
            return None
        git_candidate = classify_git_entry(str(child), (), options.report_limits)
        if git_candidate.outcome != ELIGIBLE:
            return None
        remote, remote_status = read_remote(str(child))
    return Candidate(path, ELIGIBLE, kind=KIND_PROJECT, markers=markers, git=git,
                     remote=remote, remote_status=remote_status,
                     profile=read_profile(str(path)), report=read_report_file(str(path), options.report_limits))


def scan_project(config, connection: sqlite3.Connection, project_id: str, *, owner: str) -> dict:
    if not isinstance(project_id, str) or not 1 <= len(project_id) <= 200:
        raise IndexStoreError(INVALID_INPUT, 'Invalid project identifier.')
    if not connection.execute('SELECT 1 FROM projects WHERE project_id = ?', (project_id,)).fetchone():
        raise IndexStoreError(PROJECT_NOT_FOUND, 'No project has that identifier.')
    checkouts = connection.execute('SELECT checkout_id,path,git FROM checkouts WHERE project_id = ? ORDER BY checkout_id', (project_id,)).fetchall()
    run_id = uuid.uuid4().hex
    lock.acquire(connection, owner, run_id, _now())
    outcomes = []
    try:
        connection.execute("INSERT INTO scan_runs (run_id,root,status,tool_version,started_at,scope_kind,scope_project_id) VALUES (?,NULL,'running',?,?,'project',?)", (run_id, __version__, _now().isoformat(), project_id))
        for checkout in checkouts:
            path = Path(checkout['path'])
            root = _eligible(path, config.roots)
            reason = None
            if root is None:
                reason = 'OUTSIDE_CONFIGURED_ROOTS'
            elif not path.exists():
                reason = 'MISSING'
            else:
                try:
                    options = DiscoveryOptions(report_limits=config.report)
                    candidate = _inspect_selected(path, options, checkout['git'])
                    if candidate is None or candidate.outcome != ELIGIBLE:
                        reason = 'INACCESSIBLE' if candidate and candidate.outcome == 'inaccessible' else 'SCAN_FAILED'
                    elif (candidate.remote_status == 'unavailable' and not ((path / (candidate.git or '') / '.git').is_file() and not (path / (candidate.git or '') / '.git').is_symlink())
                          or (candidate.profile and candidate.profile.status not in ('valid', 'absent'))
                          or (candidate.report and candidate.report.status not in ('present', 'not_present'))):
                        reason = 'SCAN_FAILED'
                    else:
                        stamp = _now()
                        found = DiscoveryRun(run_id, path, stamp, stamp, COMPLETE, __version__, options, {}, (candidate,), ())
                        found = enrich_run(found)
                        candidate = found.repositories[0]
                        observation = candidate.languages
                        incomplete = (found.status != COMPLETE or observation is None or observation.failed
                                      or observation.report is None or not observation.report.complete)
                        if observation and observation.frameworks:
                            incomplete = incomplete or any(m.status != 'parsed' for m in observation.frameworks.manifests)
                        if incomplete:
                            reason = 'SCAN_FAILED'
                        else:
                            result = projects.upsert(connection, candidate, root, run_id, _now())
                            if result == 'conflicts':
                                reason = 'IDENTITY_CONFLICT'
                except OSError:
                    reason = 'INACCESSIBLE'
            status = 'failed' if reason else 'completed'
            connection.execute('INSERT INTO scan_checkout_results (run_id,checkout_id,status,reason) VALUES (?,?,?,?)', (run_id, checkout['checkout_id'], status, reason))
            outcomes.append({'checkout_id': checkout['checkout_id'], 'status': status, 'reason': reason})
            lock.heartbeat(connection, run_id, _now())
        successes = sum(item['status'] == 'completed' for item in outcomes)
        status = 'failed' if not successes else 'completed' if successes == len(outcomes) else 'partial'
        connection.execute('UPDATE scan_runs SET status=?,finished_at=?,counts=? WHERE run_id=?', (status, _now().isoformat(), json.dumps({'completed': successes, 'failed': len(outcomes)-successes}), run_id))
        return {'project_id': project_id, 'run_id': run_id, 'status': status, 'checkouts': outcomes}
    except BaseException:
        connection.execute("UPDATE scan_runs SET status='interrupted',finished_at=? WHERE run_id=?", (_now().isoformat(), run_id))
        raise
    finally:
        lock.release(connection, run_id)
