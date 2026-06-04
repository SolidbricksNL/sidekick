# The Sidekick UI kit (design + navigation base for artifacts)

Every dashboard/list/grid artifact Sidekick produces starts from **one shared
design system** — the Solidbricks/Visma look: a collapsible **sidebar**, a
centered **workspace title**, **tabbed views**, a light/paper/dark **theme
toggle**, and a small widget set (KPI cards, section cards, bar/horizontal-bar
charts, sortable tables, status pills, list+detail). It is brand-consistent
(orange `#F47800` + blue `#1493E8`, Ubuntu/Open Sans/JetBrains type stacks),
**self-contained, and makes no network calls** — so it works as a snapshot
*and* as the body the live Drive-wrapper loads. The user can restyle freely;
this is the starting point, not a cage.

**Never hand-assemble the page and never paste the kernel — a build script does
it.** The kit ships as:

| File | What |
|------|------|
| `assets/ui.css` | tokens + component CSS (3 themes) |
| `assets/ui.js`  | the render kernel (shell + 4 view kinds) |
| `assets/solidbricks.png` | the real Solidbricks maker logo (footer) |
| `scripts/dashboard.py` | **builds the dashboard html** from a small data file |

> **Why a script, not paste.** The kernel is ~11 KB of dense JS. When the agent
> read it inline to paste, Cowork **truncated the read at ~11.4 KB** and produced
> a blank page. `dashboard.py` reads the assets from disk **natively** (full, no
> context limit) and bakes the complete page — so you never read or paste the
> kernel, and the real logo is embedded for you. A combined runnable preview
> lives at `plan/sidekick-ui-base.html` (open in a browser to see the look) — do
> not read it at runtime.

## One dashboard per project — edit the data, rebuild

Each active project has **one** dashboard, named "<Project> Dashboard". Its
source of truth is a tiny JSON file you edit — never the big html:

```
projects/<slug>/dashboard/<slug>-dashboard.sk.json  <- the window.SK data (you edit this)
                                                       in the local dashboard/ subfolder
                                                       (reliable read — NOT the project
                                                       root, NOT the Drive-synced artifacts/)
projects/<slug>/artifacts/<slug>-dashboard.html     <- built output (synced to Drive)
```

**Build via the `build_dashboard` MCP tool (primary).** Call the
`sidekick-sync` server's **`build_dashboard`** tool — `{project: "<ABSOLUTE>/projects/<slug>",
slug: "<slug>", title: "<Project> Dashboard"}`. It runs **natively** (real
filesystem), so it reads the full UI-kit chunks + logo and bakes the html
reliably — **the bash `dashboard.py` is truncated by the sandbox mount** (it came
back 98/161 lines → `SyntaxError`), so don't depend on it. The tool reads the
project's `<slug>-dashboard.sk.json` (local `dashboard/` subfolder) and writes
`artifacts/<slug>-dashboard.html`.

- First call with no `.sk.json` writes an **empty skeleton** (branded shell + one
  placeholder collection) and builds the html — project scaffolding does this.
- To **add or change content**: edit `<slug>-dashboard.sk.json` (the `window.SK`
  shape below — values from `data.py query`, computed rows baked in), then call
  `build_dashboard` again + `reconcile_output`. Regenerated in place; the live
  artifact updates — **no new artifact**.
- A **new, separate** dashboard only when the user explicitly asks. Otherwise
  everything lands in the project's standard dashboard.

All labels = the **default output language**. `theme` ∈ light|paper|dark,
`accent` ∈ blue|orange — set them inside the `.sk.json`.

**Fallback (only if the MCP tool is unavailable):** the bash CLI
`SK="$(find ~ -ipath '*/sidekick-core/scripts' -type d 2>/dev/null | head -1)"`,
`python3 "$SK/dashboard.py" build --project "<ABS>/projects/<slug>" --slug <slug> --title "…"`.
If it errors with a `SyntaxError`/truncation, the mount truncated the script —
use the MCP tool instead (or Read `dashboard.py` to hydrate it, then retry).

> **Cowork environment gotchas — use the MCP tool, don't improvise.**
> - The sandbox **`.remote-plugins` mount truncates bash reads/exec** of plugin
>   files (lazy/partial hydration — even `dashboard.py` came back short). The
>   **native MCP server is the reliable path** (it reads real files). The Read
>   tool also gets full content; bash does not.
> - **`artifacts/` is Drive-synced** → files there can be **cloud-only
>   placeholders** (`stat()` ok, `open()` fails until hydrated). So the editable
>   **`.sk.json` lives in the local `dashboard/` subfolder** (reliable) and you **never read
>   the built html back** — `build_dashboard` only writes it; the wrapper loads it
>   from Drive; `reconcile_output` hydrates + pushes.
> - **Don't create project files from bash** — `touch`, `python3 open(…,'w')`,
>   and heredocs into the project mount **fail inconsistently** (the same mount
>   that truncates reads). **Use the Write tool** for the `.sk.json` (now small —
>   it holds queries, not data — so Write rarely truncates) and **native MCP
>   tools** for state files: `.reports.json` via **`save_report`**, the html via
>   **`build_dashboard`**. Never hand-write `.reports.json` from bash.
> - **Registry + build go through the `sidekick-sync` MCP tools, not bash.** The
>   bash `reports.py`/`dashboard.py` truncate on the mount (`SyntaxError`); they
>   are fallbacks only. `build_dashboard` + `save_report` run natively.
> - The builder self-verifies the assembled kernel and **errors instead of baking
>   a blank page** if anything read short.

## The `window.SK` data model

```js
window.SK = {
  workspace: "Westgate development",   // centered HEADER title — the project/workspace
  theme: "paper", accent: "blue",
  collections: [ /* sidebar entries, in order */ ]
}
```

Three identities, don't mix them up: the **sidebar top** is always **"Sidekick /
your alter ego"** (the product — fixed in the kit, not settable); the **header**
shows `SK.workspace` (the project, e.g. "Consulting Seasonality"); the **footer**
shows the **Solidbricks** maker mark + "by Solidbricks" (fixed). So put the
project name in `workspace` — never "Solidbricks" anywhere but the footer.

A **collection** is one sidebar entry. `section:"top"` pins it above the
"Collections" divider; anything else falls below it.

```js
{ id:"finance", label:"Finance", icon:"euro", section:"collections",
  count: 42,            // optional badge
  views: [ /* tabs */ ] }      // OR  home:true  OR  empty:true
```

- `home:true` → renders a **home** view from the collection's own
  `greeting`, `intro`, `kpis`, `panels` (no tabs).
- `empty:true` → renders the "set up this collection" placeholder.
- otherwise `views:[…]` → one **tab** per view; `kind` picks the layout.

`icon` ∈ `home euro users check book calendar grid list layout search building
trend mail sparkle` (anything else falls back to a generic layout glyph).

### View kinds

**`dashboard`** — KPI strip + cards (each card holds a chart *or* a table):

```js
{ id:"overview", label:"Overview", kind:"dashboard",
  title:"Finance overview", subtitle:"Cost plan, spend and forecast.",
  kpis:[ {label:"Committed", value:"€ 22.9M", delta:"95%", sub:"of budget", tone:"pos"} ],
  cards:[
    { title:"Spend by month", action:"Open ledger",
      chart:{ type:"bar", unit:"M", data:[ {label:"Jan",value:2.1}, {label:"Feb",value:3.4} ] } },
    { title:"Cost by category",
      chart:{ type:"hbars", data:[ {label:"Structure",value:8.2,color:"var(--blue)"} ] } },
    { title:"Latest entries", wide:true,     // wide → full-width row
      table:{ cols:[ {key:"ref",label:"Ref"}, {key:"amount",label:"Amount",num:true} ],
              rows:[ {ref:"INV-204", amount:"€ 412,000"} ] } } ] }
```

`tone` ∈ `pos|neg|warn` (else neutral). `num:true` right-aligns + monospaces a
column. A card is either `chart` **or** `table`.

**`grid`** — a spreadsheet-style sortable table (sticky header, optional totals):

```js
{ id:"ledger", label:"Ledger", kind:"grid", title:"Ledger",
  columns:[ {key:"date",label:"Date"}, {key:"debit",label:"Debit",num:true} ],
  rows:[ {date:"2026-05-04", debit:"€ 220,000"} ],
  totals:{ debit:"€ 915,900" } }     // optional; first empty cell shows "Totals"
```

Click a header to sort (numeric-aware: it strips `€ ,` to compare numbers).

**`listdetail`** — master list on the left, full record on the right:

```js
{ id:"people", label:"People", kind:"listdetail",
  items:[
    { id:"mj", title:"Marije Jansen", subtitle:"Managing Director", status:"Active",
      initials:"MJ", color:"#1493E8",          // initials+color → avatar; omit for a plain row
      fields:[ {label:"Discipline", value:"Management"}, {label:"Since", value:"2019-03", mono:true} ],
      blocks:[ {label:"Note", text:"Owns the Westgate P&L."} ],
      tags:["Strategy","P&L"] } ] }
```

`status` renders a colored pill — known values: `Active / On site / Done /
Decided` (green), `In progress` (blue), `Open / At risk / Revisit` (amber);
anything else is neutral.

**`home`** — set on the **collection** (not a view):

```js
{ id:"home", label:"Home", icon:"home", section:"top", home:true,
  greeting:"Good morning.", intro:"Here is where things stand.",
  kpis:[ … ],                          // same KPI shape as dashboard
  panels:[ { title:"What your sidekick noticed",
             items:[ {primary:"Steel invoice", secondary:"is 6% over rate.", meta:"Watch · finance"} ] } ] }
```

## Bind to live data — store the query, NOT the numbers

A `.sk.json` should hold **layout + bindings**, not hardcoded values. Give a
KPI / card chart / card table / grid / list / panel a **`query`** (a read-only
`SELECT`) or **`recipe`** (a name in `.reports.json`) and `build_dashboard`
runs it **natively at build time** and bakes the **fresh** rows in. So the
dashboard is a live view of the data store — after a `data.py` write you just
**rebuild**, never hand-edit numbers (no desync, one source of truth = the query).

**Alias your SELECT columns to the field names the element renders:**

| Element | Binding | Result shape (column aliases) |
|---|---|---|
| KPI | `query`/`recipe` | one row → its columns merge into the KPI (`value`, `delta`, `sub`, `tone`) |
| card `chart` | `chart.query` | rows → `chart.data`; alias `label`, `value`(, `color`) |
| card `table` | `table.query` | rows → `table.rows`; alias the declared `cols[].key` |
| `grid` view | `query` (+ `totals_query`) | rows → `rows`; `totals_query`'s first row → `totals` |
| `listdetail` | `query` | rows → `items` (alias item fields) |
| home `panel` | `panel.query` | rows → `items` (alias `primary`/`secondary`/`meta`) |

```js
// KPI: SQL computes AND formats; the page only renders.
{ label:"Committed", query:"SELECT '€ '||printf('%.1fM', SUM(amount)/1e6) AS value, '95%' AS delta FROM deals" }
// grid bound to a query, with a totals row:
{ id:"ledger", kind:"grid", title:"Ledger",
  columns:[{key:"date",label:"Date"},{key:"debit",label:"Debit",num:true}],
  query:"SELECT date, debit FROM ledger ORDER BY date",
  totals_query:"SELECT '€ '||SUM(debit) AS debit FROM ledger" }
```

The SQL does the calc **and** the display formatting (the rule "calc in the
recipe, never in the page" still holds). A binding that fails (bad SQL, missing
table) makes the build **error loudly** — never a silently stale page. Elements
with no binding keep their literal values, so older hand-authored dashboards
still build.

**Two binding-SQL gotchas:**
- **`primary` is a reserved SQL word** — a bare `… AS primary` is a syntax
  error. **Backtick-quote** any alias that collides with a keyword:
  `SELECT label AS \`primary\`, note AS secondary FROM …`. (`secondary`, `meta`,
  `value`, `label` are fine unquoted; only quote the reserved ones.)
- **Unicode is safe end-to-end.** `€`, `·`, accents etc. survive in SQL strings,
  the `.sk.json`, and the baked html (everything is UTF-8; the MCP wire is
  ASCII-escaped and restored). Use real symbols — no need to fall back to `EUR`
  or `-`.

## How this fits reporting

The numbers in `SK` come from `data.py query` / `reports.py run` (via bindings,
above) — never raw table reads, never calc in the page (the rule from
`data-discipline.md` and `reporting.md` still holds). One query → one card/tab.
Labels in the default output language. **A data change = re-run `build_dashboard`
(it re-runs the bindings) + re-sync** — no editing values. The **live Cowork
artifact** is the primary deliverable; see `reporting.md` → "Live dashboard".
You never re-paste the kernel — the builder owns it.

## Keep it simple

One collection with one `home` or `dashboard` view is a perfectly good report —
you don't need the full multi-collection shell. Add collections/tabs only when
the project has genuinely separate areas. The sidebar identity, footer logo, and
kernel are fixed by the builder; you only shape `collections`.
