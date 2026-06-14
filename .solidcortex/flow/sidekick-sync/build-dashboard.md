---
domains:
  - reporting
flowId: sidekick-sync
generatedAt: 2026-06-14T11:55:56Z
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generator: solidcortex@0.17.0
kind: derived
mainCodeFile: skills/sidekick-core/scripts/dashboard.py
nodeId: build-dashboard
parent: main/sidekick-sync
related:
  - sidekick-report/build-dashboard
slug: build-dashboard
status: current
summary: The build_dashboard tool — natively bakes a project's dashboard HTML from its sk.json bindings, resolving each query/recipe against the live data store and reading the full UI kit, with no-slug rebuilding every dashboard at once.
systems:
  - mcp-server
type: process
---

## TLDR (agent)
**Purpose:** Natively bake a project's dashboard HTML from its `dashboard/<slug>-dashboard.sk.json`, resolving each `query`/`recipe` binding against the live data store and reading the full UI kit + logo from disk.
**Inputs:** `project` (ABSOLUTE), optional `slug` (omit → rebuild every dashboard), optional `title` (skeleton only); the per-project sk.json plus the chunked `assets/ui.*.css|js` + `solidbricks.png`.
**Outputs:** `artifacts/<slug>-dashboard.html` written; JSON `{data, html, collections, changed}` (or `build_all`: `{ok, count, built[], any_changed}`).
**Code anchor:** [skills/sidekick-core/scripts/dashboard.py](../../../skills/sidekick-core/scripts/dashboard.py)
**Edges:** (none)
**Key rules:**
- The agent edits only the tiny sk.json; it never reads or pastes the UI kernel (an inline read truncates at ~11 KB → blank page).
- A failing binding raises loudly (named query) rather than baking a silently stale page; assets truncated on read raise instead of writing a broken dashboard.
- After any data write, call with project only to rebuild every dashboard, then reconcile_output to push to Drive.

## Functional (user facing)

### Why use this?
This is how a project's dashboard gets made and kept current. You never hand-edit numbers into a web page — you describe what each KPI, chart, table, or grid should show, and this tool fills it from your live data and produces a single, self-contained HTML dashboard with the real Sidekick look. Re-running it after a data change is all it takes to refresh every figure.

### What it does
- Reads the small per-project layout file (`dashboard/<slug>-dashboard.sk.json`) — the only part you ever edit.
- Pulls the actual current numbers for every bound element straight from the data store at build time, so the dashboard is a live view, never a stale snapshot.
- Bakes the complete page from the shared design kit (styles, behaviour, the Solidbricks logo) read fresh from disk, producing one file that needs no network to open.
- With no slug given, rebuilds every dashboard in the project in one call — the right move after any data change.
- Reports whether the HTML actually changed, so a no-op rebuild is visible rather than silent.
- Builds an empty branded skeleton the first time, so a brand-new project has a valid dashboard to grow into.

### When it runs
Right after any change to the data store, and whenever you ask to add or update something on a dashboard. The agent rebuilds, then syncs the result to Drive so the live artifact you see refreshes in place.

### Behind the scenes
The tool runs natively on your machine, which lets it read the full design kit reliably — a sandboxed read would truncate it and produce a blank page, which is exactly why a native build exists. If a data query behind a tile is wrong, it stops with the offending query named instead of quietly showing old figures. The editable layout file lives in a local, non-synced folder so reads of it are always reliable; only the finished HTML goes to your Drive folder.

### Pro tips
- Add a tile by editing the layout file and rebuilding in place — a new dashboard is created only when you explicitly ask for one.
- Always pass the absolute project path; Cowork's working directory is a scratchpad, not your workspace.
- If a rebuild reports an error about a binding, fix that one query — the page is intentionally never baked half-stale.

### Related
- sidekick-sync/save-report — registers the report recipe a dashboard tile can bind to by name.
- sidekick-sync/reconcile-output — pushes the built HTML out to Drive after a rebuild.
- sidekick-sync/mcp-server — the host process that exposes this tool.

