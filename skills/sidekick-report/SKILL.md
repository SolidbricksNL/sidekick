---
name: sidekick-report
description: Surface a project's structured data/ store as reusable reports and interactive dashboards. Use when the user runs /sidekick-report or asks to see, present, visualize, chart, summarize, or build a dashboard/report over stored table data — "show me X as a dashboard", "give me the monthly breakdown again", "make a report of the contacts", "chart revenue by line". Sources data only via scripts/data.py query (never a raw JSON read). Saves the reusable report as a recipe in brain/reports.md (diff + approval) and renders a tabbed HTML dashboard into output/ (confirmation). Default is a self-contained snapshot (refresh = re-run); optionally a live artifact that fetches a saved recipe by name via the read-only sidekick-data MCP server. The always-on sidekick-core skill routes clear "present/visualize the data" intents here.
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
table, never use the `sqlite3` CLI or ad-hoc `python`. **Default: snapshot** —
the artifact carries your query results embedded; refresh = re-run. **Optional:
live** — the artifact fetches a saved recipe **by name** via the read-only
`sidekick-data` MCP server (`run_report`), with a snapshot fallback baked in.
Either way the **calculation rule lives in the recipe, never in the page**.
Full protocol incl. the live skeleton: `../sidekick-core/references/reporting.md`.

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
3. **Know the real shape.** Run
   `python3 "$CLAUDE_PLUGIN_ROOT/skills/sidekick-core/scripts/data.py" info --project projects/<slug>`
   for tables, columns, and category values. Match **exact** spellings in
   `WHERE` (e.g. `ON-PREM`, not `ONPREM`). (Fallback path if
   `$CLAUDE_PLUGIN_ROOT` is unset:
   `~/.claude/plugins/sidekick/skills/sidekick-core/scripts/data.py`.)
4. **Pick the lightest render that answers the need** (see reporting.md):
   a number → just `query` and answer; a keepable table → markdown in
   `log/` or a sheet in `output/`; something to explore → a tabbed HTML
   dashboard in `output/`.
5. **Query each tab/section** with `data.py query` and collect the JSON.
6. **Render.** For a dashboard, build **one self-contained `.html`** with the
   results **embedded** (a JSON `<script>` block per tab), inline vanilla-JS
   rendering, **no network calls** — adapt the skeleton in reporting.md. One
   tab per query; sortable tables; a simple inline-SVG bar chart for
   label+number tabs. Headings in the **default output language**.
7. **Save the recipe** if this is something they'll want again: add/update a
   section in `brain/reports.md` (name, plain-language purpose, the exact
   `SELECT`(s), the render target) — a **brain write → show the diff, get
   approval**. For a **live** artifact, also register it machine-readably:
   `reports.py save --project projects/<slug> --name <n> --sql "…"` (writes
   `.reports.json`; the `sidekick-data` server runs it by name).
8. **Write the artifact** to `output/` only after **confirmation** (it's a
   deliverable). **Snapshot** (default): embed the query results. **Live**
   (if the user wants always-fresh): have the page call `run_report` by name
   and **embed a snapshot fallback** too (see reporting.md). Then tell the user
   which mode it is and how to refresh.

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
- **Self-contained artifacts.** One file, data embedded, no external
  CSS/JS/fetch — opens straight from `output/` and works in the sandbox.
