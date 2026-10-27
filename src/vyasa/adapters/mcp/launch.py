"""Start the server, or say how to install what it needs. Imports the SDK only when it runs."""

from __future__ import annotations

import sys

HINT = "vyasa-mcp needs the MCP SDK. Install it with: pip install 'vyasa[mcp]'"


def main() -> None:
    try:
        from vyasa.adapters.mcp.server import main as serve
    except ModuleNotFoundError as error:
        if (error.name or "").split(".")[0] == "mcp":
            print(HINT, file=sys.stderr)
            raise SystemExit(2) from None
        raise
    serve()
