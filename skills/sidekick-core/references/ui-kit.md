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

The kit ships as two raw files you **paste** into the artifact you generate:

| File | What | Goes into |
|------|------|-----------|
| `assets/ui.css` | all tokens + component CSS (3 themes) | the `<style>` block |
| `assets/ui.js`  | the render kernel (shell + 4 view kinds) | a `<script>` after the data |

You never edit these. The **only** thing that changes per report is the
`window.SK` data object (built from `data.py query` results). A combined,
runnable preview lives at `plan/sidekick-ui-base.html` (open it in a browser to
see the look) — do not read that at runtime; read the two asset files.

> Two raw files, not one, because Cowork truncates any single installed plugin
> file past ~15.8 KB. The artifact you *write* (to `projects/<slug>/artifacts/`)
> has no such limit — paste both in full.

## Locating the assets

`$CLAUDE_PLUGIN_ROOT` is unset in the shell — resolve by search (same pattern
as the scripts dir):

```
UI="$(find ~ -ipath '*/sidekick-core/assets' -type d 2>/dev/null | head -1)"
# read "$UI/ui.css" and "$UI/ui.js"
```

## Assembling an artifact

```html
<!doctype html><html lang="{{LANG}}" data-theme="paper"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{{TITLE}}</title>
<style>
/* ← paste the full contents of assets/ui.css here */
</style></head>
<body data-accent="blue"><div id="root" class="app"></div>

<script>
window.SK = { /* ← your data, shaped as below (built from data.py query results) */ };
</script>

<script>
/* ← paste the full contents of assets/ui.js here */
</script>
</body></html>
```

`{{LANG}}` and all visible labels = the **default output language**.
`data-theme` ∈ `light|paper|dark` (the user can flip it live).
`data-accent` ∈ `blue|orange`.

## The `window.SK` data model

```js
window.SK = {
  workspace: "Westgate development",   // centered header title
  brand: "Sidekick", tagline: "your alter ego",   // sidebar identity (optional)
  theme: "paper", accent: "blue",
  collections: [ /* sidebar entries, in order */ ]
}
```

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

## How this fits reporting

The numbers in `SK` are **computed rows** baked in from `data.py query` /
`reports.py run` — never raw table reads, never calc in the page (the rule from
`data-discipline.md` and `reporting.md` still holds). One query → one tab/card.
Headings in the default output language. Confirm before writing the artifact to
`artifacts/<name>.html`. For a **live** dashboard, that same file is synced to
Drive and shown through the thin wrapper — see `reporting.md` → "Live
dashboard". A data change = rebuild `SK` from fresh query results, re-paste the
two assets (unchanged), overwrite the file, re-sync.

## Keep it simple

One collection with one dashboard view is a perfectly good report — you do not
need the full multi-collection shell. Add collections/tabs only when the user
has genuinely separate areas to switch between. Drop `brand`/`tagline` and the
home collection for a bare single-dashboard artifact.
