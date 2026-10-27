import json
import tomllib
from pathlib import Path

from vyasa.domain import profile as p

SCHEMA_FILE = Path(__file__).resolve().parents[1] / "schemas" / "project-profile.v1.json"


def flatten(data: dict) -> set[str]:
    names = set()
    for key, value in data.items():
        if key == "documentation":
            names |= {f"documentation.{k}" for k in value}
        elif key == "related_projects":
            names.add(key)
            names |= {f"related_projects.{k}" for item in value for k in item}
        else:
            names.add(key)
    return names


def test_the_example_is_a_valid_profile():
    guide = p.profile_guide()
    result = p.validate_profile(tomllib.loads(guide["example"]))
    assert result.status == "valid" and result.problems == ()


def test_the_example_uses_every_documented_field():
    guide = p.profile_guide()
    assert flatten(tomllib.loads(guide["example"])) == {f["name"] for f in guide["fields"]}


def test_limits_and_allowed_values_equal_the_validator_constants():
    fields = {f["name"]: f for f in p.profile_guide()["fields"]}
    assert fields["purpose"]["max_length"] == p.TEXT["purpose"]
    assert fields["name"]["max_length"] == p.TEXT["name"]
    assert fields["lifecycle"]["allowed_values"] == list(p.LIFECYCLES)
    assert fields["related_projects.relation"]["allowed_values"] == list(p.RELATIONS)
    assert all(fields[k]["max_length"] == lim and fields[k]["max_items"] == p.MAX_ITEMS for k, lim in p.LISTS.items())
    assert fields["documentation.entry_point"]["max_length"] == p.MAX_ENTRY_POINT
    assert fields["schema_version"]["required"] and fields["schema_version"]["allowed_values"] == [1]
    assert all(f["description"] for f in fields.values())


def test_guide_basics():
    guide = p.profile_guide()
    assert (guide["path"], guide["format"], guide["max_bytes"]) == (".vyasa/project-profile.toml", "toml", 65536)
    assert guide["schema_file"] == "schemas/project-profile.v1.json"


def test_writer_rules_cover_the_essentials():
    text = " ".join(p.profile_guide()["rules"]).lower()
    for needle in ("once", "omit", "credentials", "absolute paths", "never writes", "next scan"):
        assert needle in text


def test_the_committed_schema_equals_the_generated_one():
    assert json.loads(SCHEMA_FILE.read_text()) == p.json_schema()


def test_the_schema_matches_the_rules():
    schema = p.json_schema()
    props = schema["properties"]
    assert schema["required"] == ["schema_version"] and schema["additionalProperties"] is False
    assert props["purpose"]["maxLength"] == 500 and props["lifecycle"]["enum"] == list(p.LIFECYCLES)
    assert set(props) == {"schema_version", "name", "purpose", "lifecycle", "domain", "tags", "technologies", "owners",
                          "related_projects", "documentation"}


def test_the_example_conforms_to_the_schema_bounds():
    schema, data = p.json_schema(), tomllib.loads(p.profile_guide()["example"])
    assert set(data) <= set(schema["properties"])
    for key, value in data.items():
        spec = schema["properties"][key]
        if "maxLength" in spec:
            assert 1 <= len(value) <= spec["maxLength"]
        if "enum" in spec:
            assert value in spec["enum"]
        if spec.get("type") == "array" and key != "related_projects":
            assert len(value) <= spec["maxItems"] and all(1 <= len(v) <= spec["items"]["maxLength"] for v in value)
    for item in data["related_projects"]:
        assert set(item) == set(schema["properties"]["related_projects"]["items"]["required"])
