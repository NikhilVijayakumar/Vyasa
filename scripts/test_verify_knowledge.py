import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
    def bundle(self, concept: str = CONCEPT, index: str = "# Concepts\n\n* [Thing](thing.md) - One thing.\n", **profile: Any) -> Path:
        root = Path(tempfile.mkdtemp())
        (root / "profile.json").write_text(json.dumps({**PROFILE, **profile}), encoding="utf-8")
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

    def test_concept_over_the_line_limit_fails(self):
        errors, _ = vk.verify(self.bundle(CONCEPT + "\nline\n" * (PROFILE["max_lines"] + 1)))
        self.assertTrue(any("split it into parts" in e for e in errors), errors)

    def test_stale_after_in_the_past_warns(self):
        stale = CONCEPT.replace("status: draft\n", "status: draft\nstale_after: 2026-01-01T00:00:00Z\n")
        _, warnings = vk.verify(self.bundle(stale), now=datetime(2026, 6, 1, tzinfo=timezone.utc))
        self.assertTrue(any("stale since" in w for w in warnings), warnings)
        _, warnings = vk.verify(self.bundle(stale), now=datetime(2025, 6, 1, tzinfo=timezone.utc))
        self.assertFalse(any("stale since" in w for w in warnings), warnings)

    def test_bad_stale_after_fails(self):
        bad = CONCEPT.replace("status: draft\n", "status: draft\nstale_after: someday\n")
        errors, _ = vk.verify(self.bundle(bad))
        self.assertTrue(any("stale_after" in e for e in errors), errors)

    def test_required_sections_missing_empty_and_extra(self):
        rules = {"required_sections": {"Concept": ["Definition", "Examples"]}}
        errors, _ = vk.verify(self.bundle(**rules))
        self.assertTrue(any("missing required section 'Examples'" in e for e in errors), errors)
        empty = CONCEPT + "\n# Examples\n\n# Related\n\nx\n"
        errors, _ = vk.verify(self.bundle(empty, **rules))
        self.assertTrue(any("required section 'Examples' is empty" in e for e in errors), errors)
        full = CONCEPT + "\n# Examples\n\nOne.\n\n# Related\n\nx\n"
        errors, _ = vk.verify(self.bundle(full, **rules))
        self.assertEqual(errors, [])

    def test_fenced_hash_line_is_not_a_heading(self):
        fenced = CONCEPT + "\n```sh\n# Examples\nls\n```\n"
        errors, _ = vk.verify(self.bundle(fenced, required_sections={"Concept": ["Examples"]}))
        self.assertTrue(any("missing required section 'Examples'" in e for e in errors), errors)

    def test_forbidden_words_hit_miss_and_invalid_pattern(self):
        words = {"forbidden_words": [r"\bthis change\b"]}
        errors, _ = vk.verify(self.bundle(CONCEPT + "\nAs this change adds it.\n", **words))
        self.assertTrue(any("forbidden pattern" in e and "thing.md" in e for e in errors), errors)
        self.assertNotIn("As this change", "".join(errors))
        errors, _ = vk.verify(self.bundle(**words))
        self.assertEqual(errors, [])
        errors, _ = vk.verify(self.bundle(forbidden_words=["("]))
        self.assertTrue(any("not a valid regular expression" in e for e in errors), errors)

    def test_stable_concept_may_not_have_open_questions(self):
        asked = CONCEPT + "\n# Open questions\n\nWhy?\n"
        errors, _ = vk.verify(self.bundle(asked.replace("status: draft", "status: stable")))
        self.assertTrue(any("Open questions" in e for e in errors), errors)
        errors, _ = vk.verify(self.bundle(asked))
        self.assertEqual(errors, [])

    def test_deprecated_decision_names_an_existing_decision(self):
        decision = CONCEPT.replace("type: Concept", "type: Decision")
        old = decision.replace("status: draft", "status: deprecated")
        root = self.bundle(required_sections={})
        (root / "index.md").write_text('---\nokf_version: "0.2"\n---\n\n* [Concepts](concepts/) - c\n* [Decisions](decisions/) - d\n', encoding="utf-8")
        (root / "decisions").mkdir()
        (root / "decisions" / "index.md").write_text("# D\n\n* [Old](old.md) - o\n* [New](new.md) - n\n", encoding="utf-8")
        (root / "decisions" / "new.md").write_text(decision, encoding="utf-8")
        target = root / "decisions" / "old.md"
        target.write_text(old, encoding="utf-8")
        errors, _ = vk.verify(root)
        self.assertTrue(any("deprecated decision has no superseded_by" in e for e in errors), errors)
        for pointer, expected in (("/decisions/new.md", None), ("/decisions/gone.md", "does not exist"), ("/concepts/thing.md", "not a Decision"), ("../../x.md", "outside")):
            target.write_text(old.replace("status: deprecated\n", f"status: deprecated\nsuperseded_by: {pointer}\n"), encoding="utf-8")
            errors, _ = vk.verify(root)
            if expected:
                self.assertTrue(any(expected in e for e in errors), (pointer, errors))
            else:
                self.assertEqual(errors, [])

    def test_profile_without_the_new_keys_still_verifies(self):
        old_profile = {k: v for k, v in PROFILE.items() if k not in ("required_sections", "forbidden_words")}
        root = self.bundle(CONCEPT + "\nThis change is fine.\n# Open questions\n\nx\n")
        (root / "profile.json").write_text(json.dumps(old_profile), encoding="utf-8")
        errors, _ = vk.verify(root)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
