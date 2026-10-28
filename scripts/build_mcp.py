"""Build the vyasa-mcp executable and save it outside the repository (Windows and Linux).

Output: <out>/<name>/vyasa-mcp[.exe] (PyInstaller one-folder build). Build and work files go to a
temp directory, never into the repo. PyInstaller builds for the OS it runs on only.

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
ENTRY = "from vyasa.adapters.mcp.launch import main\n\nif __name__ == '__main__':\n    main()\n"


def load_env(path: Path) -> None:
    """Read KEY=VALUE lines from .env into os.environ; real environment variables win."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        key, sep, value = line.partition("=")
        key = key.strip()
        if sep and key and not key.startswith("#"):
            os.environ.setdefault(key, value.strip().strip("\"'"))


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

    target = Path(args.out).expanduser() / args.name
    exe = "vyasa-mcp.exe" if sys.platform == "win32" else "vyasa-mcp"
    with tempfile.TemporaryDirectory(prefix="vyasa-build-") as work:
        work_dir = Path(work)
        entry = work_dir / "vyasa_mcp_entry.py"
        entry.write_text(ENTRY, encoding="utf-8")
        subprocess.run(
            [
                sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onedir",
                "--name", "vyasa-mcp",
                "--paths", str(ROOT / "src"),
                "--collect-data", "vyasa",
                "--copy-metadata", "mcp",
                "--distpath", str(work_dir / "dist"),
                "--workpath", str(work_dir / "build"),
                "--specpath", work,
                str(entry),
            ],
            check=True,
        )
        if target.exists():
            shutil.rmtree(target)  # only <out>/<name>, the folder this script owns
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(work_dir / "dist" / "vyasa-mcp"), str(target))

    print(f"Saved: {target / exe}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
