"""The project profile: what a repository declares about itself. Pure validation; nothing here touches a file."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

PROFILE_PATH = ".vyasa/project-profile.toml"
SCHEMA_VERSION = 1
MAX_BYTES = 65536

VALID = "valid"
INVALID = "invalid"
UNSUPPORTED = "unsupported"
UNREADABLE = "unreadable"
ABSENT = "absent"
STATUSES = (VALID, INVALID, UNSUPPORTED, UNREADABLE, ABSENT)

LIFECYCLES = ("active", "maintenance", "experimental", "deprecated", "archived")
RELATIONS = ("depends_on", "used_by", "related")
MAX_ITEMS = 20

# Text fields: (key, maximum characters).
TEXT = {"name": 100, "purpose": 500}
# List-of-text fields: (key, maximum characters per item).
LISTS = {"domain": 64, "tags": 64, "technologies": 64, "owners": 100}
MAX_IDENTITY = 200
MAX_ENTRY_POINT = 200
KNOWN = {"schema_version", "lifecycle", "related_projects", "documentation", *TEXT, *LISTS}
_DRIVE = re.compile(r"^[A-Za-z]:")


@dataclass(frozen=True)
class ProfileResult:
    """The outcome of reading one profile. ``fields`` holds only values that passed validation."""

    status: str
    fields: dict = field(default_factory=dict)
    problems: tuple[tuple[str, str], ...] = ()


def clean(text: str) -> str:
    """Remove control characters and trim."""
    return "".join(ch for ch in text if unicodedata.category(ch) != "Cc").strip()


def _text(value: object, limit: int) -> tuple[str | None, str | None]:
    if not isinstance(value, str):
        return None, "must be text"
    cleaned = clean(value)
    if not 1 <= len(cleaned) <= limit:
        return None, f"must be 1 to {limit} characters"
    return cleaned, None


def _entry_point(value: object) -> tuple[str | None, str | None]:
    text, problem = _text(value, MAX_ENTRY_POINT)
    if problem or text is None:
        return None, problem
    normal = text.replace("\\", "/")
    if normal.startswith("/") or _DRIVE.match(normal) or "://" in normal or ".." in normal.split("/"):
        return None, "must be a relative path inside the repository"
    return text, None


def validate_profile(data: object) -> ProfileResult:
    """Validate a parsed profile field by field. Valid fields are kept when others fail."""
    if not isinstance(data, dict):
        return ProfileResult(UNREADABLE, {}, (("profile", "must be a table"),))
    version = data.get("schema_version")
    if isinstance(version, bool) or version != SCHEMA_VERSION:
        return ProfileResult(UNSUPPORTED, {}, (("schema_version", f"missing or unsupported (expected {SCHEMA_VERSION})"),))

    fields: dict = {}
    problems: list[tuple[str, str]] = []

    for key in sorted(set(data) - KNOWN):
        problems.append((key, "unknown field"))

    for key, limit in TEXT.items():
        if key in data:
            value, problem = _text(data[key], limit)
            if problem:
                problems.append((key, problem))
            else:
                fields[key] = value

    if "lifecycle" in data:
        value = data["lifecycle"]
        if value in LIFECYCLES and isinstance(value, str):
            fields["lifecycle"] = value
        else:
            problems.append(("lifecycle", f"must be one of {', '.join(LIFECYCLES)}"))

    for key, limit in LISTS.items():
        if key in data:
            raw = data[key]
            if not isinstance(raw, list):
                problems.append((key, "must be a list of text"))
            elif len(raw) > MAX_ITEMS:
                problems.append((key, f"at most {MAX_ITEMS} items"))
            else:
                items, bad = [], None
                for index, item in enumerate(raw):
                    value, problem = _text(item, limit)
                    if problem:
                        bad = f"item {index + 1} {problem}"
                        break
                    if value not in items:
                        items.append(value)
                if bad:
                    problems.append((key, bad))
                else:
                    fields[key] = items

    if "related_projects" in data:
        raw = data["related_projects"]
        if not isinstance(raw, list) or len(raw) > MAX_ITEMS:
            problems.append(("related_projects", f"must be a list of at most {MAX_ITEMS} tables"))
        else:
            related = []
            for index, item in enumerate(raw):
                where = f"related_projects[{index + 1}]"
                if not isinstance(item, dict) or set(item) - {"identity", "relation"}:
                    problems.append((where, "must be a table with only identity and relation"))
                    continue
                identity, problem = _text(item.get("identity"), MAX_IDENTITY)
                if problem:
                    problems.append((f"{where}.identity", problem))
                elif item.get("relation") not in RELATIONS:
                    problems.append((f"{where}.relation", f"must be one of {', '.join(RELATIONS)}"))
                else:
                    related.append({"identity": identity, "relation": item["relation"]})
            if related:
                fields["related_projects"] = related

    if "documentation" in data:
        table = data["documentation"]
        if not isinstance(table, dict):
            problems.append(("documentation", "must be a table"))
        else:
            for key in sorted(set(table) - {"entry_point"}):
                problems.append((f"documentation.{key}", "unknown field"))
            if "entry_point" in table:
                value, problem = _entry_point(table["entry_point"])
                if problem:
                    problems.append(("documentation.entry_point", problem))
                else:
                    fields["documentation.entry_point"] = value

    return ProfileResult(VALID if not problems else INVALID, fields, tuple(problems))
