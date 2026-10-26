import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("sync_skills", Path(__file__).with_name("sync_skills.py"))
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)

class SerializedReferenceTests(unittest.TestCase):
    def test_only_exact_expected_reference_is_recognized(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            canonical = root / "skills" / "example"
            canonical.mkdir(parents=True)
            agent = root / ".agents" / "skills"
            agent.mkdir(parents=True)
            stub = agent / "example"
            stub.write_text("../../skills/example", encoding="utf8")
            self.assertTrue(sync._is_serialized_reference(stub, canonical))
            stub.write_text("../../other/example", encoding="utf8")
            self.assertFalse(sync._is_serialized_reference(stub, canonical))
            stub.write_text("unique user content", encoding="utf8")
            self.assertFalse(sync._is_serialized_reference(stub, canonical))




class PortableReferenceTests(unittest.TestCase):
    def test_portable_reference_contains_only_relative_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "skills" / "example"
            target.mkdir(parents=True)
            agent = root / ".agents" / "skills"
            agent.mkdir(parents=True)
            link = agent / "example"
            sync.create_link(link, target, "portable")
            self.assertEqual(link.read_text(encoding="utf8"), "../../skills/example")
            self.assertTrue(sync._is_serialized_reference(link, target))
            self.assertTrue(target.is_dir())

    def test_unrelated_file_is_not_replaced_even_with_force(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "skills" / "example"
            target.mkdir(parents=True)
            agent = root / ".agents" / "skills"
            agent.mkdir(parents=True)
            link = agent / "example"
            link.write_text("unique content", encoding="utf8")
            args = SimpleNamespace(dry_run=False, force=True, mode="portable", prune=False)
            with patch.object(sync, "REPO", root):
                result = sync.sync_agent("test", ".agents/skills", [target], args)
            self.assertEqual(link.read_text(encoding="utf8"), "unique content")
            self.assertIn("refusing replacement", result[0])

class CategoryTests(unittest.TestCase):
    def test_duplicate_names_cannot_share_flat_agent_path(self):
        self.assertEqual(sync.find_collisions({"frontend": [Path("frontend/example")], "backend": [Path("backend/example")]}), {"example": ["frontend", "backend"]})

    def test_imported_name_is_retained_but_declared_scope_must_match_home(self):
        with tempfile.TemporaryDirectory() as directory:
            skill = Path(directory) / "frontend" / "react"
            skill.mkdir(parents=True)
            header = "---\nname: react\ndescription: React guidance.\n"
            (skill / "SKILL.md").write_text(header + "metadata:\n  author: upstream\n---\n", encoding="utf8")
            self.assertEqual(sync.validate_skills([skill]), [])
            (skill / "SKILL.md").write_text(header + "metadata:\n  scope: backend\n---\n", encoding="utf8")
            self.assertTrue(any("conflicts with home" in error for error in sync.validate_skills([skill])))

    def test_discovery_reports_legacy_folders_and_team_homes(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("frontend/example", "legacy"):
                folder = root / name
                folder.mkdir(parents=True)
                (folder / "SKILL.md").write_text("example", encoding="utf8")
            with patch.object(sync, "SKILLS_ROOT", root):
                categories, legacy = sync.discover_skills()
            self.assertEqual(list(categories), ["frontend"])
            self.assertEqual([p.name for p in legacy], ["legacy"])

if __name__ == "__main__":
    unittest.main()
