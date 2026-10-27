"""Profile schema version 2: the project declared in depth, as optional nested tables.

One list of field definitions drives the validation, the writer guide, and the JSON Schema, so they cannot drift.
Everything here is pure. A rejected value is never echoed in a problem: reasons are fixed texts.
"""

from __future__ import annotations

import datetime
import re
import unicodedata
from dataclasses import dataclass

MAX_ITEMS = 20
MAX_NAME_IN_PROBLEM = 100
MAX_KEY_IN_PROBLEM = 40

PROJECT_TYPES = ("application", "library", "service", "platform", "tool", "game", "documentation", "other", "unknown")
LIFECYCLE_STATUSES = ("planned", "active", "maintenance", "paused", "deprecated", "archived", "unknown")
CAPABILITY_STATUSES = ("planned", "in_progress", "available", "deprecated", "unknown")
INTERFACE_TYPES = ("api", "mcp", "cli", "event", "library", "file", "other")
CLASSIFICATIONS = ("public", "internal", "confidential", "restricted", "unknown")
REVIEW_FREQUENCIES = ("weekly", "monthly", "quarterly", "yearly", "on_change", "unknown")

_CREDENTIALS = re.compile(r"[a-z][a-z0-9+.\-]*://[^/\s@]*@", re.IGNORECASE)
_EMAIL = re.compile(r"[^\s@]+@[^\s@]+\.[^\s@]+")
_URL = re.compile(r"[a-z][a-z0-9+.\-]*://", re.IGNORECASE)
_LABEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,99}$")
_COMMIT = re.compile(r"^[0-9a-fA-F]{7,64}$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DRIVE = re.compile(r"^[A-Za-z]:")
_UNSAFE_KEY = re.compile(r"[^A-Za-z0-9_.\-]")


@dataclass(frozen=True)
class Field:
    """One declarable value. ``columns`` is set for a list of tables (kind ``rows``)."""

    path: str
    kind: str
    description: str
    limit: int = 0
    count: int = MAX_ITEMS
    values: tuple[str, ...] = ()
    columns: tuple["Field", ...] = ()
    required: bool = False

    @property
    def key(self) -> str:
        return self.path.rpartition(".")[2]


def _safe_key(key: object) -> str:
    """A key from the file, made safe to show: it is attacker-controlled text that agents will read."""
    return _UNSAFE_KEY.sub("_", str(key))[:MAX_KEY_IN_PROBLEM]


def _f(path: str, kind: str, description: str, **extra: object) -> Field:
    return Field(path, kind, description, **extra)  # type: ignore[arg-type]


def _docs(group: str, names: dict[str, str]) -> list[Field]:
    return [_f(f"{group}.{name}", "path", text) for name, text in names.items()]


_PROJECT = [
    _f("project.id", "label", "A label for this project that other tools may use. Vyasa never uses it to identify or merge projects."),
    _f("project.name", "text", "The project's name.", limit=100),
    _f("project.codename", "text", "An internal codename, if there is one.", limit=100),
    _f("project.summary", "text", "One sentence on what the project is.", limit=200),
    _f("project.description", "text", "A short explanation of the project's purpose and boundaries.", limit=1000),
    _f("project.project_type", "enum", "What kind of project this is.", values=PROJECT_TYPES),
    _f("project.domain", "text", "The business or technical domain.", limit=100),
    _f("project.lifecycle_status", "enum", "Where the project stands. Use unknown if you cannot tell.", values=LIFECYCLE_STATUSES),
    _f("project.created_date", "date", "When the project was created, as YYYY-MM-DD."),
    _f("project.last_reviewed_date", "date", "When a person last reviewed this profile, as YYYY-MM-DD."),
    _f("project.owner.team", "contact", "The team responsible for the project. Never an email address or a URL.", limit=100),
    _f("project.owner.role", "contact", "The owning role, for example maintainer. Never an email address or a URL.", limit=100),
    _f("project.owner.contact_reference", "contact", "A channel or handle to reach the owner. Never an email address or a URL.", limit=100),
    _f("project.business.problem_statement", "text", "The problem the project solves.", limit=1000),
    _f("project.business.target_users", "list", "Who the project is for.", limit=200),
    _f("project.business.business_objectives", "list", "What the project is meant to achieve.", limit=300),
    _f("project.business.success_criteria", "list", "How success is recognized.", limit=300),
    _f("project.business.constraints", "list", "Business or engineering constraints.", limit=300),
    _f("project.business.non_goals", "list", "What the project deliberately does not do.", limit=300),
    _f("project.scope.in_scope", "list", "What is in scope.", limit=300),
    _f("project.scope.out_of_scope", "list", "What is out of scope.", limit=300),
    _f("project.scope.known_limitations", "list", "Known limitations.", limit=300),
    _f("project.capabilities", "rows", "What the project does, as capabilities rather than tasks.", count=30, columns=(
        _f("id", "label", "A label for the capability."),
        _f("name", "text", "The capability's name.", limit=100, required=True),
        _f("description", "text", "What it does.", limit=500),
        _f("status", "enum", "Its status, from the project's own records.", values=CAPABILITY_STATUSES),
        _f("source", "path", "The document that describes it, relative to the repository."),
    )),
]
_TECHNOLOGY = [
    _f(f"project.technology.{name}", "list", text, limit=64, count=30)
    for name, text in {
        "declared_languages": "Programming languages the project declares it uses.",
        "declared_frameworks": "Frameworks and libraries the project declares it uses.",
        "declared_platforms": "Platforms it runs on.",
        "declared_datastores": "Databases and other stores it uses.",
        "declared_integrations": "Services it integrates with.",
        "infrastructure": "Infrastructure it needs.",
        "deployment_targets": "Where it is deployed.",
    }.items()
]
_ARCHITECTURE = [
    _f("project.architecture.style", "text", "The architectural style.", limit=100),
    _f("project.architecture.summary", "text", "A short summary of the architecture; keep the detail in its document.", limit=1000),
    _f("project.architecture.entry_points", "list", "Ways the system is started or called.", limit=200),
    _f("project.architecture.major_components", "list", "The major components and their responsibilities.", limit=200),
    _f("project.architecture.trust_boundaries", "list", "Trust boundaries.", limit=200),
    _f("project.architecture.architecture_document", "path", "The architecture document, relative to the repository."),
    _f("project.interfaces", "rows", "Interfaces the project offers or relies on.", count=30, columns=(
        _f("name", "text", "The interface's name.", limit=100, required=True),
        _f("type", "enum", "The kind of interface.", values=INTERFACE_TYPES),
        _f("purpose", "text", "What it is for.", limit=300),
        _f("contract_reference", "path", "The document or schema that defines it, relative to the repository."),
    )),
    _f("project.dependencies.internal_projects", "list", "Other projects it depends on, by remote identity or name.", limit=200),
    _f("project.dependencies.external_services", "list", "External services it depends on.", limit=100, count=30),
    _f("project.dependencies.critical_dependencies", "list", "Dependencies it cannot work without.", limit=100, count=30),
]
_ENGINEERING = [
    _f("project.engineering.openspec.enabled", "tri", "Whether the project uses OpenSpec: true, false, or \"unknown\"."),
    _f("project.engineering.openspec.root", "path", "The OpenSpec directory, relative to the repository."),
    _f("project.engineering.openspec.configuration", "path", "The OpenSpec configuration file, relative to the repository."),
    _f("project.engineering.okf.enabled", "tri", "Whether the project keeps an OKF knowledge bundle: true, false, or \"unknown\"."),
    _f("project.engineering.okf.root", "path", "The knowledge bundle directory, relative to the repository."),
    _f("project.engineering.okf.format_version", "text", "The OKF version the bundle declares.", limit=20),
    _f("project.engineering.agent_instructions", "rows", "Instruction files for coding agents.", count=10, columns=(
        _f("path", "path", "The instruction file, relative to the repository.", required=True),
        _f("purpose", "text", "What it covers.", limit=200),
    )),
    _f("project.engineering.testing.strategy_reference", "path", "The test strategy document, relative to the repository."),
    _f("project.engineering.testing.test_entry_points", "list", "Where tests start or how they are run.", limit=200),
    _f("project.engineering.testing.required_checks", "list", "Checks required before merging.", limit=200),
    _f("project.engineering.security.classification", "enum", "How sensitive the project is.", values=CLASSIFICATIONS),
    _f("project.engineering.security.authentication_summary", "text", "How authentication works, in brief.", limit=500),
    _f("project.engineering.security.sensitive_data_summary", "text", "What sensitive data it handles, in brief. Never include the data.", limit=500),
    _f("project.engineering.security.security_document", "path", "The security document, relative to the repository."),
    *_docs("project.engineering.operations", {
        "deployment_document": "The deployment guide, relative to the repository.",
        "runbook": "The operations runbook, relative to the repository.",
        "monitoring_reference": "The monitoring document, relative to the repository.",
        "backup_recovery_reference": "The backup and recovery document, relative to the repository.",
    }),
]
_DOCUMENTATION = _docs("project.documentation", {
    "overview": "The overview or README, relative to the repository.",
    "vision": "The vision document, relative to the repository.",
    "scope_and_roadmap": "The scope and roadmap document, relative to the repository.",
    "requirements": "The requirements, relative to the repository.",
    "architecture": "The architecture document, relative to the repository.",
    "decisions": "The decision records, relative to the repository.",
    "developer_guide": "The developer guide, relative to the repository.",
    "api_reference": "The API reference, relative to the repository.",
    "operations": "The operations guide, relative to the repository.",
    "security": "The security guidance, relative to the repository.",
    "contributing": "The contribution guide, relative to the repository.",
})
_COLLABORATION = [
    _f("project.collaboration.coding_agents", "list", "Coding agents used on the project.", limit=64, count=10),
    _f("project.collaboration.contribution_rules", "list", "Rules for contributing.", limit=300),
    _f("project.collaboration.branch_policy_reference", "path", "The branching policy document, relative to the repository."),
    _f("project.collaboration.review_policy_reference", "path", "The review policy document, relative to the repository."),
    _f("project.relationships.parent_project_id", "label", "The declared label of a parent project. Never used for identity."),
    _f("project.relationships.related_project_ids", "labels", "Declared labels of related projects. Never used for identity."),
    _f("project.relationships.replaces_project_ids", "labels", "Declared labels of projects this one replaces. Never used for identity."),
    _f("project.relationships.replaced_by_project_id", "label", "The declared label of the project that replaces this one. Never used for identity."),
    _f("project.profile_maintenance.maintained_by", "contact", "Who keeps this profile up to date. Never an email address or a URL.", limit=100),
    _f("project.profile_maintenance.review_frequency", "enum", "How often it is reviewed.", values=REVIEW_FREQUENCIES),
    _f("project.profile_maintenance.last_verified_commit", "commit", "The commit at which the profile was last checked, 7 to 64 hexadecimal characters."),
    _f("project.profile_maintenance.verification_notes", "text", "Notes from the last check.", limit=500),
]

FIELDS: tuple[Field, ...] = tuple(_PROJECT + _TECHNOLOGY + _ARCHITECTURE + _ENGINEERING + _DOCUMENTATION + _COLLABORATION)
LEAVES: dict[str, Field] = {f.path: f for f in FIELDS}
TABLES: frozenset[str] = frozenset(
    ".".join(f.path.split(".")[:n]) for f in FIELDS for n in range(1, len(f.path.split(".")))
)


# -- the kinds -----------------------------------------------------------------------------------------------------


def _clean(text: str) -> str:
    return "".join(ch for ch in text if unicodedata.category(ch) != "Cc").strip()


def _text(value: object, limit: int) -> tuple[str | None, str | None]:
    if not isinstance(value, str):
        return None, "must be text"
    cleaned = _clean(value)
    if not 1 <= len(cleaned) <= limit:
        return None, f"must be 1 to {limit} characters"
    if _CREDENTIALS.search(cleaned):
        return None, "must not contain a URL with credentials"
    return cleaned, None


def _contact(value: object, limit: int) -> tuple[str | None, str | None]:
    text, problem = _text(value, limit)
    if problem or text is None:
        return None, problem
    if _EMAIL.search(text) or _URL.search(text):
        return None, "must not be an email address or a URL"
    return text, None


def _path(value: object) -> tuple[str | None, str | None]:
    text, problem = _text(value, 200)
    if problem or text is None:
        return None, problem
    normal = text.replace("\\", "/")
    if normal.startswith("/") or _DRIVE.match(normal) or "://" in normal or ".." in normal.split("/"):
        return None, "must be a relative path inside the repository"
    return text, None


def _label(value: object) -> tuple[str | None, str | None]:
    if not isinstance(value, str) or not _LABEL.match(value):
        return None, "must be a label of letters, digits, and . _ : - up to 100 characters"
    return value, None


def _date(value: object) -> tuple[str | None, str | None]:
    if type(value) is datetime.date:
        return value.isoformat(), None
    if isinstance(value, str) and _DATE.match(value):
        try:
            return datetime.date.fromisoformat(value).isoformat(), None
        except ValueError:
            pass
    return None, "must be a calendar date written YYYY-MM-DD"


def _tri(value: object) -> tuple[object, str | None]:
    if value is True or value is False or value == "unknown":
        return value, None
    return None, 'must be true, false, or "unknown"'


def _commit(value: object) -> tuple[str | None, str | None]:
    if isinstance(value, str) and _COMMIT.match(value):
        return value.lower(), None
    return None, "must be 7 to 64 hexadecimal characters"


def _enum(value: object, values: tuple[str, ...]) -> tuple[str | None, str | None]:
    if isinstance(value, str) and value in values:
        return value, None
    return None, f"must be one of {', '.join(values)}"


def _scalar(field: Field, value: object) -> tuple[object, str | None]:
    kind = field.kind
    if kind == "text":
        return _text(value, field.limit)
    if kind == "contact":
        return _contact(value, field.limit)
    if kind == "path":
        return _path(value)
    if kind == "label":
        return _label(value)
    if kind == "date":
        return _date(value)
    if kind == "tri":
        return _tri(value)
    if kind == "commit":
        return _commit(value)
    return _enum(value, field.values)


def _list(field: Field, value: object) -> tuple[list[str] | None, str | None]:
    if not isinstance(value, list):
        return None, "must be a list of text"
    if len(value) > field.count:
        return None, f"at most {field.count} items"
    items: list[str] = []
    for index, item in enumerate(value, 1):
        cleaned, problem = _label(item) if field.kind == "labels" else _text(item, field.limit)
        if problem or cleaned is None:
            return None, f"item {index} {problem}"
        if cleaned not in items:
            items.append(cleaned)
    return items, None


def _rows(field: Field, value: object, problems: list[tuple[str, str]]) -> list[dict] | None:
    if not isinstance(value, list) or len(value) > field.count:
        problems.append((field.path, f"must be a list of at most {field.count} tables"))
        return None
    allowed = {c.key: c for c in field.columns}
    kept: list[dict] = []
    for index, row in enumerate(value, 1):
        where = f"{field.path}[{index}]"
        if not isinstance(row, dict):
            problems.append((where, "must be a table"))
            continue
        clean: dict = {}
        bad = False
        for key in sorted(set(row) - set(allowed)):
            problems.append((f"{where}.{_safe_key(key)}", "unknown field"))
            bad = True
        for key, column in allowed.items():
            if key not in row:
                if column.required:
                    problems.append((f"{where}.{key}", "is required"))
                    bad = True
                continue
            cleaned, problem = _scalar(column, row[key])
            if problem:
                problems.append((f"{where}.{key}", problem))
                bad = True
            else:
                clean[key] = cleaned
        if not bad:
            kept.append(clean)
    return kept or None


# -- validation ----------------------------------------------------------------------------------------------------


def _walk(table: dict, prefix: str, fields: dict, problems: list[tuple[str, str]]) -> None:
    for key, value in table.items():
        path = f"{prefix}{key}"
        leaf = LEAVES.get(path)
        if leaf is not None:
            if leaf.kind == "rows":
                rows = _rows(leaf, value, problems)
                if rows:
                    fields[path] = rows
            elif leaf.kind in ("list", "labels"):
                items, problem = _list(leaf, value)
                if problem:
                    problems.append((path, problem))
                else:
                    fields[path] = items
            else:
                cleaned, problem = _scalar(leaf, value)
                if problem:
                    problems.append((path, problem))
                else:
                    fields[path] = cleaned
        elif path in TABLES:
            if isinstance(value, dict):
                _walk(value, path + ".", fields, problems)
            else:
                problems.append((path, "must be a table"))
        else:
            problems.append((f"{prefix}{_safe_key(key)}", "unknown field"))


def validate_v2(data: dict) -> tuple[dict, list[tuple[str, str]]]:
    """Validate a parsed version 2 profile. Returns the valid fields (dotted names) and the problems."""
    fields: dict = {}
    problems: list[tuple[str, str]] = []
    for key in sorted(set(data) - {"schema_version", "project"}):
        problems.append((_safe_key(key), "unknown field"))
    if "project" in data:
        if isinstance(data["project"], dict):
            _walk(data["project"], "project.", fields, problems)
        else:
            problems.append(("project", "must be a table"))
    return fields, problems


# -- the guide and the schema --------------------------------------------------------------------------------------

_KIND_NAMES = {
    "text": "text", "contact": "text", "path": "text (relative path)", "label": "text (label)", "date": "date (YYYY-MM-DD)",
    "tri": 'true, false, or "unknown"', "commit": "text (hexadecimal commit)", "enum": "text", "list": "list of text",
    "labels": "list of labels", "rows": "list of tables",
}


def _guide_field(field: Field, name: str | None = None) -> dict:
    entry: dict = {"name": name or field.path, "type": _KIND_NAMES[field.kind], "required": field.required, "description": field.description}
    if field.kind in ("text", "contact", "list"):
        entry["max_length"] = field.limit
    if field.kind in ("list", "labels"):
        entry["max_items"] = field.count
    if field.kind == "rows":
        entry["max_rows"] = field.count
    if field.kind == "path":
        entry["max_length"] = 200
    if field.kind == "enum":
        entry["allowed_values"] = list(field.values)
    return entry


def guide_fields() -> list[dict]:
    """Every field with its limits, nested table columns included as ``path.key``."""
    entries: list[dict] = []
    for field in FIELDS:
        entries.append(_guide_field(field))
        entries += [_guide_field(c, f"{field.path}.{c.key}") for c in field.columns]
    return entries


def _schema_for(field: Field) -> dict:
    kind = field.kind
    base: dict = {"description": field.description}
    if kind in ("text", "contact"):
        return {"type": "string", "minLength": 1, "maxLength": field.limit, **base}
    if kind == "path":
        return {"type": "string", "minLength": 1, "maxLength": 200, **base}
    if kind == "label":
        return {"type": "string", "pattern": _LABEL.pattern, **base}
    if kind == "date":
        return {"type": "string", "format": "date", **base}
    if kind == "tri":
        return {"enum": [True, False, "unknown"], **base}
    if kind == "commit":
        return {"type": "string", "pattern": _COMMIT.pattern, **base}
    if kind == "enum":
        return {"enum": list(field.values), **base}
    if kind in ("list", "labels"):
        item = {"type": "string", "pattern": _LABEL.pattern} if kind == "labels" else {"type": "string", "minLength": 1, "maxLength": field.limit}
        return {"type": "array", "maxItems": field.count, "uniqueItems": True, "items": item, **base}
    required = [c.key for c in field.columns if c.required]
    row: dict = {"type": "object", "additionalProperties": False, "properties": {c.key: _schema_for(c) for c in field.columns}}
    if required:
        row["required"] = required
    return {"type": "array", "maxItems": field.count, "items": row, **base}


def project_schema() -> dict:
    """The ``project`` table as a JSON Schema object, nested like the TOML."""
    root: dict = {"type": "object", "additionalProperties": False, "properties": {}}
    for field in FIELDS:
        node = root
        for part in field.path.split(".")[1:-1]:
            node = node["properties"].setdefault(part, {"type": "object", "additionalProperties": False, "properties": {}})
        node["properties"][field.key] = _schema_for(field)
    return root
