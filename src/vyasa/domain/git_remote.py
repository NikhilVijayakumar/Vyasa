"""A project's Git remote: parse the config text, reduce a URL to a credential-free identity, label the provider.

Everything here is pure text work. The original URL is discarded as soon as it is parsed;
only the host, the identity, and the provider are kept.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

GITHUB = "github"
BITBUCKET = "bitbucket"
GITLAB = "gitlab"
OTHER = "other"
LOCAL = "local"
NONE = "none"

STATUS_ORIGIN = "origin"
STATUS_ONLY = "only"
STATUS_AMBIGUOUS = "ambiguous"
STATUS_NONE = "none"
STATUS_UNAVAILABLE = "unavailable"

# Add a well-known host here; every other host is "other" with the host kept.
PROVIDER_HOSTS: dict[str, str] = {
    "github.com": GITHUB,
    "bitbucket.org": BITBUCKET,
    "gitlab.com": GITLAB,
}
# The same server under another name; the port that goes with it (443 for ssh.github.com) is dropped too.
HOST_ALIASES: dict[str, str] = {"ssh.github.com": "github.com"}
CASE_INSENSITIVE_PROVIDERS = frozenset({GITHUB, BITBUCKET})
DEFAULT_PORTS = {"https": "443", "http": "80", "ssh": "22", "git": "9418"}

_REMOTE_SECTION = re.compile(r'^\[\s*remote\s+"([^"]+)"\s*\]')
_ANY_SECTION = re.compile(r"^\[")
_SCP = re.compile(r"^(?:[^@/\\\s]+@)?([^:/\\\s]+):(?!//)(.+)$")


@dataclass(frozen=True)
class GitRemote:
    """The chosen remote. No URL is kept, so no credential can be."""

    name: str
    provider: str
    host: str | None
    identity: str | None


def parse_remotes(text: str) -> dict[str, str]:
    """Remote name to its first ``url``, in file order. Everything else in the config is ignored."""
    remotes: dict[str, str] = {}
    current: str | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", ";")):
            continue
        section = _REMOTE_SECTION.match(line)
        if section:
            current = section.group(1)
            continue
        if _ANY_SECTION.match(line):
            current = None
            continue
        if current is None or "=" not in line:
            continue
        key, _, value = line.partition("=")
        if key.strip().casefold() != "url" or current in remotes:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] == '"':
            value = value[1:-1]
        else:
            for marker in (" #", " ;"):
                value = value.split(marker, 1)[0]
        remotes[current] = value.strip()
    return remotes


def _strip_path(path: str) -> str:
    path = path.split("?", 1)[0].split("#", 1)[0].strip("/")
    if path.casefold().endswith(".git"):
        path = path[:-4]
    return path.strip("/")


def normalize_remote(url: str) -> tuple[str, str | None, str | None]:
    """Return ``(provider, host, identity)`` for a remote URL or address."""
    url = url.strip()
    if not url:
        return NONE, None, None
    scheme = port = None
    if "://" in url:
        scheme, _, rest = url.partition("://")
        scheme = scheme.casefold()
        if scheme == "file":
            return LOCAL, None, None
        authority, _, path = rest.partition("/")
        authority = authority.rsplit("@", 1)[-1]
        host = authority
        if not authority.startswith("[") and ":" in authority:
            host, _, port = authority.rpartition(":")
    else:
        match = _SCP.match(url)
        if match is None or len(match.group(1)) == 1:  # a path, or a drive letter such as C:
            return LOCAL, None, None
        host, path = match.group(1), match.group(2)
    host = host.casefold()
    if not host:
        return LOCAL, None, None
    if host in HOST_ALIASES:
        host, port = HOST_ALIASES[host], None
    provider = PROVIDER_HOSTS.get(host, OTHER)
    path = _strip_path(path)
    if not path:
        return provider, host, None
    if port and port != DEFAULT_PORTS.get(scheme or ""):
        identity = f"{host}:{port}/{path}"
    else:
        identity = f"{host}/{path}"
    if provider in CASE_INSENSITIVE_PROVIDERS:
        identity = identity.casefold()
    return provider, host, identity


def choose_remote(remotes: dict[str, str]) -> tuple[GitRemote | None, str]:
    """Pick ``origin``, else the only remote, else none; return the remote and a status."""
    if "origin" in remotes:
        name, status = "origin", STATUS_ORIGIN
    elif len(remotes) == 1:
        name, status = next(iter(remotes)), STATUS_ONLY
    elif not remotes:
        return None, STATUS_NONE
    else:
        return None, STATUS_AMBIGUOUS
    provider, host, identity = normalize_remote(remotes[name])
    if provider == NONE:
        return None, STATUS_NONE
    return GitRemote(name=name, provider=provider, host=host, identity=identity), status
