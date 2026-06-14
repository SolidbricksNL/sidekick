---
flowId: sidekick-sync
nodeId: mcp-server
type: process
slug: mcp-server
status: current
kind: derived
summary: The sidekick-sync MCP server process — a stdlib JSON-RPC-over-stdio loop that declares the four sync/dashboard/report tools and dispatches each tools/call to the native engine.
systems: [mcp-server]
domains: [output-sync]
parent: main/sidekick-sync
mainCodeFile: skills/sidekick-core/scripts/sync_server.py
entry: true
edges:
  - to: sidekick-sync/reconcile-output
    via: calls
    label: reconcile_output tool
  - to: sidekick-sync/resolve-output
    via: calls
    label: resolve_output tool
  - to: sidekick-sync/build-dashboard
    via: starts
    label: build_dashboard tool
  - to: sidekick-sync/save-report
    via: starts
    label: save_report tool
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Native host process that speaks JSON-RPC over stdio and exposes the four Sidekick host-side tools (reconcile_output, resolve_output, build_dashboard, save_report) to Cowork.
**Inputs:** Newline-delimited JSON-RPC requests on stdin (initialize, tools/list, tools/call, ping); tool args carry paths only, never file bytes.
**Outputs:** One JSON-RPC response line per request on stdout; tool results wrapped as MCP text content; all logging to stderr.
**Code anchor:** [skills/sidekick-core/scripts/sync_server.py](../../../skills/sidekick-core/scripts/sync_server.py)
**Edges:** → sidekick-sync/reconcile-output (calls), → sidekick-sync/resolve-output (calls), → sidekick-sync/build-dashboard (starts), → sidekick-sync/save-report (starts)
**Key rules:**
- Only JSON-RPC goes to stdout; every diagnostic goes to stderr (a stray stdout line corrupts the protocol).
- The wire is forced ASCII (`ensure_ascii=True`) so a response survives any host stdout encoding; the agent passes paths, never bytes.
- One bad message never kills the loop — a malformed line is logged and skipped, an internal error becomes an RPC error reply.

## Functional (user facing)

### Why use this?
This is the always-on helper that lets Sidekick do three things the agent cannot do on its own from inside the sandbox: copy finished files to your synced Drive folder, build a dashboard from the real design kit, and remember a report recipe. It runs quietly in the background; you never call it directly — the typed skills do, and you only see the results (a synced file, a refreshed dashboard, a saved report).

### What it does
- Publishes exactly four host-side capabilities to Cowork: two-way output sync, conflict resolution, native dashboard builds, and report-recipe registration.
- Runs as a real process on your machine (not in the sandbox), which is the whole reason it can reach your Drive folder and read the full design kit from disk.
- Moves only paths through the conversation — the actual file contents never pass through the model, so a large Excel or HTML never costs tokens or stalls.
- Handles non-Latin characters (the euro sign, middots, accented names) end to end without garbling them.

### Behind the scenes
On startup it pins its input and output streams to UTF-8, announces itself to Cowork during the handshake, then listens line by line. Each request names one of the four tools; the server hands the work to the matching native engine and streams back a compact JSON result. If a request is malformed or a tool throws, the server reports the problem cleanly and keeps running so the session is never left without its sync helper.

### Pro tips
- If a tool reports a path error, it is almost always a relative project path — every tool wants the ABSOLUTE project directory, because Cowork's working directory is a scratchpad, not your workspace.
- The server stays up for the whole session; there is nothing to restart between tool calls.

### Related
- sidekick-sync/reconcile-output — the two-way output/artifacts sync tool.
- sidekick-sync/resolve-output — settles a sync conflict you chose.
- sidekick-sync/build-dashboard — bakes a project's dashboard HTML.
- sidekick-sync/save-report — registers a report recipe.

## Technical

**Main code:** `skills/sidekick-core/scripts/sync_server.py` — the whole server: tool table, JSON-RPC dispatch, stdio loop.

**Shape.** A dependency-free stdlib script (json, os, sys, pathlib). It inserts its own directory on `sys.path` and imports three sibling engine modules at load time: `sync` (reconcile/resolve), `dashboard` (build/build_all), `reports` (save). The file is deliberately small because Cowork truncates large plugin files on install.

**Tool declarations.** `_TOOLS` is a static list of four MCP tool specs (`name`, `description`, `inputSchema`). All four require an ABSOLUTE `project` path; the descriptions carry the operational guidance the agent reads (e.g. "OMIT slug to rebuild every dashboard", "never resolve conflicts — ask the user then call resolve_output", the recipe-vs-registration split). `tools/list` returns this list verbatim.

**Dispatch.** `handle(msg)` routes by `method`:
- `initialize` → echoes the client `protocolVersion` (default `2024-11-05`), advertises `capabilities.tools`, serverInfo `{name: sidekick-sync, version: 1.0}`.
- `tools/list` → `{tools: _TOOLS}`.
- `tools/call` → `_call_tool(req_id, name, arguments)`.
- `ping` → `{}`.
- A notification (no `id`, e.g. `notifications/initialized`) → `None` (no reply).
- Anything else → JSON-RPC error `-32601 method not found`.

`_call_tool` resolves the project path via `_resolve_project` (absolute passthrough, else joined under `CLAUDE_PROJECT_DIR`/cwd), then calls the engine: `sync.reconcile`, `sync.resolve`, `dashboard.build` / `dashboard.build_all` (no slug → build_all), `reports.save`. Errors are mapped to MCP tool errors: `KeyError` → "missing argument", `RuntimeError`/`ValueError` → message, `OSError` → "filesystem error".

**Result envelopes.** `_ok` wraps the engine dict as MCP `content: [{type:text, text: json}]` with `isError:false`; `_tool_error` is the `isError:true` form; `_rpc_error` is a protocol-level error object.

**stdio + encoding.** `main()` reconfigures stdin/stdout/stderr to UTF-8 (so non-ASCII in a `tools/call` is decoded correctly — a real query-correctness fix, not cosmetic), logs "server starting" to stderr, then loops over stdin lines. Each line is `json.loads`-parsed (non-JSON logged and skipped); `handle` runs inside a broad `try` so an unexpected exception becomes a `-32603 internal error` reply rather than killing the loop. Responses are emitted with default `ensure_ascii=True`, so the wire line is pure ASCII `\uXXXX` escapes and survives any host stdout encoding; Cowork's JSON parser restores the original characters.

**Dependencies.** Registered in `.claude-plugin/plugin.json` under `mcpServers`. Calls into the four leaf nodes' engines (`sync.py`, `dashboard.py`, `reports.py`, which in turn use `data.py`). Rationale and the "why native, not a connector or the sandbox shell" argument live in `docs/ARCHITECTURE.md` §7c.
