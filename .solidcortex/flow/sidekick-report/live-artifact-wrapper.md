---
domains:
  - reporting
  - output-sync
flowId: sidekick-report
generatedAt: 2026-06-14T11:55:56Z
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generator: solidcortex@0.17.0
kind: derived
nodeId: live-artifact-wrapper
parent: main/sidekick-report
related:
  - write-disciplines/output-write
slug: live-artifact-wrapper
status: current
summary: Wraps the Drive-synced dashboard HTML in the primary deliverable — a thin live Cowork artifact created once via mcp__cowork__create_artifact that pulls the HTML from the Google Drive connector (download_file_content, base64 to iframe srcdoc); later data changes overwrite the Drive file in place, no new artifact.
systems:
  - mcp-server
  - ui-kit
type: integration
---

## TLDR (agent)
**Purpose:** Wrap the Drive-synced dashboard HTML in the primary deliverable — a thin live Cowork artifact, created once, that pulls the HTML from the Google Drive connector and frames it.
**Inputs:** A built `artifacts/<slug>-dashboard.html` synced to Drive; the Drive `file_id` (saved via `reports.py`); the per-install `mcp__<uuid>__download_file_content` tool name; the Drive connector + Output sync on.
**Outputs:** A live artifact via `mcp__cowork__create_artifact` (an iframe loading the HTML as base64 → `srcdoc`); on a data change the Drive file is overwritten in place (same id) — no new artifact, no approval.
**Code anchor:** [skills/sidekick-core/references/reporting.md](../../../skills/sidekick-core/references/reporting.md)
**Edges:** (none)
**Key rules:**
- The live Cowork artifact is the PRIMARY deliverable — present it, not the `.html` file via present_files.
- The artifact sandbox blocks local files and local MCP servers — only cloud connectors (Drive) are reachable, hence the wrapper.
- Created once; later data changes overwrite the Drive HTML in place (stable file id) — no new `create_artifact`, no approval.
- The `<uuid>` in the download tool name is per-install — read it from the session tools, never hard-code it.

## Functional (user facing)

### Why use this?
In Cowork the dashboard you actually look at is a live artifact, not a file you
have to download and reopen. This wrapper is what makes that work: it pulls the
latest dashboard from your Drive and shows it in place, so after the data
changes the same artifact just refreshes instead of being handed to you again.

### When it runs
It is created once, the first time a project's dashboard is shown (and at project
creation when Drive sync is already on). After that it does not need recreating —
it is only rebuilt if you delete it yourself or if it is expected but missing.

### What it talks to
It talks to your Google Drive through Cowork's Drive connector. The actual
dashboard file lives on Drive (kept in sync with the project's generated file);
the wrapper fetches that file and displays it. Nothing else is contacted — the
dashboard itself makes no network calls; only this thin wrapper reaches a
connector.

### Behind the scenes
The wrapper asks Drive for the dashboard file by its stable id, receives it as
encoded text, and renders it inside a framed view. Because the file id stays the
same across updates, a data change simply overwrites the file on Drive in place —
no new artifact is created and no approval is needed; Cowork's own refresh
re-pulls the latest. If loading fails, it shows a short error rather than a blank
frame. The artifact is yours: deleting it in Cowork is harmless — the durable
pieces (the description file, the generated HTML, the Drive file and its saved id)
are untouched, so it can be recreated cheaply.

### Pro tips
- Present the live artifact as the deliverable, not the underlying file.
- The interactivity (tabs, sorting, charts) lives in the dashboard on Drive, not
  the wrapper — the wrapper only fetches and frames it.
- Without the Drive connector or output sync, there is no live view: you get the
  generated dashboard as a one-off snapshot that opens anywhere but does not
  auto-update until Drive sync is configured.

### Related
- [sidekick-report/build-dashboard](build-dashboard.md) — builds the HTML this
  wrapper loads.

## Technical

This is the only artifact that crosses an **external** boundary (the Google Drive
connector); the dashboard HTML itself is self-contained and network-free. The
wrapper template and full setup live in
`skills/sidekick-core/references/reporting.md` → "Live dashboard"; architecture in
`docs/ARCHITECTURE.md` §7b.

Why a wrapper at all: the Cowork artifact sandbox blocks **local files and local
MCP servers** (a local `sidekick-data` server was tried and removed) — only cloud
connectors are reachable. And every `update_artifact` is approval-gated, so
re-emitting a fresh artifact on each data change would be friction. The wrapper
sidesteps both: it is created once and thereafter only the Drive file changes.

Setup (once per dashboard):
1. Build the HTML (`sidekick-report/build-dashboard`) →
   `projects/<slug>/artifacts/<slug>-dashboard.html`.
2. `reconcile_output` syncs `artifacts/` (and `output/`) so the file lands on
   Drive.
3. Resolve the Drive `file_id` (Drive connector, search by name) and persist it:
   `reports.py save --name <slug>-dashboard --drive-file-id <id>` (stable across
   overwrites — same file, same id).
4. Find the per-install download tool `mcp__<uuid>__download_file_content`
   (`<uuid>` read from the session tools, never hard-coded).
5. Create the live artifact with `mcp__cowork__create_artifact`, body = the thin
   wrapper.

The wrapper (an `<iframe sandbox="allow-same-origin allow-scripts">` plus a small
script): it calls `window.cowork.callMcpTool(TOOL, {fileId: FILE_ID})`, runs the
result through an `unwrap()` that peels every Drive-tool response shape
(`"<json>"` / `{content}` / `{content:[{text}]}` / `{base64Content}` / raw b64)
down to a base64 string, then `atob` + UTF-8 fixup → `iframe.srcdoc`. `allow-scripts`
is needed because the real interactivity runs inside the framed dashboard, not the
wrapper. A failure surfaces a short inline error, not a blank frame.

Lifecycle: realized as an empty skeleton at project scaffold (with the live
artifact created right away when Output sync is on, else on first show). The
artifact is the user's to delete — recreate with the stored file id when a
dashboard is expected and the artifact is gone; rebuild the HTML/Drive file first
if those are gone too; `build_dashboard` makes a fresh skeleton if even the
`.sk.json` is gone. **Never error on a missing dashboard — (re)build and
(re)create it.** Keeping it live: after a `data.py` write, `build_dashboard
{project}` → `reconcile_output` overwrites the Drive file in place (same id) — the
live artifact updates on Cowork's next refresh, no approval.

Gating: the live artifact is created once (`mcp__cowork__create_artifact`); later
content refreshes go to the Drive HTML, not the artifact — so they need no
approval. Requires the Drive connector + Output sync on (§7c); without them, fall
back to presenting the built `.html` as a one-off snapshot.

Dependencies: upstream `sidekick-report/build-dashboard` (produces the HTML);
external Google Drive connector + the per-install Cowork download tool; the
`sidekick-sync` MCP server's `reconcile_output` (sync) and `reports.py` (stores the
`drive_file_id`).
