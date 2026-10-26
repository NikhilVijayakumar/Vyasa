import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_requirements as vr  # noqa: E402

DIMS = vr.DIMENSIONS
FEATURE = """@FR-001 @P1 @pkg
Feature: Thing
  Statement.

  @FR-001-S1
  Scenario: Works
    Given a thing
    When it runs
    Then it works
    And it is quick
"""


def grill(skip: str | None = None) -> str:
    out = ["# Grill"]
    for number, dim in enumerate(DIMS, 1):
        if dim == skip:
            continue
        out += [f"## {dim}", "", f"**Q{number}. A question?**", "", "- **Recommendation:** do it", "- **Why:** because",
                "- **Status:** Recommended", "- **Feeds:** FR-001", ""]
    return "\n".join(out)


class VerifyRequirementsTests(unittest.TestCase):
    def tree(self, feature=FEATURE, grill_text=None, owns="FR-001, NFR-001", second_owner=False) -> Path:
        root = Path(tempfile.mkdtemp())
        (root / "functional-requirements.md").write_text("| FR-001 | Area | P1 |\n", encoding="utf-8")
        (root / "non-functional-requirements.md").write_text("## NFR-001 — Quality\n", encoding="utf-8")
        for name in ("pkg", "other") if second_owner else ("pkg",):
            pkg = root / name
            (pkg / "features").mkdir(parents=True)
            (pkg / "requirement.md").write_text(f"# R\n\n- **Owns:** {owns}\n", encoding="utf-8")
            (pkg / "diagrams.md").write_text("# D\n", encoding="utf-8")
            (pkg / "grill-log.md").write_text(grill_text or grill(), encoding="utf-8")
            (pkg / "features" / "a.feature").write_text(feature, encoding="utf-8")
        return root

    def test_valid_tree_passes(self):
        errors, stats = vr.verify(self.tree())
        self.assertEqual(errors, [])
        self.assertEqual(stats["scenarios"], 1)

    def test_scenario_without_then_fails(self):
        errors, _ = vr.verify(self.tree(feature=FEATURE.replace("    Then it works\n    And it is quick\n", "")))
        self.assertTrue(any("no Then" in e for e in errors), errors)

    def test_outline_without_examples_fails(self):
        bad = FEATURE.replace("Scenario: Works", "Scenario Outline: Works").replace("a thing", "a <thing>")
        errors, _ = vr.verify(self.tree(feature=bad))
        self.assertTrue(any("no Examples" in e for e in errors), errors)

    def test_duplicate_scenario_title_fails(self):
        errors, _ = vr.verify(self.tree(feature=FEATURE + "\n  Scenario: Works\n    Given x\n    When y\n    Then z\n"))
        self.assertTrue(any("duplicate scenario title" in e for e in errors), errors)

    def test_missing_dimension_fails(self):
        errors, _ = vr.verify(self.tree(grill_text=grill(skip="Data")))
        self.assertTrue(any("missing dimension 'Data'" in e for e in errors), errors)

    def test_unowned_requirement_fails(self):
        errors, _ = vr.verify(self.tree(owns="FR-001"))
        self.assertTrue(any("NFR-001: not owned" in e for e in errors), errors)

    def test_requirement_owned_twice_fails(self):
        errors, _ = vr.verify(self.tree(second_owner=True))
        self.assertTrue(any("owned by several packages" in e for e in errors), errors)

    def test_owned_fr_needs_a_tagged_feature(self):
        errors, _ = vr.verify(self.tree(feature=FEATURE.replace("@FR-001 ", "")))
        self.assertTrue(any("no feature file tagged @FR-001" in e for e in errors), errors)

    def test_decisions_report_lists_decision_needed_only(self):
        text = grill().replace("- **Status:** Recommended", "- **Status:** Decision needed", 1)
        root = self.tree(grill_text=text)
        report = vr.decisions_markdown(root)
        self.assertIn("## pkg", report)
        self.assertEqual(sum(1 for line in report.splitlines() if line.startswith("| Q")), 2)  # header plus one decision


if __name__ == "__main__":
    unittest.main()
