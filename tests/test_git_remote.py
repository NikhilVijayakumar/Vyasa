import os

import pytest

from vyasa.adapters.filesystem.git_config import MAX_CONFIG_BYTES, read_remote
from vyasa.domain.git_remote import (
    BITBUCKET,
    GITHUB,
    GITLAB,
    LOCAL,
    NONE,
    OTHER,
    STATUS_AMBIGUOUS,
    STATUS_NONE,
    STATUS_ONLY,
    STATUS_ORIGIN,
    STATUS_UNAVAILABLE,
    choose_remote,
    normalize_remote,
    parse_remotes,
)

# -- parsing ------------------------------------------------------------------------------------


CONFIG = """\
[core]
\trepositoryformatversion = 0
\tbare = false
[remote "origin"]
\turl = https://github.com/Org/Repo.git
\tfetch = +refs/heads/*:refs/remotes/origin/*
[remote "upstream"]
# a comment
\turl = git@gitlab.com:team/repo.git
\tfetch = +refs/heads/*:refs/remotes/upstream/*
[branch "main"]
\tremote = origin
\turl = not-a-remote
"""


def test_remotes_are_returned_in_file_order_with_their_first_url():
    assert parse_remotes(CONFIG) == {
        "origin": "https://github.com/Org/Repo.git",
        "upstream": "git@gitlab.com:team/repo.git",
    }


def test_other_sections_comments_and_keys_are_ignored():
    text = '[core]\nurl = ignored\n; note\n[remote "a"]\npushurl = https://x/y\nfetch = z\n'
    assert parse_remotes(text) == {}


def test_quotes_and_trailing_comments_are_removed_from_the_value():
    text = '[remote "a"]\nurl = "https://github.com/o/r.git"\n[remote "b"]\nurl = https://github.com/o/s.git # note\n'
    assert parse_remotes(text) == {"a": "https://github.com/o/r.git", "b": "https://github.com/o/s.git"}


def test_only_the_first_url_of_a_remote_counts():
    text = '[remote "a"]\nurl = https://one/x\nurl = https://two/y\n'
    assert parse_remotes(text) == {"a": "https://one/x"}


def test_keys_are_case_insensitive_and_section_spacing_is_tolerated():
    assert parse_remotes('[ remote  "a" ]\nURL=https://h/o/r\n') == {"a": "https://h/o/r"}


def test_empty_and_garbage_text_give_no_remotes():
    assert parse_remotes("") == {}
    assert parse_remotes("\x00\x01 not a config [[[") == {}


# -- normalizing and labelling ---------------------------------------------------------------------


@pytest.mark.parametrize(
    "url",
    [
        "https://github.com/Org/Repo.git",
        "https://github.com/Org/Repo",
        "https://github.com/Org/Repo/",
        "git@github.com:Org/Repo.git",
        "github.com:Org/Repo",
        "ssh://git@github.com:22/Org/Repo.git",
        "https://user:token@github.com/Org/Repo/",
        "https://GitHub.COM/Org/Repo.GIT",
        "https://github.com:443/Org/Repo.git?x=1#frag",
        "ssh://git@ssh.github.com:443/Org/Repo.git",
    ],
)
def test_equivalent_forms_give_one_identity(url):
    assert normalize_remote(url) == (GITHUB, "github.com", "github.com/org/repo")


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://bitbucket.org/Team/Repo.git", (BITBUCKET, "bitbucket.org", "bitbucket.org/team/repo")),
        ("git@bitbucket.org:Team/Repo.git", (BITBUCKET, "bitbucket.org", "bitbucket.org/team/repo")),
        ("https://gitlab.com/Group/Sub/Repo.git", (GITLAB, "gitlab.com", "gitlab.com/Group/Sub/Repo")),
        ("git@gitlab.com:Group/Repo.git", (GITLAB, "gitlab.com", "gitlab.com/Group/Repo")),
        ("https://git.example.com/Team/Repo.git", (OTHER, "git.example.com", "git.example.com/Team/Repo")),
        ("git@git.example.com:Team/Repo.git", (OTHER, "git.example.com", "git.example.com/Team/Repo")),
        ("https://git.example.com:8443/Team/Repo.git", (OTHER, "git.example.com", "git.example.com:8443/Team/Repo")),
        ("https://git.example.com:443/Team/Repo", (OTHER, "git.example.com", "git.example.com/Team/Repo")),
        ("ssh://git@git.example.com:2222/Team/Repo", (OTHER, "git.example.com", "git.example.com:2222/Team/Repo")),
        ("git://git.example.com:9418/team/repo.git", (OTHER, "git.example.com", "git.example.com/team/repo")),
        ("https://dev.azure.com/org/project/_git/repo", (OTHER, "dev.azure.com", "dev.azure.com/org/project/_git/repo")),
        ("https://github.com", (GITHUB, "github.com", None)),
    ],
)
def test_providers_hosts_and_case(url, expected):
    assert normalize_remote(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "/srv/repos/x.git",
        "../x",
        "./x",
        "x",
        "C:\\repos\\x",
        "C:/repos/x",
        "c:/repos/x",
        "file:///srv/x.git",
        "FILE:///srv/x.git",
    ],
)
def test_paths_and_file_urls_are_local_without_identity(url):
    assert normalize_remote(url) == (LOCAL, None, None)


def test_an_empty_url_is_none():
    assert normalize_remote("") == (NONE, None, None)
    assert normalize_remote("   ") == (NONE, None, None)


@pytest.mark.parametrize(
    "url",
    [
        "https://alice:s3cret@bitbucket.org/team/repo.git",
        "https://alice:s3cret@git.example.com:8443/team/repo.git",
        "ssh://alice:s3cret@git.example.com/team/repo.git",
        "alice@git.example.com:team/repo.git",
        "https://ghp_TOKEN123@github.com/org/repo.git",
    ],
)
def test_credentials_never_appear_in_any_returned_value(url):
    provider, host, identity = normalize_remote(url)
    kept = f"{provider} {host} {identity}"
    for secret in ("alice", "s3cret", "ghp_TOKEN123"):
        assert secret not in kept


# -- choosing ---------------------------------------------------------------------------------------


def test_origin_is_preferred_whatever_the_order():
    remote, status = choose_remote({"upstream": "https://gitlab.com/a/b", "origin": "https://github.com/c/d"})
    assert status == STATUS_ORIGIN and remote.name == "origin" and remote.provider == GITHUB
    assert remote.identity == "github.com/c/d"


def test_the_only_remote_is_used_even_if_not_named_origin():
    remote, status = choose_remote({"backup": "https://bitbucket.org/a/b"})
    assert status == STATUS_ONLY and remote.name == "backup" and remote.provider == BITBUCKET


def test_several_remotes_without_origin_are_ambiguous():
    assert choose_remote({"a": "https://github.com/a/b", "b": "https://github.com/c/d"}) == (None, STATUS_AMBIGUOUS)


def test_no_remote_and_an_empty_url_are_none():
    assert choose_remote({}) == (None, STATUS_NONE)
    assert choose_remote({"origin": ""}) == (None, STATUS_NONE)


def test_the_chosen_remote_keeps_no_url():
    remote, _ = choose_remote({"origin": "https://alice:s3cret@github.com/org/repo.git"})
    assert "s3cret" not in repr(remote) and "alice" not in repr(remote)
    assert not hasattr(remote, "url")


def test_a_local_remote_has_no_identity():
    remote, status = choose_remote({"origin": "/srv/x.git"})
    assert (remote.provider, remote.identity, status) == (LOCAL, None, STATUS_ORIGIN)


# -- reading ----------------------------------------------------------------------------------------------


def project_with_config(tmp_path, text):
    git = tmp_path / ".git"
    git.mkdir()
    (git / "config").write_bytes(text.encode("utf-8"))
    return os.fspath(tmp_path)


def test_the_config_of_a_git_directory_is_read(tmp_path):
    remote, status = read_remote(project_with_config(tmp_path, CONFIG))
    assert status == STATUS_ORIGIN and remote.provider == GITHUB


def test_a_config_with_a_byte_order_mark_and_windows_line_endings_is_read(tmp_path):
    text = "\ufeff" + CONFIG.replace("\n", "\r\n")
    remote, status = read_remote(project_with_config(tmp_path, text))
    assert status == STATUS_ORIGIN and remote.identity == "github.com/org/repo"


def test_a_repository_without_a_config_or_remote_has_none(tmp_path):
    (tmp_path / ".git").mkdir()
    assert read_remote(os.fspath(tmp_path)) == (None, STATUS_NONE)
    other = tmp_path / "other"
    other.mkdir()
    assert read_remote(project_with_config(other, "[core]\n\tbare = false\n")) == (None, STATUS_NONE)


def test_a_pointer_file_is_unavailable(tmp_path):
    (tmp_path / ".git").write_text("gitdir: ../.git/modules/x\n", encoding="utf-8")
    assert read_remote(os.fspath(tmp_path)) == (None, STATUS_UNAVAILABLE)


def test_no_git_entry_is_unavailable(tmp_path):
    assert read_remote(os.fspath(tmp_path)) == (None, STATUS_UNAVAILABLE)


def test_an_oversized_config_is_unavailable_and_one_at_the_limit_is_read(tmp_path):
    big = '[remote "origin"]\nurl = https://github.com/o/r\n' + "# pad\n" * (MAX_CONFIG_BYTES // 6 + 10)
    assert read_remote(project_with_config(tmp_path, big)) == (None, STATUS_UNAVAILABLE)
    head = '[remote "origin"]\nurl = https://github.com/o/r\n'
    exact = head + "#" * (MAX_CONFIG_BYTES - len(head))
    other = tmp_path / "exact"
    other.mkdir()
    remote, status = read_remote(project_with_config(other, exact))
    assert status == STATUS_ORIGIN and remote.provider == GITHUB


def test_a_linked_config_is_unavailable(tmp_path):
    target = tmp_path / "elsewhere.txt"
    target.write_text('[remote "origin"]\nurl = https://github.com/o/r\n', encoding="utf-8")
    project = tmp_path / "proj"
    (project / ".git").mkdir(parents=True)
    try:
        os.symlink(target, project / ".git" / "config")
    except (OSError, NotImplementedError) as error:
        pytest.skip(f"this platform or account cannot create file symlinks: {error}")
    assert read_remote(os.fspath(project)) == (None, STATUS_UNAVAILABLE)


def test_at_most_the_limit_plus_one_byte_is_read(tmp_path, monkeypatch):
    import builtins

    directory = project_with_config(tmp_path, "#" * (MAX_CONFIG_BYTES * 2))
    sizes = []
    real = builtins.open

    class Watching:
        def __init__(self, handle):
            self.handle = handle

        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            self.handle.close()

        def read(self, size=-1):
            sizes.append(size)
            return self.handle.read(size)

    def watching(file, *args, **kwargs):
        handle = real(file, *args, **kwargs)
        return Watching(handle) if os.path.basename(os.fspath(file)) == "config" else handle

    monkeypatch.setattr(builtins, "open", watching)
    read_remote(directory)
    assert sizes == [MAX_CONFIG_BYTES + 1]
