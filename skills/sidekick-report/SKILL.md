---
name: sidekick-report
description: Surface a project's structured data/ store as reusable reports and interactive dashboards. Use when the user runs /sidekick-report or asks to see, present, visualize, chart, summarize, or build a dashboard/report over stored table data — "show me X as a dashboard", "give me the monthly breakdown again", "make a report of the contacts", "chart revenue by line". Sources data only via scripts/data.py query (never a raw JSON read). Saves the reusable report as a recipe in brain/reports.md (diff + approval) and renders a tabbed HTML dashboard into the project's artifacts/ folder (confirmation). Default is a self-contained snapshot (refresh = regenerate); optionally a live dashboard — the HTML is synced to Drive and a thin wrapper artifact loads it, so only the Drive file is overwritten on a data change (no per-refresh approval). The always-on sidekick-core skill routes clear "present/visualize the data" intents here.
---

# Sidekick — Report (present & reuse the data store)

You turn a project's `data/` store into things a human can read and re-run:
**saved reports** (reusable queries) and **rendered artifacts** (tabbed HTML
dashboards, sheets). You sit on top of the data discipline and never break
its one rule. Full protocol: `../sidekick-core/references/reporting.md`
(read it). Data rules: `../sidekick-core/references/data-discipline.md`.

## The one rule

**All data comes from `data.py query`** (or a saved recipe, which runs the
same engine). Never hand-read `data/*.json`, never make the page read the raw
table, never use the `sqlite3` CLI or ad-hoc `python`. You bake **computed
rows** into the HTML; the **calculation rule lives in the recipe, never in the
page**. **Default: snapshot** — a self-contained `.html` in `artifacts/`;
refresh = regenerate. **Optional: live** — sync that HTML to Drive and show it
through a **thin wrapper artifact** (loads the Drive HTML via the Drive
connector); a data change overwrites the Drive HTML, no per-refresh approval.
Full protocol incl. the wrapper: `../sidekick-core/references/reporting.md`.

## When you run

- The user runs `/sidekick-report [what they want]`, or
- they ask to see/present/visualize/chart/summarize stored data, or to
  "do that report again". The always-on skill may hand these to you.

## How you work

1. **Settings + project.** Read `sidekick.settings.md` (chat + output
   language). Determine the project (active one, or ask via the picker if
   unclear). The project must have a `data/` store — if it has none, say so
   and point to `data.py`/the data discipline; there is nothing to report on.
2. **Load existing recipes.** If `brain/reports.md` exists, read it — the
   user may be asking to re-run a saved report ("the monthly one again").
3. **Know the real shape.** Resolve the helper once — `$CLAUDE_PLUGIN_ROOT` is
   unset in the shell, so find it:
   `SK="$(find ~ -ipath '*/sidekick-core/scripts' -type d 2>/dev/null | head -1)"`,
   then `python3 "$SK/data.py" info --project projects/<slug>`
   for tables, columns, and category values. Match **exact** spellings in
   `WHERE` (e.g. `ON-PREM`, not `ONPREM`).
4. **Pick the lightest render that answers the need** (see reporting.md):
   a number → just `query` and answer; a keepable table → markdown in `log/` or
   a sheet in `output/`; something to explore → the project's **standard
   dashboard** (build/extend it; don't make a new artifact unless asked).
5. **Query each section** with `data.py query` and collect the JSON.
6. **Build with `dashboard.py` — never paste the kernel.** Shape the results into
   the dashboard's small data file `artifacts/<slug>-dashboard.sk.json` (a
   `window.SK` object: collections → views, each `kind: dashboard | grid |
   listdetail | home`; **computed** rows baked in, labels in the **default output
   language**). Then resolve the scripts dir
   (`find ~ -ipath '*/sidekick-core/scripts'`) and run
   `python3 "$SK/dashboard.py" build --project "<ABS>/projects/<slug>" --slug <slug> --title "<Project> Dashboard"`.
   The script bakes the UI kit + logo into `artifacts/<slug>-dashboard.html` — you
   never read or paste `ui.js`/`ui.css` (Cowork truncates the read → blank page).
   Full guide + data model: `../sidekick-core/references/ui-kit.md`.
7. **Save the recipe** if they'll want it again: add/update a section in
   `brain/reports.md` (name, purpose, the exact `SELECT`(s)) — a **brain write →
   diff + approval**. Also register it: `reports.py save --name <n> --sql "…"
   --artifact artifacts/<slug>-dashboard.html --tables <t1>,<t2>` (writes
   `.reports.json`; `reports.py uses --table <t>` drives regeneration).
8. **Show it as the live Cowork artifact (the deliverable).** Sync to Drive
   (`reconcile_output` covers `artifacts/`), resolve its Drive file id and save it
   (`reports.py save --name <slug>-dashboard --drive-file-id <id>`), then create
   the live artifact with **`mcp__cowork__create_artifact`** = the thin wrapper
   (file id + per-install `mcp__<uuid>__download_file_content` tool name). Present
   **that**, not the file. Later data changes: edit the `.sk.json`, re-run
   `dashboard.py build`, re-sync — no new artifact. Full steps: reporting.md →
   "Live dashboard". Without Drive/sync, fall back to a one-off snapshot file.

## Gatekeepers (reused — no new one)

- **Recipe** in `brain/reports.md` → **diff + approval**.
- **Artifact** in `output/` → **confirm** before create/overwrite, default
  output language.
- **Reading** the data → **free** (`query`/`info`).

## Boundaries

- **Data only through `data.py` (`query`/`info`).** Never read or `grep` the
  raw `data/*.json`; never the `sqlite3` CLI or ad-hoc `python`; never embed
  data you didn't get from a `query`.
- **Don't write data.** Reporting reads and presents; it never
  `insert`/`update`/`delete`/`create`/`addcol`. If the user wants to change
  records or structure, hand back to the normal `sidekick-core` data flow.
- **Don't grow `data.py`.** Reporting uses its existing `query`/`info`
  (Cowork truncates the helper past ~16 KB). Recipe-registry logic lives in
  `reports.py`, not `data.py`. Registering a recipe (`reports.py save`) mirrors
  an approved `brain/reports.md` entry — it is not a data-record write.
- **Dashboard built by `dashboard.py`, never hand-pasted.** The script bakes the
  **Sidekick UI kit** (`../sidekick-core/references/ui-kit.md`) + logo into one
  self-contained `artifacts/<slug>-dashboard.html`; you only edit the small
  `<slug>-dashboard.sk.json`. Never read/paste `ui.js`/`ui.css` inline (Cowork
  truncates the read → blank page). The **live Cowork artifact** that wraps the
  Drive html is the deliverable, and the only piece that calls a connector; the
  dashboard html itself makes no network calls.
