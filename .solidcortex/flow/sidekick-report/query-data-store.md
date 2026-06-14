---
domains:
  - reporting
  - structured-data
edges:
  - label: persist as a recipe
    to: sidekick-report/save-report-recipe
    via: starts
  - label: bake fresh rows
    to: sidekick-report/build-dashboard
    via: starts
flowId: sidekick-report
generatedAt: 2026-06-14T11:55:56Z
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generator: solidcortex@0.17.0
kind: derived
mainCodeFile: skills/sidekick-core/scripts/data.py
nodeId: query-data-store
parent: main/sidekick-report
related:
  - structured-data/query-data
  - structured-data/info-discover
  - sidekick-find/probe-data-tables
  - sidekick-status/read-data-tables
slug: query-data-store
status: current
summary: Sources every report number through data.py info/query (read-only SELECTs against the project's JSON-table store) — the single-access-path rule, never a raw JSON read; returns the JSON the recipe and dashboard consume.
systems:
  - python-helpers
type: process
---

## TLDR (agent)
**Purpose:** Source every report number through `data.py info`/`query` — read-only SELECTs over the project's JSON-table store — and return the JSON the recipe and dashboard consume.
**Inputs:** A render decision from report-entry; a project with a `data/` store; a `SELECT`/`WITH` SQL (or `info` for shape); category spellings must match exactly (`ON-PREM`, not `ONPREM`).
**Outputs:** `{ok, action:"query", rowcount, rows:[…]}` JSON (or an `info` table/column/values report); a `ValueError` on non-SELECT SQL or a bad column/table (enriched with the real schema).
**Code anchor:** [skills/sidekick-core/scripts/data.py](../../../skills/sidekick-core/scripts/data.py)
**Edges:** → sidekick-report/save-report-recipe (starts — persist as a recipe), → sidekick-report/build-dashboard (starts — bake fresh rows)
**Key rules:**
- All report data comes from `data.py query`/`info` — never a raw `data/*.json` read, `sqlite3` CLI, or ad-hoc `python`.
- `query` runs SELECT/WITH only; insert/update/delete are refused (it's read-only).
- Queries run over a throwaway in-memory SQLite built from the JSON; the on-disk store is never touched.
- Run `info` first to learn tables, columns, and exact category values before writing the SELECT.

## Functional (user facing)

### Why use this?
Every figure in a report has to come from somewhere trustworthy. This step is
that single, reliable door to your data: it reads the store, runs the question
you asked as a query, and hands back the rows — already filtered and shaped — so
the report shows real, current numbers and never a stale guess.

### What it does
- Reads the project's structured store and answers a question against it as a
  read-only query — it can summarize, group, sort, and filter, but it cannot
  change anything.
- Can first describe the store's shape: which tables exist, what columns each
  has, and (for short value lists) the exact spellings of category values, so a
  filter matches reality instead of a typo.
- Returns the result as plain rows the rest of the flow turns into a saved
  recipe and a rendered dashboard.

### When the query is wrong
If a query names a column or table that does not exist, it does not fail
silently — it comes back with the real tables and columns available, so the next
attempt can be corrected in one go rather than a round of guessing.

### Behind the scenes
The data is held as ordinary files, but the question is answered by loading a
fresh, temporary copy into an in-memory database, running the query there, and
throwing that copy away. Your stored files are only ever read, never modified by
this step. This keeps a single, auditable path to the data: every report,
snapshot or live, is fed the same way.

### Pro tips
- Ask for the shape first when you are unsure of a column name or a category's
  exact spelling — it saves a failed query.
- Category filters are case- and spelling-exact: `ON-PREM` is not `ONPREM`.
- A query that only needs one number does not need a recipe or an artifact — the
  answer can go straight into chat.

### Related
- [sidekick-report/report-entry](report-entry.md) — the step that decides a query
  is needed.
- [sidekick-report/save-report-recipe](save-report-recipe.md) — persists a
  recurring query as a recipe.
- [sidekick-report/build-dashboard](build-dashboard.md) — bakes the fresh rows
  into the dashboard.

## Technical

`skills/sidekick-core/scripts/data.py` is the structured-data helper. Two
read-only subcommands serve reporting:

- **`query(project, sql)`** (`def query`, ~L264) — strips a trailing `;`, rejects
  anything not starting with `select`/`with` (raising `ValueError`), then builds a
  `:memory:` SQLite from each `data/*.json` table (columns from `_schema.json` or
  inferred), runs the SELECT with `row_factory = sqlite3.Row`, and returns
  `{ok, action:"query", rowcount, rows}`. On a `sqlite3.Error` containing
  "no such", it appends `| available: <table(col, …)>` so the caller self-corrects.
  The on-disk JSON is never written.
- **`info`** (`cmd_info`, ~L333) — lists tables with columns and, for
  low-cardinality columns (≤ `_ENUM_MAX` = 12 distinct), the exact `values` for
  spelling-safe `WHERE` matches. Returns `exists:false` with no tables when the
  store is absent.

Key data structures: one JSON array of objects per table under `<project>/data/`,
plus `_schema.json` (column names + types). `query()` is also the engine
`reports.py` and `dashboard.py` call (recipe `run`, binding resolution) — one
access path for CLI, recipes, and dashboard bindings alike.

Helper resolution: `$CLAUDE_PLUGIN_ROOT` is unset in the shell, so the skill finds
the scripts dir with
`find ~ -ipath '*/sidekick-core/scripts' -type d`. Budget: `data.py` is kept under
~15 KB (Cowork truncates plugin files on install ~15.8 KB), which is why
recipe-registry logic lives in `reports.py`, not here.

Dependencies: upstream `sidekick-report/report-entry` (decides a query is needed);
downstream `sidekick-report/save-report-recipe` (persists the query) and
`sidekick-report/build-dashboard` (bakes the rows). Protocol:
`skills/sidekick-core/references/reporting.md` ("the one rule"), data rules in
`data-discipline.md`.
