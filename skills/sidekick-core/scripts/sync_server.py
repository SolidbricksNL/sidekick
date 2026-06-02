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
                            "description": "project dir, e.g. projects/<slug> "
                                           "(relative to the workspace) or an absolute path"},
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
                "project": {"type": "string"},
                "base": {"type": "string"},
                "file": {"type": "string", "description": "conflicting relative path under output/"},
                "keep": {"type": "string", "enum": ["local", "external", "both"]},
            },
            "required": ["project", "base", "file", "keep"],
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
