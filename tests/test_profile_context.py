import json
from dataclasses import replace
from datetime import timedelta

import pytest
from test_frameworks_query import REGISTRY, fw, mf
from test_language_query import report, scanned  # noqa: F401
from test_local_index import ROOT, T0, db, make_run, repo, store  # noqa: F401
from test_markers_query import VERSION as MARKERS_VERSION, found as marker_found

from vyasa.application import profile_context as pc
from vyasa.application import query
from vyasa.domain.index import PROJECT_NOT_FOUND, IndexStoreError
from vyasa.domain.languages import LanguageOutcome
from vyasa.domain.markers import MarkerReport
from vyasa.domain.profile import ProfileResult

NOW = lambda: T0 + timedelta(hours=1)  # noqa: E731


# --- builders for the checkout dictionaries `get_project` returns ---

def langs(*labels, status="complete", declared=()):
    items = [{"label": l, "status": "files_detected", "files": 1} for l in labels]
    items += [{"label": l, "status": "declared", "files": None} for l in declared]
    return {"status": status, "stopped_by": None if status == "complete" else "entries", "observed_at": "t", "types_version": 2, "items": items}


def frames(*keys, status="complete"):
    return {"status": status, "registry_version": 1, "stopped_by": None, "observed_at": "t", "ecosystems": [],
            "technologies": [{"key": k, "name": k, "category": "x", "scopes": ["runtime"], "manifests": ["m"]} for k in keys]}


def marks(status="complete", **detected):
    """detected: marker -> list of paths; every other marker is not_detected (complete) or unknown (partial)."""
    from vyasa.domain.markers import MARKERS

    missing = "not_detected" if status == "complete" else "unknown"
    items = []
    for marker in MARKERS:
        if marker in detected:
            paths = [{"path": p} for p in detected[marker]]
            items.append({"marker": marker, "state": "detected", "total": len(paths), "rules": ["r"], "paths": paths, "more": 0})
        else:
            items.append({"marker": marker, "state": missing})
    return {"status": status, "rules_version": 1, "stopped_by": None, "observed_at": "t", "items": items}


def checkout(languages=None, frameworks=None, markers=None):
    return {"languages": languages or langs(), "frameworks": frameworks or frames(), "markers": markers or marks()}


def codes(findings):
    return sorted((f["code"], f["subject"]) for f in findings)


# --- differences ---

def test_declared_language_not_detected_after_a_complete_assessment():
    found = pc.differences(checkout(langs("Python")), {"project.technology.declared_languages": ["Rust", "Python"]})
    assert codes(found) == [("declared_language_not_detected", "Rust")]


def test_declared_language_found_through_a_manifest_counts_as_detected():
    found = pc.differences(checkout(langs(declared=["Rust"])), {"project.technology.declared_languages": ["rust"]})
    assert found == []


def test_partial_observation_makes_no_absence_claim():
    partial = checkout(langs("Python", status="partial"), frames(status="partial"), marks("partial"))
    fields = {"project.technology.declared_languages": ["Rust"], "project.technology.declared_frameworks": ["FastAPI"],
              "project.engineering.openspec.enabled": True,
              "project.engineering.agent_instructions": [{"path": "AGENTS.md"}]}
    assert pc.differences(partial, fields) == []


def test_not_assessed_observations_make_no_claim():
    nothing = checkout({"status": "not_observed", "items": []}, {"status": "not_assessed", "technologies": [], "ecosystems": []},
                       {"status": "not_assessed", "items": []})
    fields = {"project.technology.declared_languages": ["Rust"], "project.engineering.openspec.enabled": True}
    assert pc.differences(nothing, fields) == []


def test_detected_language_not_declared_only_when_languages_are_declared():
    only_python = {"project.technology.declared_languages": ["Python"]}
    found = pc.differences(checkout(langs("Python", "Go")), only_python)
    assert codes(found) == [("detected_language_not_declared", "Go")] and found[0]["severity"] == "info"
    assert pc.differences(checkout(langs("Python", "Go")), {}) == []
    assert pc.differences(checkout(langs("Python", "Go")), {"project.name": "x"}) == []


def test_declared_only_language_by_manifest_is_not_reported_as_undeclared():
    found = pc.differences(checkout(langs(declared=["Rust"])), {"project.technology.declared_languages": ["Python"]})
    assert codes(found) == [("declared_language_not_detected", "Python")]  # Rust came from a manifest, not from files


def test_declared_framework_not_detected_matches_by_key_or_name():
    declared = {"project.technology.declared_frameworks": ["FastAPI", "react"]}
    found = pc.differences(checkout(frameworks=frames("react")), declared)
    assert codes(found) == [("declared_framework_not_detected", "FastAPI")]
    assert pc.differences(checkout(frameworks=frames("fastapi", "react")), declared) == []


def test_detected_technology_not_declared_skips_ubiquitous_ones():
    declared = {"project.technology.declared_frameworks": ["FastAPI"]}
    found = pc.differences(checkout(frameworks=frames("fastapi", "django", "pytest")), declared)
    assert codes(found) == [("detected_technology_not_declared", "django")]  # pytest is ubiquitous


def test_nothing_declared_in_the_category_reports_nothing_undeclared():
    assert pc.differences(checkout(frameworks=frames("django")), {"project.name": "x"}) == []


def test_unmatched_declared_names_are_not_comparable():
    declared = {"project.technology.declared_frameworks": ["PostgreSQL", "FastAPI"]}
    found = pc.differences(checkout(frameworks=frames("fastapi")), declared)
    assert codes(found) == [("declared_not_comparable", "PostgreSQL")] and found[0]["severity"] == "info"


def test_version_one_technologies_are_resolved_one_by_one():
    declared = {"technologies": ["Python", "FastAPI", "PostgreSQL"]}
    found = pc.differences(checkout(langs("Python"), frames("django")), declared)
    assert codes(found) == [
        ("declared_framework_not_detected", "FastAPI"), ("declared_not_comparable", "PostgreSQL"),
        ("detected_technology_not_declared", "django")]


def test_declared_openspec_not_detected_and_the_reverse():
    enabled = {"project.engineering.openspec.enabled": True}
    disabled = {"project.engineering.openspec.enabled": False}
    unknown = {"project.engineering.openspec.enabled": "unknown"}
    assert codes(pc.differences(checkout(markers=marks()), enabled)) == [("declared_openspec_not_detected", "openspec")]
    assert pc.differences(checkout(markers=marks(openspec_directory=["openspec"])), enabled) == []
    assert codes(pc.differences(checkout(markers=marks(openspec_directory=["openspec"])), disabled)) == [("openspec_detected_but_declared_disabled", "openspec")]
    assert pc.differences(checkout(markers=marks()), disabled) == [] and pc.differences(checkout(markers=marks()), unknown) == []


def test_declared_openspec_disabled_but_found_is_reported_even_when_partial():
    partial = marks("partial", openspec_directory=["openspec"])
    assert codes(pc.differences(checkout(markers=partial), {"project.engineering.openspec.enabled": False})) == [("openspec_detected_but_declared_disabled", "openspec")]


def test_declared_agent_instruction_files_are_compared_with_the_detected_paths():
    declared = {"project.engineering.agent_instructions": [{"path": "AGENTS.md"}, {"path": "docs\\CLAUDE.md"}, {"path": "GEMINI.md"}]}
    detected = marks(agent_instructions=["agents.md", "docs/CLAUDE.md"])
    assert codes(pc.differences(checkout(markers=detected), declared)) == [("declared_agent_instruction_not_detected", "GEMINI.md")]
    assert codes(pc.differences(checkout(markers=marks()), {"project.engineering.agent_instructions": [{"path": "AGENTS.md"}]})) == [
        ("declared_agent_instruction_not_detected", "AGENTS.md")]


def test_no_claim_when_more_paths_matched_than_were_stored():
    markers = marks(agent_instructions=["a/AGENTS.md"])
    for item in markers["items"]:
        if item["marker"] == "agent_instructions":
            item["more"] = 5
    assert pc.differences(checkout(markers=markers), {"project.engineering.agent_instructions": [{"path": "AGENTS.md"}]}) == []


def test_findings_are_labelled_sorted_and_stable():
    fields = {"project.technology.declared_languages": ["Rust", "Zig-less", "Go"], "project.engineering.openspec.enabled": True}
    one = pc.differences(checkout(langs("Python")), fields)
    two = pc.differences(checkout(langs("Python")), dict(reversed(list(fields.items()))))
    assert one == two == sorted(one, key=lambda f: (f["code"], f["subject"]))
    for finding in one:
        assert set(finding) == {"code", "severity", "subject", "detail"} and finding["severity"] in {"review", "info"}
        assert finding["detail"] == pc.DETAILS[finding["code"]]


def test_details_are_fixed_text_without_declared_content():
    for text in pc.DETAILS.values():
        assert "{" not in text and text.endswith(".")


def test_no_profile_means_no_findings():
    assert pc.differences(checkout(langs("Python"), frames("django"), marks()), {}) == []


# --- the stored bundle ---

def full(name, fields=None, languages=("Python",), manifests=(), markers=(), stopped_by=None, status="valid"):
    scan = scanned(report(tuple((l, 1) for l in languages), stopped_by=stopped_by))
    outcome = LanguageOutcome(scan.languages, composition=scan.composition,
                              markers=MarkerReport(tuple(markers), MARKERS_VERSION, stopped_by),
                              frameworks=fw(*manifests, stopped_by=stopped_by))
    profile = ProfileResult(status, fields or {}) if fields is not None else None
    return replace(repo(name), languages=outcome, profile=profile)


@pytest.fixture
def reader(db):
    store(db, make_run([
        full("api", {"project.summary": "Billing.", "project.technology.declared_languages": ["Python", "Rust"],
                     "project.technology.declared_frameworks": ["FastAPI"], "project.engineering.openspec.enabled": True},
             manifests=[mf("pyproject.toml", "python", ("django", None, "runtime"))]),
        full("noprofile"),
        replace(repo("old"), languages=LanguageOutcome(report())), repo("plain"),
    ]))
    return db


def context(db, name):
    pid = next(p["project_id"] for p in query.search_projects(db, now=NOW)["data"]["projects"] if p["display_name"] == name)
    return pc.profile_context(db, pid, now=NOW)


def test_the_bundle_has_facts_profile_differences_and_workflow(reader):
    bundle = context(reader, "api")
    data = bundle["data"]
    assert data["source"] == {"kind": "index", "generated_at": NOW().isoformat()}
    assert data["project_id"] and data["display_name"] == "api" and data["identity"]["status"]
    (checkout,) = data["checkouts"]
    assert {"languages", "composition", "markers", "frameworks", "differences"} <= set(checkout)
    assert data["profile"]["status"] == "valid" and data["profile"]["declared"]["project.summary"]["value"] == "Billing."
    assert data["workflow"] == list(pc.WORKFLOW)
    assert codes(checkout["differences"]) == [
        ("declared_framework_not_detected", "FastAPI"), ("declared_language_not_detected", "Rust"),
        ("declared_openspec_not_detected", "openspec"), ("detected_technology_not_declared", "django")]
    assert bundle["schema_version"] == "1" and "freshness" in bundle["meta"]


def test_the_bundle_equals_project_details_plus_the_extras(reader):
    pid = context(reader, "api")["data"]["project_id"]
    details = query.get_project(reader, pid, now=NOW)["data"]
    data = context(reader, "api")["data"]
    for key in ("project_id", "display_name", "state", "identity", "profile", "review_candidates", "created_at"):
        assert data[key] == details[key]
    stripped = [{k: v for k, v in c.items() if k != "differences"} for c in data["checkouts"]]
    assert stripped == details["checkouts"]


def test_no_profile_is_an_ordinary_state(reader):
    data = context(reader, "noprofile")["data"]
    assert data["profile"]["status"] == "absent" and data["checkouts"][0]["differences"] == []
    assert data["workflow"] == list(pc.WORKFLOW)
    assert any(".vyasa/project-profile.toml" in step for step in data["workflow"])


def test_never_assessed_observations_claim_nothing(reader):
    data = context(reader, "old")["data"]
    assert data["checkouts"][0]["differences"] == [] and data["checkouts"][0]["markers"]["status"] == "not_assessed"
    assert context(reader, "plain")["data"]["checkouts"][0]["differences"] == []


def test_unknown_and_invalid_project_ids(reader):
    for value, code in (("nope", PROJECT_NOT_FOUND), ("", "INVALID_INPUT"), (3, "INVALID_INPUT")):
        with pytest.raises(IndexStoreError) as error:
            pc.profile_context(reader, value, now=NOW)
        assert error.value.code == code


def test_the_bundle_has_no_absolute_path_and_no_file_text(reader):
    text = json.dumps(context(reader, "api"))
    assert str(ROOT) not in text and "/ws" not in text and ":\\" not in text


def test_malformed_manifest_shows_only_status_and_reason(db):
    bad = mf("package.json", "javascript", status="malformed", reason="syntax")
    store(db, make_run([full("m", manifests=[bad])]))
    text = json.dumps(context(db, "m")["data"]["checkouts"][0]["frameworks"])
    assert '"reason": "syntax"' in text and "{not json" not in text


def test_the_workflow_is_fixed_text():
    assert all(isinstance(step, str) and step for step in pc.WORKFLOW)
    joined = " ".join(pc.WORKFLOW).lower()
    for needle in ("get_profile_guide", "evidence", "omit", "secrets", "maintainer", "observed counts"):
        assert needle in joined
    assert pc.WORKFLOW == tuple(pc.WORKFLOW)


def test_the_bundle_is_read_only(reader):
    before = [tuple(r) for r in reader.execute("SELECT * FROM checkout_profiles")]
    context(reader, "api")
    assert [tuple(r) for r in reader.execute("SELECT * FROM checkout_profiles")] == before
    assert REGISTRY.version >= 1
