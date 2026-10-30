"""Open the index database: create it safely, set its pragmas, and apply forward-only migrations."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from vyasa.domain.index import MIGRATION_FAILED, SCHEMA_TOO_NEW, UNAVAILABLE, IndexStoreError

MIGRATIONS = Path(__file__).resolve().parent / "migrations"
BUSY_TIMEOUT_MS = 5000


def _migrations(directory: Path) -> list[tuple[int, Path]]:
    """Numbered files ``NNNN_name.sql`` in order."""
    return sorted((int(p.name.split("_", 1)[0]), p) for p in directory.glob("[0-9]*_*.sql"))


def _private(path: Path, mode: int) -> None:
    if os.name == "posix":
        os.chmod(path, mode)


def _create(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    _private(path.parent, 0o700)
    if not path.exists():
        os.close(os.open(path, os.O_CREAT | os.O_WRONLY, 0o600))
    _private(path, 0o600)


def _backup(connection: sqlite3.Connection, path: Path, version: int) -> None:
    target = path.with_name(f"{path.name}.bak-v{version}")
    copy = sqlite3.connect(target)
    try:
        connection.backup(copy)
    finally:
        copy.close()
    _private(target, 0o600)


def _apply(connection: sqlite3.Connection, number: int, file: Path) -> None:
    rebuild = file.name == "0012_project_scan_scope.sql"
    check = ("CREATE TEMP TABLE _migration_fk_check (n INTEGER CHECK (n = 0));"
             "INSERT INTO _migration_fk_check SELECT COUNT(*) FROM pragma_foreign_key_check;"
             "DROP TABLE _migration_fk_check;") if rebuild else ""
    script = f"BEGIN;\n{file.read_text(encoding='utf-8')}\n{check}\nPRAGMA user_version = {number};\nCOMMIT;"
    if rebuild:
        connection.execute("PRAGMA foreign_keys = OFF")
    try:
        connection.executescript(script)
    except sqlite3.Error as error:
        if connection.in_transaction:
            connection.rollback()
        raise IndexStoreError(MIGRATION_FAILED, f"migration {file.name} failed: {error}") from error
    finally:
        if rebuild:
            connection.execute("PRAGMA foreign_keys = ON")


def open_memory_index(migrations: Path = MIGRATIONS) -> sqlite3.Connection:
    """A migrated index that lives only in memory and vanishes when closed: nothing is created on disk."""
    connection = sqlite3.connect(":memory:", isolation_level=None)
    connection.execute("PRAGMA foreign_keys = ON")
    for number, file in _migrations(migrations):
        _apply(connection, number, file)
    connection.row_factory = sqlite3.Row
    return connection


def open_index(path: Path | str, *, read_only: bool = False, migrations: Path = MIGRATIONS) -> sqlite3.Connection:
    """Open (and for a writer, create and migrate) the index at ``path``."""
    path = Path(path)
    steps = _migrations(migrations)
    latest = steps[-1][0] if steps else 0
    try:
        if read_only:
            connection = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True, isolation_level=None)
        else:
            _create(path)
            connection = sqlite3.connect(path, isolation_level=None)
    except (OSError, sqlite3.Error) as error:
        raise IndexStoreError(UNAVAILABLE, f"cannot open the index under {path.parent}: {error}") from error
    try:
        # The version is read before anything can change the file, so a newer schema is left untouched.
        version = connection.execute("PRAGMA user_version").fetchone()[0]
        if version > latest:
            raise IndexStoreError(SCHEMA_TOO_NEW, f"the index is at schema {version}; this Vyasa knows up to {latest}")
        connection.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS}")
        connection.execute("PRAGMA foreign_keys = ON")
        if not read_only:
            connection.execute("PRAGMA journal_mode = WAL")
            pending = [(n, f) for n, f in steps if n > version]
            if pending and version > 0:
                _backup(connection, path, version)
            for number, file in pending:
                _apply(connection, number, file)
        connection.row_factory = sqlite3.Row
        return connection
    except sqlite3.Error as error:
        connection.close()
        raise IndexStoreError(UNAVAILABLE, f"cannot use the index at {path}: {error}") from error
    except BaseException:
        connection.close()
        raise
