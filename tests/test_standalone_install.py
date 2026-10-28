import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "build_mcp.py"
spec = importlib.util.spec_from_file_location("build_mcp", SCRIPT)
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


def bundles(tmp_path):
    made = {}
    for name in ("vyasa", "vyasa-mcp"):
        folder = tmp_path / "dist" / name
        folder.mkdir(parents=True)
        (folder / name).write_text("new", encoding="utf-8")
        made[name] = folder
    return made


def example(tmp_path):
    path = tmp_path / "example.toml"
    path.write_text("[workspace]\nroots = []\n", encoding="utf-8")
    return path


def test_layout_has_both_bundles_and_a_seeded_data_folder(tmp_path):
    root = tmp_path / "out" / "Vyasa"
    build.install(root, bundles(tmp_path), example(tmp_path))
    assert (root / "vyasa" / "vyasa").is_file()
    assert (root / "vyasa-mcp" / "vyasa-mcp").is_file()
    assert (root / "data" / "config.toml").read_text(encoding="utf-8").startswith("[workspace]")


def test_rebuild_replaces_bundles_and_keeps_data(tmp_path):
    root = tmp_path / "out" / "Vyasa"
    (root / "vyasa").mkdir(parents=True)
    (root / "vyasa" / "stale").write_text("old", encoding="utf-8")
    (root / "data").mkdir()
    (root / "data" / "config.toml").write_bytes(b"mine")
    (root / "data" / "index.sqlite3").write_bytes(b"index")
    build.install(root, bundles(tmp_path), example(tmp_path))
    assert not (root / "vyasa" / "stale").exists()
    assert (root / "data" / "config.toml").read_bytes() == b"mine"
    assert (root / "data" / "index.sqlite3").read_bytes() == b"index"
