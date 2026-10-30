"""Human-managed, machine-local names for configured workspace roots."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unicodedata
from pathlib import Path

from vyasa.domain.index import INVALID_INPUT, INTERNAL_ERROR, IndexStoreError


def _record(directory: Path, root: Path) -> Path:
    key = hashlib.sha256(os.path.normcase(os.path.normpath(str(root))).encode("utf-8")).hexdigest()
    return directory / "workspace-names" / (key + ".json")


def _validate(name: object) -> str:
    if not isinstance(name, str):
        raise IndexStoreError(INVALID_INPUT, "The workspace name is invalid.")
    value = name.strip()
    if not value or len(value) > 100 or any(unicodedata.category(ch) == "Cc" for ch in value):
        raise IndexStoreError(INVALID_INPUT, "Use a name of 1 to 100 characters without control characters.")
    return value


def read_name(directory: Path, root: Path) -> str | None:
    record = _record(directory, root)
    try:
        with record.open("rb") as f:
            raw = f.read(4097)
        if len(raw) > 4096:
            raise ValueError("record too large")
        data = json.loads(raw)
        if not isinstance(data, dict) or set(data) != {"name"} or _validate(data["name"]) != data["name"]:
            raise ValueError("invalid record")
        return data["name"]
    except FileNotFoundError:
        return None
    except (OSError, UnicodeError, ValueError, IndexStoreError) as error:
        raise IndexStoreError(INTERNAL_ERROR, "Workspace name metadata cannot be read.") from error


def write_name(directory: Path, root: Path, name: str) -> str:
    value = _validate(name)
    record = _record(directory, root)
    read_name(directory, root)  # refuse to overwrite malformed or inaccessible data
    try:
        record.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=record.parent, delete=False) as f:
                temporary = Path(f.name)
                json.dump({"name": value}, f, ensure_ascii=True)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temporary, record)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
    except OSError as error:
        raise IndexStoreError(INTERNAL_ERROR, "Workspace name could not be saved.") from error
    return value
