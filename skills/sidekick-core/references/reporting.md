# Presentation & reporting (`sidekick-report`)

The full protocol for surfacing a project's `data/` store: **saved reports**
(reusable queries) and **rendered artifacts** (tabbed HTML dashboards,
sheets). Loaded on demand by the `sidekick-report` skill and by `sidekick`
when the user wants to *see* the data. Read `data-discipline.md` first — this
layer sits on top of it and never breaks its one rule.

## The one rule still holds: data comes from `data.py query`

A report **never** reaches the data any other way. You run
`data.py query`, take the JSON result, and use it. You do **not** hand-read
`data/*.json`, you do **not** make the rendered page read the raw table, and
you do **not** use the `sqlite3` CLI or ad-hoc `python`. The page carries a
**snapshot** of a query result — already filtered and shaped by your
`SELECT` — embedded in the file. This keeps the single-access-path rule from
`data-discipline.md` intact even for a "live"-feeling dashboard.

There are **two ways to present** (pick per need — both bake **computed** rows
into the page; the calc rule stays in the recipe, never in the page's JS):

- **Snapshot (default).** A self-contained `.html`: tabs, sorting, charts run
  in the page, numbers are as of generation. **Refresh = re-run the report**
  (regenerate the file). Opens anywhere; no Drive, no connector. Use this
  unless the user wants the view to update without you regenerating an artifact.
- **Live dashboard (Drive-wrapped).** The same generated `.html` is **synced to
  Drive**; a **thin wrapper artifact** loads it from Drive (via the Drive
  connector) into an iframe. Then the artifact never needs updating again — you
  only **overwrite the Drive HTML** when data/rules change (no approval), and
  Cowork's refresh re-pulls it. This exists because the artifact sandbox blocks
  **local files and local MCP servers**; only **cloud connectors** (Drive) are
  reachable, and **every `update_artifact` is approval-gated** — so re-emitting
  a fresh artifact on each change is friction. See "Live dashboard" below.

## A report = recipe + artifact

| Half | Where | Gatekeeper |
|------|-------|------------|
| **Recipe** — the reusable report definition | `brain/reports.md` | diff + approval (it's a brain write) |
| **Artifact** — the produced file | `output/` | confirm (it's a deliverable) |

You may build a one-off view without saving a recipe. But the moment the
user asks for something **again**, save it as a recipe so "run it again" is
trivial next time. The recipe *is* the reusable software — no need to
re-derive the query.

### `brain/reports.md` format

One section per report. Plain language + the exact SQL, so any session can
re-run it without re-inspecting the data.

```markdown
# Reports

_Last updated: 2026-06-02_

## monthly-revenue
What: revenue per product line for the current year, biggest first.
Render: html dashboard (tabs: by line, by month) → output/monthly-revenue.html
Queries:
- by_line:  SELECT line, SUM(amount) AS revenue FROM deals
            WHERE year = 2026 GROUP BY line ORDER BY revenue DESC
- by_month: SELECT month, SUM(amount) AS revenue FROM deals
            WHERE year = 2026 GROUP BY month ORDER BY month
```

Saving or changing a recipe is a **brain write** → show the diff, get
approval. Keep the SQL in step with the real columns (run `data.py info`
first; match exact category spellings — `ON-PREM`, not `ONPREM`).

### Also register the recipe (for live dashboards)

`brain/reports.md` is the human-readable, gated source of truth. For a recipe
that backs a **live dashboard**, also write a machine-readable copy via the
registry helper, so the agent can regenerate it deterministically and know what
to regenerate when data changes:

```
SK="$(find ~ -ipath '*/sidekick-core/scripts' -type d 2>/dev/null | head -1)"
python3 "$SK/reports.py" save --project projects/<slug> --name <report-name> \
    --sql "SELECT …" --desc "<one line>" \
    --artifact artifacts/<report-name>.html --tables <table1>,<table2>
# later, after the HTML is synced to Drive and you resolved its file id:
python3 "$SK/reports.py" save --project projects/<slug> --name <report-name> \
    --drive-file-id <DRIVE_FILE_ID>
```

(`$CLAUDE_PLUGIN_ROOT` is unset in the shell — resolve the scripts dir by
search; see `data-discipline.md` → Locating the helper.)

This stores `projects/<slug>/.reports.json` (project root — never scanned as a
data table) with the recipe's `sql`, its dashboard path (`artifact`), the
`tables` it reads, and the synced HTML's `drive_file_id`. `reports.py list`
shows them; `reports.py run --name <n>` runs the SQL (same engine as `data.py
query`); `reports.py uses --table <t>` lists the reports a change to table `<t>`
should regenerate. `save` **merges** (re-saving with only `--drive-file-id`
keeps the SQL). Registering mirrors an already-approved brain recipe, so it
needs no separate gate. Skip the registry for one-off snapshots.

## Choosing the render kind

Ask what the user actually wants, then pick the lightest thing that does it:

- **A number / short answer** → just run `data.py query` and say it in chat.
  No artifact, no recipe (unless they'll ask again).
- **A table they want to keep/share** → a markdown table in `log/`
  (free) for reference, or an exported sheet in `output/` (confirm) if it's
  a deliverable.
- **A dashboard to explore** → the project's **standard dashboard**, built with
  `dashboard.py` into **`artifacts/`** and shown as the live Cowork artifact
  (below). Add to the existing one; don't make a new artifact unless asked.

Dashboards live in **`artifacts/`** (a synced folder, like `output/`); plain
deliverables (docs/sheets) stay in `output/`.

## The dashboard — build it with `dashboard.py` (never paste the kernel)

Every active project has **one** dashboard, "<Project> Dashboard", built from the
shared **Sidekick UI kit** (Solidbricks look: sidebar, tabbed views,
light/paper/dark, KPI & section cards, charts, sortable grids, list+detail; the
real Solidbricks logo in the footer). You do **not** hand-roll the page and you
do **not** paste the ~11 KB kernel — pasting it inline made Cowork truncate the
read (~11.4 KB) and emit a **blank page**. The bundled **`dashboard.py`** reads
`ui.css` + `ui.js` + the logo from disk and bakes the complete html. Full guide +
`window.SK` data model: **`ui-kit.md`** (read it). In short:

1. **Query** each section with `data.py query` (or `reports.py run`); collect JSON.
2. **Shape** the results into the dashboard's small data file
   `artifacts/<slug>-dashboard.sk.json` — a `window.SK` object (collections →
   views, each `kind: dashboard | grid | listdetail | home`). Bake **computed**
   rows in; the calc rule stays in the recipe, never in the page.
3. **Build:** resolve the scripts dir (`$CLAUDE_PLUGIN_ROOT` is unset) and run
   `SK="$(find ~ -ipath '*/sidekick-core/scripts' -type d 2>/dev/null | head -1)"`,
   then `python3 "$SK/dashboard.py" build --project "<ABS>/projects/<slug>" --slug <slug> --title "<Project> Dashboard"`.
   It writes `artifacts/<slug>-dashboard.html` (a branded **skeleton** if there is
   no `.sk.json` yet — that is what project scaffolding does).
4. **Show it as the live Cowork artifact** (next section) — that is the deliverable.

**One per project; edit in place.** "Add X to the dashboard" → edit the
`<slug>-dashboard.sk.json` + re-run `dashboard.py build` + re-sync. Do **not**
spin up a new artifact. Only an explicit "make a *new/separate* dashboard"
warrants a second html (different `--slug`). Labels in the **default output
language**.

## Live dashboard — the Cowork artifact is the PRIMARY deliverable

In Cowork the dashboard the user sees is a **live artifact**, not a file you hand
over with `present_files`. The `.html` in `artifacts/` (synced to Drive) is the
**backing store**; the **live artifact** is the deliverable. It is a thin wrapper
that loads the Drive html into an iframe and re-pulls on Cowork's own refresh.
So: build the html → sync → **create the live artifact**, and present *that*.

### Set it up (once per dashboard)

1. **Build** the html with `dashboard.py` (above) →
   `projects/<slug>/artifacts/<slug>-dashboard.html`.
2. **Sync to Drive.** Run `reconcile_output` (it syncs `artifacts/` as well as
   `output/`) so the file lands at `<base>/<slug>/artifacts/...` and the Drive
   client uploads it.
3. **Resolve the Drive file id** (Drive connector, search by name) and save it:
   `reports.py save --name <slug>-dashboard --drive-file-id <id>`. Stable across
   later overwrites (same file → same id) — one-time.
4. **Find the download tool name** `mcp__<uuid>__download_file_content` (`<uuid>`
   is **per-install** — read it from the session tools, never hard-code).
5. **Create the live artifact** with **`mcp__cowork__create_artifact`**, body =
   the thin wrapper below (file id + tool name filled in). **This is the primary
   output — present this, not the `.html` file.**

### The wrapper (thin — no refresh button; Cowork has its own)

```html
<!DOCTYPE html><html lang="nl"><head><meta charset="utf-8">
<style>html,body{margin:0;height:100%}iframe{border:0;width:100%;height:100vh;background:#fff}
#e{font:13px system-ui;padding:12px;color:#dc2626}</style></head><body>
<iframe id="f" sandbox="allow-same-origin allow-scripts"></iframe><div id="e" hidden></div>
<script>
const FILE_ID="{{DRIVE_FILE_ID}}";          // from reports.py (step 3)
const TOOL="{{DRIVE_DOWNLOAD_TOOL}}";        // mcp__<uuid>__download_file_content (step 4)
(async()=>{try{
  let res=await window.cowork.callMcpTool(TOOL,{fileId:FILE_ID});
  let p=res; if(typeof res==="string"){const i=res.indexOf("{");if(i>=0)p=JSON.parse(res.slice(i));}
  if(p&&p.content&&p.content[0])p=JSON.parse(p.content[0].text);
  const b64=p.base64Content??p.content??p;
  document.getElementById("f").srcdoc=typeof b64==="string"?decodeURIComponent(escape(atob(b64))):JSON.stringify(p);
}catch(e){const el=document.getElementById("e");el.hidden=false;el.textContent="Kon live-inhoud niet laden: "+e.message;}
})();
</script></body></html>
```

The real interactivity (tabs, sort, chart) lives in the **dashboard HTML** on
Drive, not the wrapper — hence `allow-scripts`. The wrapper only fetches and
frames it.

### Lifecycle — created at scaffold, self-healing if deleted

- **At project creation** the dashboard is realized as an **empty skeleton**
  (`dashboard.py build` writes the html + `.sk.json`). If **Output sync is on**,
  also sync it and **create the live artifact** right away, so a fresh project
  already shows its "<Project> Dashboard". If sync is off, the skeleton waits
  locally and the live artifact is created the first time a dashboard is shown
  (once Drive is available); until then, present a snapshot.
- **The live artifact is the user's** — they may delete it in Cowork. That's
  fine: the durable parts (`<slug>-dashboard.sk.json`, the html, the Drive file +
  its id in `.reports.json`) are untouched.
- **If a dashboard is expected and the live artifact is gone, recreate it** —
  call `mcp__cowork__create_artifact` again with the stored Drive file id (cheap,
  nothing lost). If the html/Drive file is gone too, rebuild from the `.sk.json`
  (`dashboard.py build` → `reconcile_output`) first; if even the `.sk.json` is
  gone, `dashboard.py build` makes a fresh skeleton. **Never error on a missing
  dashboard — (re)build and (re)create it.**

### Keeping it live (the trigger)

When data or a rule changes — **through the chat, so you are in the loop** — edit
the data and rebuild in the same turn, **no new artifact**:

1. Edit the dashboard's `<slug>-dashboard.sk.json` (fresh `data.py query` rows).
   (`reports.py uses --table <changed-table>` finds which dashboards a table
   change touches.)
2. Re-run `dashboard.py build`, then `reconcile_output`. The Drive file is
   overwritten **in place** (same id) — **no `mcp__cowork__create_artifact`, no
   approval.** The live artifact shows the new version on Cowork's next refresh.

So: editing a salary → update the record → edit the `.sk.json` → `dashboard.py
build` → re-sync → the live artifact reflects the new totals, untouched.

> Needs the Drive connector + Output sync on (base path). Without them: build the
> html and fall back to presenting it as a one-off snapshot file — tell the user
> it won't auto-update until Drive sync is configured.

## Gatekeepers (reused, nothing new)

- **Recipe** (save/change in `brain/reports.md`) → diff + approval. Mirroring it
  into `.reports.json` is part of the same approved change (no separate gate).
- **Dashboard** (`dashboard.py build` → overwrite in `artifacts/`) → default
  output language. The **live artifact** (`mcp__cowork__create_artifact`) is
  created once; later content refreshes go to the Drive html, not the artifact.
- **Reading** the data to build either → free (it's a `query`).

`sidekick-report` is therefore not read-only (unlike status/find), but it
introduces **no new gatekeeper** — it leans entirely on the brain and output
rules already defined.

## What stays out of this layer

- **No new `data.py` command.** Its `query`/`info` suffice; reporting added a
  reusable `query()` *function* (called by `reports.py`) but **no new
  subcommand**. Keep `data.py` under ~16 KB (Cowork truncates it on install) —
  recipe logic lives in `reports.py`, not `data.py`.
- **Rules never live in the page.** Snapshot or live, the calculation runs in
  the recipe and you bake **computed rows** into the HTML; the page only
  renders. (A local MCP server for the artifact was tried and removed — the
  sandbox blocks it; only cloud connectors are reachable.)
- **No raw JSON.** Not to fill the page, not "just to look". Always via a
  recipe / `query`.
