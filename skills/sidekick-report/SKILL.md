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
   a number → just `query` and answer; a keepable table → markdown in
   `log/` or a sheet in `output/`; something to explore → a tabbed HTML
   dashboard in `output/`.
5. **Query each tab/section** with `data.py query` and collect the JSON.
6. **Render.** Build **one self-contained `.html`** with the results
   **embedded** (a JSON `<script>` block per tab), inline vanilla-JS rendering,
   **no network calls** — adapt the skeleton in reporting.md. One tab per query;
   sortable tables; a simple inline-SVG bar chart for label+number tabs.
   Headings in the **default output language**. Write it to
   `artifacts/<name>.html` after **confirmation**.
7. **Save the recipe** if they'll want it again: add/update a section in
   `brain/reports.md` (name, purpose, the exact `SELECT`(s), the render target)
   — a **brain write → diff + approval**. Also register it machine-readably:
   `reports.py save --name <n> --sql "…" --artifact artifacts/<n>.html
   --tables <t1>,<t2>` (writes `.reports.json`; drives regeneration on a data
   change via `reports.py uses --table <t>`).
8. **For a live dashboard** (always-fresh without re-emitting an artifact):
   sync the HTML to Drive (`reconcile_output` now covers `artifacts/`), resolve
   its Drive file id and save it (`reports.py save --name <n> --drive-file-id
   <id>`), then emit the **thin wrapper** once (filling in the file id + the
   per-install `mcp__<uuid>__download_file_content` tool name). On later data
   changes: regenerate the HTML + re-sync — no artifact update. Full steps:
   reporting.md → "Live dashboard". Tell the user which mode it is.

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
- **Self-contained dashboard HTML.** One file in `artifacts/`, data embedded,
  no external CSS/JS/fetch — works as a snapshot and as the body the live
  wrapper loads from Drive. (The wrapper itself is the only artifact that calls
  a connector; the dashboard HTML never does.)
