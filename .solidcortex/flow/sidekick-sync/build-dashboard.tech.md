---
flowId: sidekick-sync
nodeId: build-dashboard
slug: build-dashboard
status: current
kind: derived
summary: The build_dashboard tool — natively bakes a project's dashboard HTML from its sk.json bindings, resolving each query/recipe against the live data store and reading the full UI kit, with no-slug rebuilding every dashboard at once.
systems: [mcp-server]
domains: [reporting]
parent: sidekick-sync/mcp-server
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## Technical

**Entry point.** The `build_dashboard` MCP tool is declared in `skills/sidekick-core/scripts/sync_server.py` (`_TOOLS[2]`). `_call_tool` resolves the project, then branches: `if args.get("slug")` → `dashboard.build(proj, slug, title)`, else → `dashboard.build_all(proj)`. Input schema requires only `project`; `slug` and `title` are optional (omit slug to rebuild all).

**Main code.** `skills/sidekick-core/scripts/dashboard.py` (~296 LOC). Entry functions `build` / `build_all`; a `path` subcommand prints the resolved paths.

**Paths.** `_paths(project, slug)` returns `(proj/artifacts, proj/dashboard/<slug>-dashboard.sk.json, proj/artifacts/<slug>-dashboard.html)`. The editable source sits in a LOCAL, non-synced `dashboard/` subfolder (reliable reads); the built HTML goes to the Drive-synced `artifacts/`. `build` requires an ABSOLUTE project path (raises `RuntimeError` otherwise) and migrates a legacy pre-v0.16.0 root-level `<slug>-dashboard.sk.json` into `dashboard/`, reading it `utf-8-sig` to tolerate a BOM.

**Build flow (`build`).** Loads the sk.json (`utf-8-sig`) if present (overriding `workspace` with `title` when given), else writes a fresh `_skeleton(title)` — a branded shell with one placeholder "Overview" collection. Then `_resolve_bindings(project, data)` mutates the SK in place, `_assemble(data)` bakes the HTML, and `changed = new_html != prev` is computed against the prior file (a placeholder/unhydrated `prev` read that OSErrors → treated as no prior). The HTML is written and `{data, html, collections, changed}` returned.

**Binding resolution.** `_resolve_bindings` lazily imports the sibling `data` (query engine) and `reports` (recipe registry, optional). `rows_for(el)` runs `reports.run(project, el["recipe"])` for a `recipe` binding or `data.query(project, el["query"])` for a `query` binding, returning `rows`; any failure raises `RuntimeError("dashboard binding failed (<ref>): …")` naming the offending query/recipe — so a bad binding is loud, never a silently stale page. `resolve(node)` walks `kpis` (first row → kpi fields via `_unbind`), `cards` (`chart.data` / `table.rows`), `panels` (`items`), grid views (`kind:grid` → `rows`), list-detail views (`kind:listdetail` → `items`), and `totals_query` (grid totals row). It runs over each collection's home and each `views[]` entry.

**Assembly + truncation guard.** `_concat(glob_pat)` joins the chunked kit (`ui.1.css`, `ui.2.css`, … / `ui.1.js`, …) in numeric order — the kit is shipped in <9 KB chunks because Cowork's `.remote-plugins` mount truncates a script-read of a ~11 KB file. `_assemble` enforces end-sentinels: the assembled JS must end with `render();` and the CSS must be ≥4000 B and end with `}`; either failing raises `RuntimeError` instead of baking a partial (blank) kernel. The logo is read from `assets/solidbricks.png` and inlined as a base64 data URI; `window.SK` carries the resolved SK JSON, `window.SB_LOGO` the logo. `_esc` HTML-escapes the title.

**build_all.** `_dashboard_slugs(project)` collects slugs from `dashboard/*-dashboard.sk.json` plus any legacy root-level file; `build_all` rebuilds each (each keeps its own title) and returns `{ok, count, built[], any_changed}`. This is the no-slug path used after a data write so one call refreshes every dashboard.

**Dependencies.** `data.py` (query engine) and `reports.py` (recipe registry, see sidekick-sync/save-report). Reads `assets/ui.*.css|js` + `solidbricks.png`. Rationale (native build vs sandbox truncation, sk.json as bindings-not-values, one dashboard per project) in `docs/ARCHITECTURE.md` §7b and `references/ui-kit.md`.
