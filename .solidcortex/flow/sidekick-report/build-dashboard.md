---
domains:
  - reporting
edges:
  - label: show as live artifact
    to: sidekick-report/live-artifact-wrapper
    via: calls
flowId: sidekick-report
generatedAt: 2026-06-14T11:55:56Z
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generator: solidcortex@0.17.0
kind: derived
mainCodeFile: skills/sidekick-core/scripts/dashboard.py
nodeId: build-dashboard
parent: main/sidekick-report
related:
  - sidekick-sync/build-dashboard
slug: build-dashboard
status: current
summary: Shapes the tiny per-project dashboard/<slug>-dashboard.sk.json (window.SK layout with query/recipe bindings, not numbers) and calls build_dashboard, which resolves the bindings natively and bakes the shared UI kit plus fresh rows into a self-contained artifacts/<slug>-dashboard.html.
systems:
  - python-helpers
  - ui-kit
type: process
---

## TLDR (agent)
**Purpose:** Shape the tiny per-project `dashboard/<slug>-dashboard.sk.json` (layout + query/recipe bindings, not numbers) and call `build_dashboard`, which resolves the bindings natively and bakes the shared UI kit + fresh rows into `artifacts/<slug>-dashboard.html`.
**Inputs:** Rows/queries from query-data-store; a `window.SK` `.sk.json` (collections → views, each `kind: dashboard|grid|listdetail|home`) with each element bound to a `query`/`recipe`; an absolute project path + slug + title.
**Outputs:** A self-contained `artifacts/<slug>-dashboard.html` (UI kit + logo + baked rows), a `changed` flag, and the `.sk.json` (skeleton on first build); a loud `RuntimeError` on a bad binding or truncated asset.
**Code anchor:** [skills/sidekick-core/scripts/dashboard.py](../../../skills/sidekick-core/scripts/dashboard.py)
**Edges:** → sidekick-report/live-artifact-wrapper (calls — show as live artifact)
**Key rules:**
- Never read or paste the ~11 KB UI kernel — the build script reads the assets natively and bakes the page; an inline paste truncates to a blank page.
- The `.sk.json` stores QUERIES/recipes, not numbers; bindings resolve at build time, so a data change = rebuild, never hand-edit values.
- One dashboard per project, edited in place; a new artifact only on an explicit "make a separate dashboard" request.
- The `.sk.json` lives in the local `dashboard/` subfolder (reliable read), never the project root or the Drive-synced `artifacts/`.

## Functional (user facing)

### Why use this?
This is how stored data becomes something you can actually explore: a branded,
tabbed dashboard with KPI cards, charts, sortable tables and list+detail views.
You do not assemble the page; you describe what should be on it and the figures
are pulled in live, so the dashboard reflects the current data rather than a
frozen copy.

### What it does
- Builds each project's single dashboard from the shared Sidekick design — a
  sidebar, a centered project title, tabbed views, a light/paper/dark theme, KPI
  and section cards, bar and horizontal-bar charts, sortable grids, and
  list+detail panels, with the Solidbricks logo in the footer.
- Stores not the numbers but the questions: every card, chart, table and KPI
  carries the query that fills it, so the figures are recomputed each time the
  dashboard is built.
- Produces one self-contained file that opens on its own and makes no network
  calls, so it works both as a standalone snapshot and as the body the live view
  loads.
- Keeps one dashboard per project. "Add this to the dashboard" extends the
  existing one in place; a brand-new dashboard happens only when you explicitly
  ask for a separate one.

### When the data changes
Because the dashboard remembers the questions, not the answers, you never edit
numbers by hand. After the data changes, rebuilding re-runs every question and
bakes in the fresh figures — one rebuild refreshes every dashboard in the
project, and it reports whether anything actually moved.

### When a query is broken
A query that points at a missing table or column does not produce a quietly
stale page — the build stops and says which query failed, so a dashboard never
silently shows old or wrong numbers.

### Behind the scenes
The heavy, brand-consistent rendering engine and the real logo are read from
disk by the builder and folded into the page for you — you only ever touch a
small description file. The builder also checks that the engine read in full and
refuses to produce a page rather than risk a blank one. Labels follow your
project's default output language.

### Pro tips
- To change what is shown, edit the small description file and rebuild — never
  the big generated page.
- After any change to the data, rebuild so the dashboard catches up; do not wait
  to notice it is stale.
- Keep it simple: one collection with a single home or dashboard view is a
  perfectly good report — add tabs only when the project has genuinely separate
  areas.

### Related
- [sidekick-report/query-data-store](query-data-store.md) — sources the rows /
  bindings the dashboard renders.
- [sidekick-report/save-report-recipe](save-report-recipe.md) — a card may bind to
  a saved recipe by name.
- [sidekick-report/live-artifact-wrapper](live-artifact-wrapper.md) — wraps the
  built HTML as the live Cowork deliverable.

## Technical

`skills/sidekick-core/scripts/dashboard.py` builds the page; the
`sidekick-sync` MCP server's **`build_dashboard`** tool runs it **natively**
(reliable filesystem) and is the primary path. The bash `dashboard.py` is a
fallback only — the Cowork `.remote-plugins` mount truncates a script-read of it
(a 12 KB read came back at ~11.4 KB → `SyntaxError`/blank page).

Files (`_paths`, ~L123): editable source
`<project>/dashboard/<slug>-dashboard.sk.json` (local, non-synced → reliable read;
**not** the project root, **not** the Drive-synced `artifacts/` whose files can be
cloud-only placeholders); built output `<project>/artifacts/<slug>-dashboard.html`
(written, never read back).

Data model: a `window.SK` object — `workspace` (the project title), `theme`,
`accent`, and `collections` (sidebar entries → `views`/`home`/`empty`). View
`kind ∈ dashboard | grid | listdetail | home`. Full model: `references/ui-kit.md`.

Build (`build`, ~L202) — `--project` must be absolute (else `RuntimeError`):
1. Ensure `artifacts/` + `dashboard/` exist; migrate a legacy root-level
   `<slug>-dashboard.sk.json` (pre-v0.16.0) into `dashboard/`, BOM-tolerant.
2. Load the `.sk.json` (or write a branded **`_skeleton`** when none exists).
3. **`_resolve_bindings`** (~L138) walks every KPI / card chart / card table /
   home panel / grid / listdetail / `totals_query`, runs each element's `query`
   (via `data.query`) or `recipe` (via `reports.run`) **natively**, and replaces
   the binding with the live rows in place — aliasing SELECT columns to the
   renderer's field names. A failing binding raises a `RuntimeError` naming the
   query (no silent stale). Elements with no binding keep literal values, so
   older hand-authored dashboards still build.
4. **`_assemble`** (~L82) concatenates the chunked `assets/ui.*.css` + `ui.*.js`
   (shipped < 9 KB each to survive the truncating mount; joined in numeric
   order), guards the end-sentinels (`render();` / closing `}`) and raises rather
   than bake a partial blank page, base64-embeds `solidbricks.png`, and bakes one
   self-contained HTML. Returns `{data, html, collections, changed}` (`changed` =
   did the html move vs. the prior build).

`build_all` (~L255) rebuilds **every** dashboard slug in the project (`build` with
no slug) and returns `any_changed` — the post-data-change path. The proactive
trigger (after a `data.py insert/update/delete`: `build_dashboard {project}` →
`reconcile_output`, same turn) is described in `references/reporting.md` →
"Keeping it live."

Dependencies: imports sibling `data.py` (query engine) and `reports.py` (recipe
`run`) lazily for binding resolution — both documented in their own nodes
(`sidekick-report/query-data-store`, `sidekick-report/save-report-recipe`); the UI
kit assets in `skills/sidekick-core/assets/`. Downstream:
`sidekick-report/live-artifact-wrapper` turns the built HTML into the live Cowork
deliverable. Architecture: `docs/ARCHITECTURE.md` §7b.
