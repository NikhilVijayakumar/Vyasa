import json
from dataclasses import replace

import pytest
from test_frameworks_query import NOW, framed, fw, mf
from test_local_index import ROOT, db, make_run, store  # noqa: F401

from vyasa.application import query
from vyasa.domain.index import INVALID_INPUT, PROJECT_NOT_FOUND, IndexStoreError


def named(manifest, name):
    return replace(manifest, declared_name=name)


def py(*deps, name=None, **kw):
    return named(mf("pyproject.toml", "python", *deps, **kw), name)


def js(*deps, name=None, **kw):
    return named(mf("package.json", "javascript", *deps, **kw), name)




def build(db, repos, **kw):
    store(db, make_run(repos, **kw))
    return lambda name: db.execute("SELECT project_id FROM projects WHERE display_name = ?", (name,)).fetchone()[0]


def ask(db, pid):
    return query.get_project_dependencies(db, pid, now=NOW)["data"]


def entry(data, name, scope=None):
    (found,) = [d for d in data["dependencies"] if d["name"] == name and (scope is None or d["scope"] == scope)]
    return found


# --- slice 3: dependencies with evidence ---

def test_dependencies_carry_scope_constraint_and_source(db):
    ident = build(db, [framed("a", fw(py(("fastapi", ">=0.1", "runtime"), ("pytest", None, "dev"))))])
    data = ask(db, ident("a"))
    assert [(d["name"], d["ecosystem"], d["constraint"], d["scope"], d["source"]) for d in data["dependencies"]] == [
        ("fastapi", "python", ">=0.1", "runtime", "pyproject.toml"), ("pytest", "python", None, "dev", "pyproject.toml")]
    assert data["project_id"] == ident("a") and data["display_name"] == "a"


def test_same_name_in_two_scopes_is_two_entries_in_a_stable_order(db):
    ident = build(db, [framed("a", fw(js(("zed", "1", "runtime"), ("lib", "1", "dev"), ("lib", "2", "runtime")), py(("req", None, "runtime"))))])
    data = ask(db, ident("a"))
    assert [(d["ecosystem"], d["name"], d["scope"]) for d in data["dependencies"]] == [
        ("javascript", "lib", "dev"), ("javascript", "lib", "runtime"), ("javascript", "zed", "runtime"), ("python", "req", "runtime")]


def test_unknown_and_invalid_identifiers(db):
    build(db, [framed("a", fw(py()))])
    with pytest.raises(IndexStoreError) as unknown:
        query.get_project_dependencies(db, "nope")
    assert unknown.value.code == PROJECT_NOT_FOUND
    for bad in ("", None, 5):
        with pytest.raises(IndexStoreError) as error:
            query.get_project_dependencies(db, bad)  # type: ignore[arg-type]
        assert error.value.code == INVALID_INPUT


def test_no_local_path_in_the_answer(db):
    ident = build(db, [framed("a", fw(py(("x", None, "runtime"), name="a-pkg"))), framed("b", fw(py(("a-pkg", None, "runtime"))))])
    for name in ("a", "b"):
        text = json.dumps(ask(db, ident(name)))
        assert str(ROOT) not in text and "/ws" not in text


def test_only_the_latest_observation_of_active_checkouts_counts(db):
    build(db, [framed("a", fw(py(("old", None, "runtime"))))])
    ident = build(db, [framed("a", fw(py(("new", None, "runtime"))))])
    assert [d["name"] for d in ask(db, ident("a"))["dependencies"]] == ["new"]


# --- slice 4: internal, ambiguous, external ---

def test_internal_dependency_names_the_project(db):
    ident = build(db, [framed("a", fw(py(("ledger-core", ">=1", "runtime")))), framed("b", fw(py(name="ledger-core")))])
    found = entry(ask(db, ident("a")), "ledger-core")
    assert found["resolution"] == "internal"
    assert found["projects"] == [{"project_id": ident("b"), "display_name": "b"}]


def test_same_name_in_another_ecosystem_is_external(db):
    ident = build(db, [framed("a", fw(py(("ui", None, "runtime")))), framed("b", fw(js(name="ui")))])
    found = entry(ask(db, ident("a")), "ui")
    assert found["resolution"] == "external" and found["projects"] == []


def test_ambiguous_lists_every_candidate(db):
    ident = build(db, [framed("a", fw(py(("ledger-core", None, "runtime")))), framed("b", fw(py(name="ledger-core"))),
                       framed("c", fw(py(name="ledger-core")))])
    found = entry(ask(db, ident("a")), "ledger-core")
    assert found["resolution"] == "ambiguous"
    assert [p["display_name"] for p in found["projects"]] == ["b", "c"]


def test_not_indexed_is_external_and_invents_no_project(db):
    ident = build(db, [framed("a", fw(py(("requests", None, "runtime"))))])
    found = entry(ask(db, ident("a")), "requests")
    assert found["resolution"] == "external" and found["projects"] == []


def test_a_project_never_depends_on_itself(db):
    ident = build(db, [framed("a", fw(py(("self-pkg", None, "runtime"), name="self-pkg")))])
    assert entry(ask(db, ident("a")), "self-pkg")["resolution"] == "external"


def test_names_match_case_insensitively_outside_python_too(db):
    ident = build(db, [framed("a", fw(js(("Shared-Lib", "1", "runtime")))), framed("b", fw(js(name="shared-lib")))])
    assert entry(ask(db, ident("a")), "Shared-Lib")["resolution"] == "internal"


def test_a_missing_checkout_is_not_a_target(db):
    build(db, [framed("a", fw(py(("lib", None, "runtime")))), framed("b", fw(py(name="lib")))])
    ident = build(db, [framed("a", fw(py(("lib", None, "runtime"))))])
    assert entry(ask(db, ident("a")), "lib")["resolution"] == "external"


# --- slice 5: dependents ---

def test_dependents_name_the_edge(db):
    ident = build(db, [framed("a", fw(py(("lib", ">=2", "dev")))), framed("b", fw(py(name="lib")))])
    (dep,) = ask(db, ident("b"))["dependents"]
    assert dep == {"project_id": ident("a"), "display_name": "a", "ecosystem": "python", "name": "lib", "constraint": ">=2",
                   "scope": "dev", "source": "pyproject.toml", "resolution": "internal"}


def test_ambiguous_dependent_is_marked(db):
    ident = build(db, [framed("a", fw(py(("lib", None, "runtime")))), framed("b", fw(py(name="lib"))), framed("c", fw(py(name="lib")))])
    for owner in ("b", "c"):
        (dep,) = ask(db, ident(owner))["dependents"]
        assert dep["display_name"] == "a" and dep["resolution"] == "ambiguous"


def test_no_dependents(db):
    ident = build(db, [framed("a", fw(py(name="lib")))])
    data = ask(db, ident("a"))
    assert data["dependents"] == [] and data["dependents_total"] == 0 and data["dependents_truncated"] is False


def test_dependents_are_capped_with_a_total(db):
    repos = [framed("lib", fw(py(name="lib")))] + [framed(f"u{n:03}", fw(py(("lib", None, "runtime")))) for n in range(101)]
    ident = build(db, repos)
    data = ask(db, ident("lib"))
    assert len(data["dependents"]) == 100 and data["dependents_total"] == 101 and data["dependents_truncated"] is True
    assert [d["display_name"] for d in data["dependents"]] == sorted(d["display_name"] for d in data["dependents"])


# --- slice 6: coverage ---

def test_complete_observation(db):
    ident = build(db, [framed("a", fw(py(("x", None, "runtime"), name="a")))])
    coverage = ask(db, ident("a"))["coverage"]
    assert coverage["status"] == "complete" and coverage["nested_not_parsed"] == 0
    assert coverage["manifests"] == [{"path": "pyproject.toml", "ecosystem": "python", "status": "parsed", "reason": None,
                                      "declared_name_recorded": True}]
    assert coverage["declared_names_recorded"] is True and coverage["other_projects_unchecked"] == 0


def test_unparsed_manifest_is_listed_and_the_rest_kept(db):
    bad = mf("package.json", "javascript", status="malformed", reason="syntax")
    ident = build(db, [framed("a", fw(bad, py(("x", None, "runtime"))))])
    data = ask(db, ident("a"))
    assert [d["name"] for d in data["dependencies"]] == ["x"]
    assert {m["path"]: (m["status"], m["reason"]) for m in data["coverage"]["manifests"]} == {
        "package.json": ("malformed", "syntax"), "pyproject.toml": ("parsed", None)}


def test_partial_walk_is_partial(db):
    ident = build(db, [framed("a", fw(py(), stopped_by="entries"), stopped_by="entries")])
    assert ask(db, ident("a"))["coverage"]["status"] == "partial"


def test_not_assessed_has_empty_lists(db):
    ident = build(db, [framed("a")])
    data = ask(db, ident("a"))
    assert data["coverage"]["status"] == "not_assessed"
    assert data["dependencies"] == [] and data["dependents"] == [] and data["coverage"]["manifests"] == []


def test_nested_manifests_are_counted(db):
    ident = build(db, [framed("a", fw(py(), nested=[("javascript", 2), ("python", 1)]))])
    assert ask(db, ident("a"))["coverage"]["nested_not_parsed"] == 3


def test_observations_without_recorded_names_say_so_and_count_as_unchecked(db):
    ident = build(db, [framed("a", fw(py(("lib", None, "runtime")))), framed("b", fw(py(name="lib")))])
    db.execute("UPDATE language_observations SET names_recorded = NULL WHERE checkout_id IN"
               " (SELECT checkout_id FROM checkouts WHERE path LIKE '%b')")
    db.execute("UPDATE checkout_manifests SET declared_name = NULL WHERE observation_id IN"
               " (SELECT observation_id FROM language_observations WHERE names_recorded IS NULL)")  # as before the migration
    coverage = ask(db, ident("a"))["coverage"]
    assert coverage["other_projects_unchecked"] == 1 and coverage["declared_names_recorded"] is True
    assert entry(ask(db, ident("a")), "lib")["resolution"] == "external"
    db.execute("UPDATE language_observations SET names_recorded = NULL")
    own = ask(db, ident("a"))["coverage"]
    assert own["declared_names_recorded"] is False and own["manifests"][0]["declared_name_recorded"] is False


def test_other_partial_or_unassessed_projects_are_unchecked(db):
    ident = build(db, [framed("a", fw(py())), framed("b", fw(py(), stopped_by="entries"), stopped_by="entries"), framed("c")])
    assert ask(db, ident("a"))["coverage"]["other_projects_unchecked"] == 2
