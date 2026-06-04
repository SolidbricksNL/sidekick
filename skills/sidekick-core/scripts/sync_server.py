#!/usr/bin/env python3
"""Sidekick output-sync MCP server (stdlib stdio, no third-party deps).

Why this exists: the agent's Bash tool runs in a sandbox whose writes do NOT
reach the filesystem the storage client (Google Drive for Desktop / OneDrive)
watches, so a shell-invoked sync never syncs. A plugin MCP server runs as a
*native host* process and CAN write to the watched path. It exposes the same
engine as sync.py as two tools, so the model passes only paths - file bytes
never go through the model. Protocol: sync-discipline.md.

stdio rule: only JSON-RPC goes to stdout; all logging goes to stderr.
Keep this file small - Cowork truncates large plugin files on install."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sync  # noqa: E402  (sibling module: the shared sync engine)
import dashboard  # noqa: E402  (sibling: the dashboard builder)

_PROTOCOL = "2024-11-05"
_TOOLS = [
    {
        "name": "reconcile_output",
        "description": ("Two-way sync a project's output/ with the external "
                        "base path (file copies, binary-safe). Returns JSON: "
                        "pushed, pulled, in_sync, conflicts, errors. Never "
                        "resolves conflicts - ask the user, then call "
                        "resolve_output."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string",
                            "description": "ABSOLUTE path to the project dir, e.g. "
                                           "C:\\\\Claude Cowork\\\\Sidekick\\\\projects\\\\finance. "
                                           "Pass the full path - a relative path may "
                                           "resolve against the wrong directory."},
                "base": {"type": "string",
                         "description": "external base path, e.g. G:\\\\My Drive\\\\sidekick"},
            },
            "required": ["project", "base"],
        },
    },
    {
        "name": "resolve_output",
        "description": "Settle one output-sync conflict the user chose.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "ABSOLUTE path to the project dir (same as reconcile_output)"},
                "base": {"type": "string"},
                "file": {"type": "string", "description": "conflicting relative path under output/"},
                "keep": {"type": "string", "enum": ["local", "external", "both"]},
            },
            "required": ["project", "base", "file", "keep"],
        },
    },
    {
        "name": "build_dashboard",
        "description": ("(Re)build a project's dashboard HTML from its "
                        "dashboard/<slug>-dashboard.sk.json. Runs NATIVELY so it reads the "
                        "full UI kit + logo AND resolves the sk.json's `query`/`recipe` "
                        "bindings against the live data store (via data.py) - so the html "
                        "always shows CURRENT numbers, no hand-editing. Prefer this over the "
                        "bash dashboard.py (the sandbox mount truncates it). OMIT `slug` to "
                        "rebuild EVERY dashboard in the project - do this after any data.py "
                        "write so all dashboards refresh in one call. Returns JSON with "
                        "`changed` (did the html actually move). Then call reconcile_output "
                        "to push to Drive."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string",
                            "description": "ABSOLUTE path to the project dir (same as reconcile_output)"},
                "slug": {"type": "string", "description": "project slug, e.g. finance. "
                         "OMIT to rebuild every dashboard in the project."},
                "title": {"type": "string",
                          "description": "optional dashboard title, e.g. 'Finance Dashboard' "
                                         "(only needed for a fresh skeleton)"},
            },
            "required": ["project"],
        },
    },
]


def _log(msg):
    print(f"[sidekick-sync] {msg}", file=sys.stderr, flush=True)


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
        if name == "reconcile_output":
            proj = _resolve_project(args["project"])
            return _ok(req_id, sync.reconcile(proj, args["base"]))
        if name == "resolve_output":
            proj = _resolve_project(args["project"])
            return _ok(req_id, sync.resolve(proj, args["base"], args["file"], args["keep"]))
        if name == "build_dashboard":
            proj = _resolve_project(args["project"])
            if args.get("slug"):
                return _ok(req_id, dashboard.build(proj, args["slug"], args.get("title")))
            return _ok(req_id, dashboard.build_all(proj))
        return _tool_error(req_id, f"unknown tool {name!r}")
    except KeyError as e:
        return _tool_error(req_id, f"missing argument {e}")
    except RuntimeError as e:
        return _tool_error(req_id, str(e))
    except OSError as e:
        return _tool_error(req_id, f"filesystem error: {e}")


def handle(msg):
    method = msg.get("method")
    req_id = msg.get("id")
    is_request = "id" in msg
    if method == "initialize":
        ver = (msg.get("params") or {}).get("protocolVersion") or _PROTOCOL
        return {"jsonrpc": "2.0", "id": req_id,
                "result": {"protocolVersion": ver,
                           "capabilities": {"tools": {}},
                           "serverInfo": {"name": "sidekick-sync", "version": "1.0"}}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": _TOOLS}}
    if method == "tools/call":
        params = msg.get("params") or {}
        return _call_tool(req_id, params.get("name"), params.get("arguments") or {})
    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    if not is_request:
        return None  # a notification (e.g. notifications/initialized) - no reply
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
        except Exception as e:  # never let one bad message kill the server
            resp = _rpc_error(msg.get("id"), -32603, f"internal error: {e}")
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
