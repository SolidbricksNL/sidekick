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

"Live" here means **interactive over a snapshot**: tabs, sorting, filtering,
and charts run in the page, but the numbers are as of generation time.
**Refresh = re-run the report** (re-query, rewrite the artifact). Say so to
the user — the dashboard is a snapshot, not a live feed.

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

## Choosing the render kind

Ask what the user actually wants, then pick the lightest thing that does it:

- **A number / short answer** → just run `data.py query` and say it in chat.
  No artifact, no recipe (unless they'll ask again).
- **A table they want to keep/share** → a markdown table in `log/`
  (free) for reference, or an exported sheet in `output/` (confirm) if it's
  a deliverable.
- **A dashboard to explore** → a self-contained tabbed `.html` in `output/`
  (confirm). This is the "live artifact" case below.

## The dashboard artifact (self-contained HTML)

One `.html` file. The data is **embedded** (a `<script type="application/json">`
block per tab), rendering is **inline** (vanilla JS), and it makes **no
network requests** — Cowork's artifact sandbox blocks outbound `fetch`, and a
self-contained file also opens straight from `output/` in any browser.

Build it like this:

1. **Query each tab** with `data.py query` and collect the JSON results.
2. **Embed** each result as a JSON `<script>` block (do not fetch it).
3. **One tab per query.** Render each as a sortable table; add a simple
   inline-SVG bar chart when a tab is one label column + one numeric column.
4. **Confirm before writing** to `output/` (it's a deliverable), generate
   labels/headings in the **default output language**, then write the file.
5. Tell the user it's a snapshot and how to refresh (re-run the report).

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

## Gatekeepers (reused, nothing new)

- **Recipe** (save/change in `brain/reports.md`) → diff + approval.
- **Artifact** (create/overwrite in `output/`) → confirm, default output
  language.
- **Reading** the data to build either → free (it's a `query`).

`sidekick-report` is therefore not read-only (unlike status/find), but it
introduces **no new gatekeeper** — it leans entirely on the brain and output
rules already defined.

## What stays out of this layer

- **No new `data.py` command.** Reporting needs only `query`/`info`, which
  exist. Don't grow the helper (Cowork truncates it past ~16 KB).
- **No live data binding.** The artifact never reads `data/` at runtime; it
  carries a snapshot. (A React/Cowork-artifact render that binds to live data
  was deferred — it depends on the still-new live-artifact runtime.)
- **No raw JSON.** Not to fill the page, not "just to look". Always `query`.
