import pytest

from vyasa.application.scanning import checkout_scan as module
from vyasa.application.scanning.checkout_scan import scan_checkout
from vyasa.application.scanning.file_composition import compose, default_file_types
from vyasa.application.scanning.languages import detect_languages
from vyasa.domain.file_composition import WalkLimits, documentation_only
from vyasa.domain.languages import CheckoutScan

TYPES = default_file_types()


def tree(root, *names):
    for name in names:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    return root


def mixed(tmp_path):
    return tree(tmp_path, "a.py", "b.rs", "c.h", "d.md", "e.txt", "x/f.go", "x/g.png", "Cargo.toml")


def test_languages_sum_to_the_code_count(tmp_path):
    scan = scan_checkout(mixed(tmp_path), TYPES)
    assert isinstance(scan, CheckoutScan)
    assert sum(n for _, n in scan.languages.files_detected) == scan.composition.code == 4
    assert (scan.composition.documentation, scan.composition.other) == (1, 3)


def test_languages_sum_to_the_code_count_when_capped(tmp_path):
    scan = scan_checkout(mixed(tmp_path), TYPES, WalkLimits(max_entries=4))
    assert not scan.composition.complete and scan.composition.stopped_by == scan.languages.stopped_by == "entries"
    assert sum(n for _, n in scan.languages.files_detected) == scan.composition.code


def test_both_results_share_one_evidence(tmp_path):
    scan = scan_checkout(mixed(tmp_path), TYPES, exclusions=["zeta", "alpha"])
    assert scan.composition.evidence == scan.languages.evidence
    assert scan.composition.evidence.exclusions == ("alpha", "zeta")


def test_the_walk_happens_once(tmp_path, monkeypatch):
    calls = []
    real = module.walk_checkout

    def counting(*args, **kwargs):
        calls.append(1)
        return real(*args, **kwargs)

    monkeypatch.setattr(module, "walk_checkout", counting)
    scan_checkout(mixed(tmp_path), TYPES)
    assert len(calls) == 1


def test_public_functions_are_views_of_the_scan(tmp_path):
    root = mixed(tmp_path)
    scan = scan_checkout(root, TYPES)
    assert compose(root, TYPES) == scan.composition
    assert detect_languages(root, TYPES) == scan.languages


def test_missing_root_raises(tmp_path):
    with pytest.raises(ValueError):
        scan_checkout(tmp_path / "nope", TYPES)


@pytest.mark.parametrize("code,docs,complete,expected", [
    (0, 4, True, True), (1, 4, True, False), (0, 0, True, False), (0, 4, False, None), (3, 0, False, None),
])
def test_documentation_only_rule(code, docs, complete, expected):
    assert documentation_only(code, docs, complete) is expected
