r"""Standalone MCP — 3 domain servers: calc/calculator, site, catalog.

Run single:
  python -m et_mcp.server --server calc --transport stdio              # 6 tools
  python -m et_mcp.server --server site --transport stdio              # 2 tools BM25+grep
  python -m et_mcp.server --server catalog --transport stdio           # 9 tools
  python -m et_mcp.server --server all --transport stdio               # 17 tools (default)

HTTP (detached):
  python -m et_mcp.server --server catalog --transport streamable-http --port 8001
  python -m et_mcp.server --server site --transport streamable-http --port 8002
  python -m et_mcp.server --server calc --transport streamable-http --port 8003

Binding to a non-loopback address (Docker, LAN, reverse proxy) accepts any Host
header unless --allowed-host / MCP_ALLOWED_HOSTS lists the names clients use,
e.g. --allowed-host et-mcp:8001 --allowed-host mcp.example.com.

Inspector:
  npx -y @modelcontextprotocol/inspector
"""
from __future__ import annotations

import argparse
import functools
import json
import sys

try:
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    from mcp.server.fastmcp import FastMCP
    from mcp.server.transport_security import TransportSecuritySettings
    from mcp.types import CallToolResult, TextContent
    import anyio
except ImportError as e:
    raise ImportError("mcp not installed. Run: pip install -e .  (or pip install 'mcp>=1.28,<2')") from e

from et_mcp.tools.registry import TOOLSETS
from et_mcp.settings import settings

# Map user-facing names -> registry keys
NAME_MAP = {"calculator": "calc", "calc": "calc", "site": "site", "catalog": "catalog", "all": "all"}


def _security(allowed_hosts: list[str]) -> TransportSecuritySettings | None:
    """Host-header (DNS rebinding) protection.

    FastMCP derives this from the host given to its constructor, so it must be
    built here rather than patched onto settings after construction.
    """
    if allowed_hosts:
        return TransportSecuritySettings(enable_dns_rebinding_protection=True, allowed_hosts=allowed_hosts)
    return None  # FastMCP default: loopback hosts only for 127.0.0.1/localhost/::1, open otherwise


def _as_tool(fn):
    """Run a sync tool in a worker thread and flag error payloads.

    Tools do blocking DB and model-download work; FastMCP would otherwise call
    them on the event loop and stall every other session. Dict results carrying
    an "error" key are returned with isError=true (same JSON body) so clients can
    distinguish a failed call from evidence.
    """
    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        result = await anyio.to_thread.run_sync(functools.partial(fn, *args, **kwargs))
        if isinstance(result, dict) and result.get("error"):
            return CallToolResult(isError=True, structuredContent=result,
                                  content=[TextContent(type="text", text=json.dumps(result, indent=2, default=str))])
        return result
    return wrapper


def build_mcp(selected: str, host: str = "127.0.0.1", port: int = 8000, allowed_hosts: list[str] | None = None) -> FastMCP:
    key = NAME_MAP.get(selected, selected)
    if key == "all":
        name = "et-mcp"
        tools = {k: v for d in TOOLSETS.values() for k, v in d.items()}
    else:
        if key not in TOOLSETS:
            raise SystemExit(f"Unknown --server {selected!r}, choose from {list(NAME_MAP)}")
        name = f"et-mcp-{key}"
        tools = TOOLSETS[key]
    mcp = FastMCP(name, host=host, port=port, transport_security=_security(allowed_hosts or []))
    for tool_name, fn in tools.items():
        mcp.tool(name=tool_name)(_as_tool(fn))
    return mcp


def main() -> None:
    p = argparse.ArgumentParser(description="ET MCP domain servers (calc/site/catalog)")
    p.add_argument("--server", choices=["calc", "calculator", "site", "catalog", "all"], default="all",
                   help="Domain server to expose (default all=17 tools)")
    p.add_argument("--transport", choices=["stdio", "sse", "streamable-http"], default="stdio")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--allowed-host", action="append", default=[],
                   help="Host header accepted over HTTP, e.g. et-mcp:8001 (repeatable; also MCP_ALLOWED_HOSTS, comma-separated)")
    args = p.parse_args()
    allowed = args.allowed_host + [h.strip() for h in settings.mcp_allowed_hosts.split(",") if h.strip()]
    if allowed:
        allowed += ["127.0.0.1:*", "localhost:*", "[::1]:*"]
    mcp = build_mcp(args.server, args.host, args.port, allowed)
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
