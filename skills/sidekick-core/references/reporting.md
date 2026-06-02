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
- **A dashboard to explore** → a self-contained tabbed `.html` in the
  project's **`artifacts/`** folder (confirm). This is the dashboard the live
  wrapper loads from Drive (below).

Dashboards live in **`artifacts/`** (a synced folder, like `output/`); plain
deliverables (docs/sheets) stay in `output/`.

## The dashboard HTML (self-contained)

One `.html` file. The data is **embedded** (a `<script type="application/json">`
block per tab), rendering is **inline** (vanilla JS), and it makes **no
network requests** — Cowork's artifact sandbox blocks outbound `fetch`. The same
file works both as a standalone snapshot and as the body the live wrapper loads.

Build it like this:

1. **Query each tab** with `data.py query` (or `reports.py run`) and collect the
   JSON results.
2. **Embed** each result as a JSON `<script>` block (do not fetch it).
3. **One tab per query.** Render each as a sortable table; add a simple
   inline-SVG bar chart when a tab is one label column + one numeric column.
4. **Confirm before writing** to `artifacts/<name>.html`, generate
   labels/headings in the **default output language**, then write the file.
5. For a **live** dashboard, continue with "Live dashboard" below; otherwise
   tell the user it's a snapshot and that re-running regenerates it.

### Skeleton to adapt

Keep it self-contained; swap in the real tabs and embedded data. No external
CSS/JS, no `fetch`.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Monthly revenue</title>
<style>
  body{font:14px system-ui,sans-serif;margin:0;color:#1a1a1a}
  header{padding:16px 20px;border-bottom:1px solid #e5e5e5}
  .tabs{display:flex;gap:4px;padding:0 20px;border-bottom:1px solid #e5e5e5}
  .tabs button{border:0;background:none;padding:10px 14px;cursor:pointer;font:inherit;border-bottom:2px solid transparent}
  .tabs button.active{border-bottom-color:#1a1a1a;font-weight:600}
  .panel{padding:20px;display:none}.panel.active{display:block}
  table{border-collapse:collapse;width:100%}
  th,td{text-align:left;padding:6px 10px;border-bottom:1px solid #eee}
  th{cursor:pointer;user-select:none}th:hover{background:#f6f6f6}
  .bar{height:14px;background:#3b6;border-radius:2px}
  .muted{color:#888;font-size:12px}
</style>
</head>
<body>
<header><h2 style="margin:0">Monthly revenue</h2>
  <div class="muted">Snapshot generated by Sidekick — re-run the report to refresh.</div>
</header>
<nav class="tabs" id="tabs"></nav>
<main id="panels"></main>

<!-- one data block per tab; fill from data.py query results -->
<script type="application/json" id="by_line">
[{"line":"Cloud","revenue":820000},{"line":"On-prem","revenue":410000}]
</script>
<script type="application/json" id="by_month">
[{"month":"2026-01","revenue":98000},{"month":"2026-02","revenue":104000}]
</script>

<script>
// declare the tabs: id matches a <script> block above
const TABS = [
  {id:"by_line",  label:"By line",  chart:{label:"line",  value:"revenue"}},
  {id:"by_month", label:"By month", chart:null},
];
const data = id => JSON.parse(document.getElementById(id).textContent);

function table(rows, chart){
  if(!rows.length) return "<p class='muted'>No rows.</p>";
  const cols = Object.keys(rows[0]);
  const max = chart ? Math.max(...rows.map(r=>+r[chart.value]||0)) : 0;
  const head = cols.map(c=>`<th data-c="${c}">${c}</th>`).join("")+(chart?"<th></th>":"");
  const body = rows.map(r=>{
    const tds = cols.map(c=>`<td>${r[c]}</td>`).join("");
    const bar = chart?`<td style="width:30%"><div class="bar" style="width:${max?(+r[chart.value]/max*100):0}%"></div></td>`:"";
    return `<tr>${tds}${bar}</tr>`;
  }).join("");
  return `<table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
}

const panels = document.getElementById("panels"), tabsEl = document.getElementById("tabs");
TABS.forEach((t,i)=>{
  const b=document.createElement("button");b.textContent=t.label;
  b.onclick=()=>{document.querySelectorAll(".tabs button,.panel").forEach(e=>e.classList.remove("active"));
    b.classList.add("active");document.getElementById("p_"+t.id).classList.add("active");};
  if(i===0)b.classList.add("active");tabsEl.appendChild(b);
  const p=document.createElement("section");p.className="panel"+(i===0?" active":"");p.id="p_"+t.id;
  p.innerHTML=table(data(t.id),t.chart);panels.appendChild(p);
  // click a header to sort that column
  p.querySelectorAll("th[data-c]").forEach(th=>th.onclick=()=>{
    const c=th.dataset.c, rows=data(t.id).slice();
    const num=rows.every(r=>r[c]===""||!isNaN(+r[c]));
    rows.sort((a,b)=>num?(+b[c]-+a[c]):String(a[c]).localeCompare(String(b[c])));
    p.innerHTML=table(rows,t.chart);
  });
});
</script>
</body>
</html>
```

Adapt freely: more tabs, different columns, a different chart, the user's
output language for headings. Keep it **one file, no network, data embedded**.

## Live dashboard (Drive-wrapped)

The dashboard HTML is **dumb** — fully generated by you (data baked in). To make
it *live* (updates without re-emitting an artifact each time), you sync it to
Drive and show it through a **thin wrapper artifact** that loads the Drive HTML
into an iframe.

### One-time setup (per dashboard)

1. **Generate** the self-contained dashboard HTML (above) → write
   `projects/<slug>/artifacts/<name>.html`.
2. **Sync to Drive.** Run `reconcile_output` (it now syncs `artifacts/` as well
   as `output/`) so the file lands at `<base>/<slug>/artifacts/<name>.html` and
   the Drive client uploads it.
3. **Resolve the Drive file id.** Find the synced file via the Drive connector
   (search/list by name) and save it:
   `reports.py save --name <name> --drive-file-id <id>`. The id is **stable**
   across later content overwrites (same file → same id), so this is one-time.
4. **Find the Drive download tool name.** It is `mcp__<uuid>__download_file_content`
   where `<uuid>` is **per-install** — read it from the session's available
   tools; do not hard-code.
5. **Emit the wrapper once** as the Cowork artifact (one `update_artifact`
   approval), filling in the two values from steps 3–4.

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

### Keeping it live (the trigger)

When data or a rule changes — which happens **through the chat, so you are in
the loop** — **regenerate the dashboard HTML and re-sync**, in the same turn:

1. Find affected dashboards: `reports.py uses --table <changed-table>`.
2. For each, re-run its recipe, rebuild `artifacts/<name>.html`, run
   `reconcile_output`. The Drive file is overwritten **in place** (same id) —
   **no `update_artifact`, no approval.** The wrapper shows the new version on
   Cowork's next refresh.

So: editing a salary → update the record → regenerate the salary dashboard HTML
→ re-sync → the live wrapper reflects the new totals, untouched.

> Requires the Drive connector enabled (the wrapper reads it) and Output sync on
> with a base path (the HTML reaches Drive). With neither, fall back to a plain
> snapshot dashboard in `artifacts/` and tell the user it won't auto-update.

## Gatekeepers (reused, nothing new)

- **Recipe** (save/change in `brain/reports.md`) → diff + approval. Mirroring it
  into `.reports.json` is part of the same approved change (no separate gate).
- **Dashboard HTML** (create/overwrite in `artifacts/`) → confirm, default
  output language. The **wrapper** artifact is emitted once (one approval);
  later content refreshes go to the Drive HTML, not the artifact.
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
