"""Build the vyasa and vyasa-mcp executables and their data folder outside the repository (Windows and Linux).

Output: <out>/<name>/vyasa/vyasa[.exe], <out>/<name>/vyasa-mcp/vyasa-mcp[.exe], and <out>/<name>/data/
(config.toml seeded once, then the index). Built executables use that data folder with no environment
setup (VYASA_HOME still overrides). A rebuild replaces the two executable folders and never touches
data/. Build and work files go to a temp directory, never into the repo. PyInstaller builds for the OS
it runs on only.

Output root, first match wins: --out, env VYASA_MCP_OUT, then VYASA_MCP_OUT in <repo>/.env (see
.env.example). No default: one of them is required.

    VYASA_MCP_OUT=/opt/mcp python scripts/build_mcp.py              (Linux)
    $env:VYASA_MCP_OUT = "E:\\MCP"; python scripts/build_mcp.py     (Windows)
    python scripts/build_mcp.py --out D:\\Servers --name "Vyasa MCP"
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = {
    "vyasa": "from vyasa.adapters.cli.main import run\n\nif __name__ == '__main__':\n    run()\n",
    "vyasa-mcp": "from vyasa.adapters.mcp.launch import main\n\nif __name__ == '__main__':\n    main()\n",
}


def load_env(path: Path) -> None:
    """Read KEY=VALUE lines from .env into os.environ; real environment variables win."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        key, sep, value = line.partition("=")
        key = key.strip()
        if sep and key and not key.startswith("#"):
            os.environ.setdefault(key, value.strip().strip("\"'"))


def build_one(name: str, entry_text: str, work_dir: Path) -> Path:
    """Build one PyInstaller one-folder bundle in work_dir and return its folder."""
    entry = work_dir / f"{name}_entry.py"
    entry.write_text(entry_text, encoding="utf-8")
    subprocess.run(
        [
            sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onedir",
            "--name", name,
            "--paths", str(ROOT / "src"),
            "--collect-data", "vyasa",
            "--copy-metadata", "mcp",
            "--distpath", str(work_dir / "dist"),
            "--workpath", str(work_dir / "build" / name),
            "--specpath", str(work_dir),
            str(entry),
        ],
        check=True,
    )
    return work_dir / "dist" / name


def install(root: Path, bundles: dict[str, Path], example_config: Path) -> None:
    """Replace only the bundle folders under root; create data/ and seed its config once."""
    root.mkdir(parents=True, exist_ok=True)
    for name, folder in bundles.items():
        target = root / name
        if target.exists():
            shutil.rmtree(target)  # only <root>/<bundle>, a folder this script owns
        shutil.move(str(folder), str(target))
    data = root / "data"
    data.mkdir(exist_ok=True)
    config = data / "config.toml"
    if not config.exists():
        shutil.copyfile(example_config, config)


def main() -> int:
    load_env(ROOT / ".env")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", default=os.environ.get("VYASA_MCP_OUT"), help="output root (env VYASA_MCP_OUT)")
    parser.add_argument("--name", default=os.environ.get("VYASA_MCP_NAME", "Vyasa MCP"), help="folder under the output root (env VYASA_MCP_NAME)")
    args = parser.parse_args()

    if not args.out:
        print("Output root not set. Set VYASA_MCP_OUT or pass --out.", file=sys.stderr)
        return 2
    if subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], capture_output=True).returncode:
        print("PyInstaller missing. Install it with: pip install -e '.[mcp,build]'", file=sys.stderr)
        return 2

    root = Path(args.out).expanduser() / args.name
    suffix = ".exe" if sys.platform == "win32" else ""
    with tempfile.TemporaryDirectory(prefix="vyasa-build-") as work:
        bundles = {name: build_one(name, text, Path(work)) for name, text in ENTRIES.items()}
        install(root, bundles, ROOT / "examples" / "config.toml")  # both built before anything is replaced

    print(f"Saved: {root / 'vyasa' / ('vyasa' + suffix)}")
    print(f"Saved: {root / 'vyasa-mcp' / ('vyasa-mcp' + suffix)}")
    print(f"Data:  {root / 'data'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
