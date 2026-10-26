import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_knowledge as vk  # noqa: E402

PROFILE = json.loads((Path(__file__).resolve().parents[1] / "knowledge" / "profile.json").read_text(encoding="utf-8"))
CONCEPT = """---
type: Concept
title: Thing
description: One thing.
status: draft
generated: { by: human:someone, at: 2026-10-26T00:00:00Z }
---

# Definition

See [other](/concepts/other.md).
"""


class VerifyKnowledgeTests(unittest.TestCase):
    def bundle(self, concept: str = CONCEPT, index: str = "# Concepts\n\n* [Thing](thing.md) - One thing.\n") -> Path:
        root = Path(tempfile.mkdtemp())
        (root / "profile.json").write_text(json.dumps(PROFILE), encoding="utf-8")
        (root / "index.md").write_text('---\nokf_version: "0.2"\n---\n\n* [Concepts](concepts/) - c\n', encoding="utf-8")
        (root / "concepts").mkdir()
        (root / "concepts" / "index.md").write_text(index, encoding="utf-8")
        (root / "concepts" / "thing.md").write_text(concept, encoding="utf-8")
        return root

    def test_valid_bundle_passes_and_broken_internal_link_only_warns(self):
        errors, warnings = vk.verify(self.bundle())
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)

    def test_link_out_of_bundle_fails(self):
        errors, _ = vk.verify(self.bundle(CONCEPT.replace("/concepts/other.md", "../../openspec/specs/x.md")))
        self.assertTrue(any("outside the knowledge bundle" in e for e in errors), errors)

    def test_forbidden_path_mention_fails(self):
        errors, _ = vk.verify(self.bundle(CONCEPT + "\nDefined in docs/requirements/x.md.\n"))
        self.assertTrue(any("docs/requirements/" in e for e in errors), errors)

    def test_missing_field_wrong_folder_and_bad_actor_fail(self):
        bad = CONCEPT.replace("type: Concept", "type: Decision").replace("description: One thing.\n", "").replace("human:someone", "someone")
        errors, _ = vk.verify(self.bundle(bad))
        for expected in ("missing required field 'description'", "belongs in 'decisions/'", "actor convention"):
            self.assertTrue(any(expected in e for e in errors), (expected, errors))

    def test_unlisted_concept_fails(self):
        errors, _ = vk.verify(self.bundle(index="# Concepts\n"))
        self.assertTrue(any("does not list 'thing.md'" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
