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

`brain/reports.md` is the human-readable, gated source of truth. For a live
dashboard, also register the machine-readable copy via the **`save_report` MCP
tool** (native — the bash `reports.py save` truncates on the mount).

An entry is **one of two kinds** (don't cram a whole dashboard into one `sql`): a
**query recipe** (a single named `SELECT`, reusable/bindable) or a **dashboard
registration** (`artifact` + `drive_file_id` + `tables`, no sql). A brain report
with several sub-queries → **one recipe per sub-query**:

```
save_report { project, name: "revenue-by-line", sql: "SELECT …", tables: ["deals"] }
save_report { project, name: "<slug>-dashboard",            # no sql; merges, set id later
              artifact: "artifacts/<slug>-dashboard.html", drive_file_id: "<id>", tables: ["deals"] }
```

A new entry needs **at least** `sql` **or** `artifact`/`drive_file_id`;
`save_report` **merges** + validates the name. Stored in `.sidekick/reports.json`
(never scanned as a table). The dashboard's *rendering* queries already live
inline in the `.sk.json` **bindings** — the registry is for **named reuse** + the
**`drive_file_id`** the wrapper needs. Mirrors an approved brain recipe — no
separate gate; skip for one-off snapshots.

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
2. **Shape** the dashboard's small data file `<slug>-dashboard.sk.json` — in the
   project's local **`dashboard/`** subfolder (not the project root, and not
   `artifacts/`, which is Drive-synced and may serve cloud-only placeholders). A
   `window.SK` object (collections → views, each `kind: dashboard | grid |
   listdetail | home`). **Store the QUERY, not the numbers:** give each KPI /
   chart / table / grid / panel a `query` (a read-only `SELECT`) or `recipe`
   (a `.sidekick/reports.json` name) and alias its columns to the field names the element
   renders (see `ui-kit.md` → "Bind to live data"). The SQL does the calc **and**
   the formatting; the page only renders. This makes the dashboard a live view —
   no hardcoded values to desync, one source of truth.
3. **Build via the `build_dashboard` MCP tool** (the `sidekick-sync` server):
   `{project: "<ABS>/projects/<slug>", slug: "<slug>", title: "<Project> Dashboard"}`.
   It runs **natively** (reliable FS): resolves the `query`/`recipe` bindings
   against the live data store and bakes the FRESH rows into
   `artifacts/<slug>-dashboard.html` (a branded **skeleton** if there is no
   `.sk.json` yet). It returns `changed` (did the html move). **Omit `slug` to
   rebuild every dashboard in the project** — do that after a data change. A bad
   binding errors loudly (no silent stale). **Do not** lean on the bash
   `dashboard.py` — the sandbox mount truncates it; it's a fallback only.
4. **Show it as the live Cowork artifact** (next section) — that is the deliverable.

**One per project; edit in place.** "Add X to the dashboard" → edit the
`<slug>-dashboard.sk.json` + re-run `build_dashboard` + re-sync. Do **not**
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
#e{font:13px system-ui;padding:12px;color:#dc2626;white-space:pre-wrap}</style></head><body>
<iframe id="f" sandbox="allow-same-origin allow-scripts"></iframe><div id="e" hidden></div>
<script>
const FILE_ID="{{DRIVE_FILE_ID}}";          // from reports.py (step 3)
const TOOL="{{DRIVE_DOWNLOAD_TOOL}}";        // mcp__<uuid>__download_file_content (step 4)
// Drive tools differ in shape; unwrap() peels them ALL to a base64 string:
//   "<json>" | {content:"<b64>"} | {content:[{text}]} | {base64Content:"<b64>"} | "<b64>"
function unwrap(x){
  if(x==null) return "";
  if(typeof x==="string"){ const s=x.trim();
    if(s[0]==="{"||s[0]==="["){ try{ return unwrap(JSON.parse(s)); }catch(e){ return s; } }
    return s; }                                  // already base64
  if(Array.isArray(x)) return unwrap(x[0]);
  return unwrap(x.base64Content ?? x.content ?? x.text ?? x.data ?? "");
}
(async()=>{try{
  const res=await window.cowork.callMcpTool(TOOL,{fileId:FILE_ID});
  const b64=unwrap(res);
  if(!b64) throw new Error("empty response from "+TOOL);
  document.getElementById("f").srcdoc=decodeURIComponent(escape(atob(b64)));
}catch(e){const el=document.getElementById("e");el.hidden=false;el.textContent="Kon live-inhoud niet laden: "+e.message;}
})();
</script></body></html>
```

The real interactivity (tabs, sort, chart) lives in the **dashboard HTML** on
Drive, not the wrapper — hence `allow-scripts`. The wrapper only fetches and
frames it.

### Lifecycle — created at scaffold, self-healing if deleted

- **At project creation** the dashboard is realized as an **empty skeleton**
  (`build_dashboard` writes the html + `.sk.json`). If **Output sync is on**,
  also sync it and **create the live artifact** right away, so a fresh project
  already shows its "<Project> Dashboard". If sync is off, the skeleton waits
  locally and the live artifact is created the first time a dashboard is shown
  (once Drive is available); until then, present a snapshot.
- **The live artifact is the user's** — they may delete it in Cowork. That's
  fine: the durable parts (`<slug>-dashboard.sk.json`, the html, the Drive file +
  its id in `.sidekick/reports.json`) are untouched.
- **If a dashboard is expected and the live artifact is gone, recreate it** —
  call `mcp__cowork__create_artifact` again with the stored Drive file id (cheap,
  nothing lost). If the html/Drive file is gone too, rebuild from the `.sk.json`
  (`build_dashboard` → `reconcile_output`) first; if even the `.sk.json` is
  gone, `build_dashboard` makes a fresh skeleton. **Never error on a missing
  dashboard — (re)build and (re)create it.**

### Keeping it live (the trigger) — PROACTIVE, same turn

The `.sk.json` stores **queries, not numbers**, so a data change needs **no
editing** — just rebuild. **After any `data.py insert/update/delete` in a project
with a dashboard, in the same turn:**

1. Call **`build_dashboard` with `project` only (no `slug`)** — rebuilds **every**
   dashboard, re-running each binding against the new data (check the returned
   `any_changed`).
2. Call `reconcile_output` — the Drive file(s) are overwritten **in place** (same
   id), **no `mcp__cowork__create_artifact`, no approval**; the live artifact
   updates on Cowork's next refresh.

So: edit a salary → `data.py update` → `build_dashboard {project}` →
`reconcile_output` → every dashboard reflects the new totals. Don't wait for the
user to notice it's stale — refresh as part of the write.

> Needs the Drive connector + Output sync on (base path). Without them: build the
> html and fall back to presenting it as a one-off snapshot file — tell the user
> it won't auto-update until Drive sync is configured.

## Gatekeepers (reused, nothing new)

- **Recipe** (save/change in `brain/reports.md`) → diff + approval. Mirroring it
  into `.sidekick/reports.json` (via `save_report`) is part of the same approved change
  (no separate gate).
- **Dashboard** (`build_dashboard` → overwrite in `artifacts/`) → default
  output language. The **live artifact** (`mcp__cowork__create_artifact`) is
  created once; later content refreshes go to the Drive html, not the artifact.
- **Reading** the data to build either → free (it's a `query`).

**Combining the two prompts is allowed.** When the recipe and dashboard are
created in the **same turn**, fold the brain-approval and output-confirm into
**one** decision: *show the `brain/reports.md` diff*, then a single "approve &
build" `AskUserQuestion`. Showing the diff is non-negotiable; the click can be
combined. Keep them separate only if the recipe changes without a (re)build, or
vice versa.

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
