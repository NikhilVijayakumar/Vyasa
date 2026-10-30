import io
import json

from vyasa.adapters.cli.main import main
from vyasa.application.scanning.frameworks import default_registry


def test_catalog_matches_registry_without_index(tmp_path):
    out, err = io.StringIO(), io.StringIO()
    code = main(["query", "technologies"], {"VYASA_HOME": str(tmp_path)}, out, err)
    assert code == 0 and not err.getvalue()
    data = json.loads(out.getvalue())["data"]
    registry = default_registry()
    assert data["registry_version"] == registry.version
    assert {entry["key"] for entry in data["technologies"]} == set(registry.keys())
    assert data["technologies"] == sorted(data["technologies"], key=lambda e: (e["name"].casefold(), e["key"]))
    assert all(set(entry) == {"key", "name", "category", "ecosystem"} for entry in data["technologies"])
    assert not (tmp_path / "index.sqlite3").exists()
