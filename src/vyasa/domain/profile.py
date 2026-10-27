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


# -- the guide and the schema file, built from the constants above so they cannot drift ------------------------

SCHEMA_FILE = "schemas/project-profile.v1.json"
DESCRIPTIONS = {
    "schema_version": "Always 1.",
    "name": "The project's own name, if it differs from its folder name.",
    "purpose": "One or two sentences on what the project is for. State only what the repository shows.",
    "lifecycle": "Where the project stands. Omit if you cannot tell.",
    "domain": "The business or problem areas the project serves, for example payments.",
    "tags": "Short free-form labels.",
    "technologies": "Main languages, frameworks, and services the project is built with.",
    "owners": "Teams or people responsible. Use names or handles, never contact secrets.",
    "related_projects": "Other projects this one depends on, is used by, or is related to.",
    "related_projects.identity": "The other project's remote identity (host/organization/repository) or its name.",
    "related_projects.relation": "How the other project relates to this one.",
    "documentation.entry_point": "The main documentation file, as a path inside the repository.",
}
EXAMPLE = '''schema_version = 1
name = "Billing API"
purpose = "Issues and reconciles customer invoices for the storefront."
lifecycle = "active"
domain = ["payments"]
tags = ["python", "api"]
technologies = ["FastAPI", "PostgreSQL"]
owners = ["team-billing"]
related_projects = [{ identity = "github.com/acme/ledger", relation = "depends_on" }]

[documentation]
entry_point = "docs/index.md"
'''
WRITER_RULES = (
    f"Write the file once, at {PROFILE_PATH} in the repository root, creating the .vyasa folder if needed.",
    "Include only fields you can support from what the repository shows. Omit any field you do not know; an omitted field is better than a guess.",
    "Do not include credentials, tokens, private contact details, URLs with credentials, or absolute paths.",
    "Keep every value within the limits; a field that breaks a rule is dropped and reported, the others are kept.",
    "Do not change any other file for Vyasa. Vyasa reads the profile on its next scan and never writes it.",
    "Treat the file as a declaration for people to review: tell the maintainer what you wrote so they can correct and commit it.",
)


def _field(name: str, kind: str, required: bool = False, **extra: object) -> dict:
    return {"name": name, "type": kind, "required": required, "description": DESCRIPTIONS[name], **extra}


def profile_guide() -> dict:
    """Everything a writer needs to produce a valid profile, built from the validation constants."""
    fields = [_field("schema_version", "integer", True, allowed_values=[SCHEMA_VERSION])]
    fields += [_field(key, "text", max_length=limit) for key, limit in TEXT.items()]
    fields.append(_field("lifecycle", "text", allowed_values=list(LIFECYCLES)))
    fields += [_field(key, "list of text", max_items=MAX_ITEMS, max_length=limit) for key, limit in LISTS.items()]
    fields.append(_field("related_projects", "list of tables", max_items=MAX_ITEMS))
    fields.append(_field("related_projects.identity", "text", True, max_length=MAX_IDENTITY))
    fields.append(_field("related_projects.relation", "text", True, allowed_values=list(RELATIONS)))
    fields.append(_field("documentation.entry_point", "text", max_length=MAX_ENTRY_POINT))
    return {
        "path": PROFILE_PATH,
        "format": "toml",
        "schema_version": SCHEMA_VERSION,
        "max_bytes": MAX_BYTES,
        "schema_file": SCHEMA_FILE,
        "fields": fields,
        "example": EXAMPLE,
        "rules": list(WRITER_RULES),
    }


def _text_schema(limit: int, name: str) -> dict:
    return {"type": "string", "minLength": 1, "maxLength": limit, "description": DESCRIPTIONS[name]}


def _list_schema(limit: int, name: str) -> dict:
    return {
        "type": "array", "maxItems": MAX_ITEMS, "uniqueItems": True,
        "items": {"type": "string", "minLength": 1, "maxLength": limit}, "description": DESCRIPTIONS[name],
    }


def json_schema() -> dict:
    """The profile as a JSON Schema, for editors and validators that read TOML through JSON."""
    properties = {"schema_version": {"const": SCHEMA_VERSION, "description": DESCRIPTIONS["schema_version"]}}
    properties.update({key: _text_schema(limit, key) for key, limit in TEXT.items()})
    properties["lifecycle"] = {"enum": list(LIFECYCLES), "description": DESCRIPTIONS["lifecycle"]}
    properties.update({key: _list_schema(limit, key) for key, limit in LISTS.items()})
    properties["related_projects"] = {
        "type": "array", "maxItems": MAX_ITEMS, "description": DESCRIPTIONS["related_projects"],
        "items": {
            "type": "object", "additionalProperties": False, "required": ["identity", "relation"],
            "properties": {
                "identity": _text_schema(MAX_IDENTITY, "related_projects.identity"),
                "relation": {"enum": list(RELATIONS), "description": DESCRIPTIONS["related_projects.relation"]},
            },
        },
    }
    properties["documentation"] = {
        "type": "object", "additionalProperties": False,
        "properties": {"entry_point": _text_schema(MAX_ENTRY_POINT, "documentation.entry_point")},
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Vyasa project profile, schema version 1",
        "type": "object",
        "additionalProperties": False,
        "required": ["schema_version"],
        "properties": properties,
    }
