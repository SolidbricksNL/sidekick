#!/usr/bin/env python3
"""Sidekick data MCP server (`sidekick-data`, stdlib stdio, no deps).

READ-ONLY. Lets a live artifact fetch a saved report recipe's output by name,
so calculation rules live in the recipe (the agent owns them) - never in the
artifact's JavaScript. Two tools, both read-only:
  - run_report(project, name) -> the recipe's computed rows (via data.py query)
  - list_reports(project)     -> the available recipe names

It deliberately exposes NO write/mutate tools, so an artifact that can reach it
can only read. Recipes are saved by the agent via reports.py (gated as a brain
write). Protocol: reporting.md.
stdio rule: only JSON-RPC to stdout; logging to stderr.
Keep this file small - Cowork truncates large plugin files on install."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reports  # noqa: E402  (sibling module: registry + query engine)

_PROTOCOL = "2024-11-05"
_TOOLS = [
    {
        "name": "run_report",
        "description": ("Run a saved report recipe by name and return its "
                        "computed rows as JSON. Use this from a live artifact "
                        "instead of putting calculation rules in the page."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string",
                            "description": "ABSOLUTE path to the project dir, e.g. "
                                           "C:\\\\Claude Cowork\\\\Sidekick\\\\projects\\\\finance"},
                "name": {"type": "string", "description": "the saved recipe name"},
            },
            "required": ["project", "name"],
        },
    },
    {
        "name": "list_reports",
        "description": "List the saved report recipes for a project.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "ABSOLUTE path to the project dir"},
            },
            "required": ["project"],
        },
    },
]


def _log(msg):
    print(f"[sidekick-data] {msg}", file=sys.stderr, flush=True)


def _resolve_project(project):
    p = Path(project)
    if p.is_absolute():
        return str(p)
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    return str(Path(root) / project)


def _ok(req_id, payload):
    return {"jsonrpc": "2.0", "id": req_id,
            "result": {"content": [{"type": "text",
                                    "text": json.dumps(payload, ensure_ascii=False)}],
                       "isError": False}}


def _tool_error(req_id, message):
    return {"jsonrpc": "2.0", "id": req_id,
            "result": {"content": [{"type": "text", "text": f"error: {message}"}],
                       "isError": True}}


def _rpc_error(req_id, code, message):
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def _call_tool(req_id, name, args):
    try:
        if name == "run_report":
            return _ok(req_id, reports.run(_resolve_project(args["project"]), args["name"]))
        if name == "list_reports":
            return _ok(req_id, reports.list_reports(_resolve_project(args["project"])))
        return _tool_error(req_id, f"unknown tool {name!r}")
    except KeyError as e:
        return _tool_error(req_id, f"missing argument {e}")
    except ValueError as e:
        return _tool_error(req_id, str(e))
    except OSError as e:
        return _tool_error(req_id, f"filesystem error: {e}")


def handle(msg):
    method = msg.get("method")
    req_id = msg.get("id")
    if method == "initialize":
        ver = (msg.get("params") or {}).get("protocolVersion") or _PROTOCOL
        return {"jsonrpc": "2.0", "id": req_id,
                "result": {"protocolVersion": ver,
                           "capabilities": {"tools": {}},
                           "serverInfo": {"name": "sidekick-data", "version": "1.0"}}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": _TOOLS}}
    if method == "tools/call":
        params = msg.get("params") or {}
        return _call_tool(req_id, params.get("name"), params.get("arguments") or {})
    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    if "id" not in msg:
        return None  # notification - no reply
    return _rpc_error(req_id, -32601, f"method not found: {method}")


def main():
    _log("server starting")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            _log(f"ignoring non-JSON line: {line[:80]!r}")
            continue
        try:
            resp = handle(msg)
        except Exception as e:
            resp = _rpc_error(msg.get("id"), -32603, f"internal error: {e}")
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
