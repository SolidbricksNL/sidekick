---
domains:
  - reporting
  - write-disciplines
flowId: sidekick-report
generatedAt: 2026-06-14T11:55:56Z
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generator: solidcortex@0.17.0
kind: derived
mainCodeFile: skills/sidekick-core/scripts/reports.py
nodeId: save-report-recipe
parent: main/sidekick-report
related:
  - sidekick-sync/save-report
slug: save-report-recipe
status: current
summary: Saves a recurring ask as a reusable recipe — a named, plain-language report plus its exact SELECT(s) — into brain/reports.md (a brain write, diff + approval) and mirrors the machine copy into .sidekick/reports.json via the save_report tool / reports.py.
systems:
  - python-helpers
type: process
---

## TLDR (agent)
**Purpose:** Persist a recurring report as a reusable recipe — a named, plain-language entry plus its exact SELECT(s) in `brain/reports.md` — and mirror the machine copy into `.sidekick/reports.json`.
**Inputs:** A query (from query-data-store) the user will want again; a recipe name (slug-ish), purpose, render kind, and the SELECT(s); optional `artifact`/`drive_file_id`/`tables` for a dashboard registration.
**Outputs:** A `brain/reports.md` section (gated, human-readable) + a merged/validated entry in `.sidekick/reports.json` via the `save_report` MCP tool / `reports.py save`.
**Code anchor:** [skills/sidekick-core/scripts/reports.py](../../../skills/sidekick-core/scripts/reports.py)
**Edges:** (none)
**Key rules:**
- Saving/changing a `brain/reports.md` recipe is a brain write — show the diff, get approval before writing.
- One registry entry is EITHER a query recipe (one named SELECT) OR a dashboard registration (artifact+drive_file_id+tables, no sql) — never both crammed.
- A multi-sub-query report = one recipe entry per sub-query, not one entry with a "representative" sql.
- Mirroring into `.sidekick/reports.json` rides the approved brain change (no separate gate); use the native tool, never hand-write the JSON.

## Functional (user facing)

### Why use this?
When you ask for the same view a second time — "give me the monthly revenue
breakdown again" — you should not have to re-explain it. Saving it as a recipe
captures the question once, in plain language plus the exact query, so next time
"run the monthly one" just works. The recipe is the reusable piece; it lives
with the project's durable knowledge.

### What it does
- Records a report by name, with a short plain-language description of what it
  shows and the exact query (or queries) it runs.
- Stores it in the project's brain, where lasting project knowledge belongs, so
  any later session can re-run it without re-inspecting the data.
- Keeps a second, machine-readable copy used by dashboards and the live view, so
  a saved report can be referred to by name elsewhere.
- Handles reports with several parts (by line, by month) as several named
  recipes — one per part — rather than one tangled entry.

### When you save vs. skip
You do not have to save every one-off. The moment a request is something you
will plausibly ask for again, saving it pays off; a single, throwaway number
does not need a recipe.

### Behind the scenes
Because saving a recipe changes the project's brain, it is treated like any
durable change: you are shown exactly what will be added or altered, and you
approve it before it is written. The machine-readable mirror is updated as part
of that same approved change — it is not a separate decision — and it is written
by the native tool, not hand-edited, so the two copies stay in step.

### Pro tips
- Give recipes stable, memorable names — that name is how you re-run them later.
- Keep the saved query honest with the real columns: check the store's shape
  first so a recipe does not drift from the data.
- A dashboard is registered as its own entry (it points at the produced file and
  its synced location) separately from the query recipes that feed it.

### Related
- [sidekick-report/query-data-store](query-data-store.md) — produces the query a
  recipe captures.
- [sidekick-report/build-dashboard](build-dashboard.md) — a dashboard may bind to
  a saved recipe by name.

## Technical

`skills/sidekick-core/scripts/reports.py` is the recipe registry; the human mirror
is `brain/reports.md`.

Two halves, two homes:
- **`brain/reports.md`** — one `##` section per report: name, `What:`, `Render:`,
  and the exact `SELECT`(s). The gated, plain-language source of truth. Writing or
  changing it is a brain write → diff + approval.
- **`.sidekick/reports.json`** — the machine-readable mirror, written via the
  `save_report` MCP tool (native) / `reports.py save`. The bash `reports.py save`
  truncates on the Cowork mount, so the **native** tool is the reliable path; never
  hand-write the JSON.

`save(project, name, sql=None, desc=None, artifact=None, drive_file_id=None,
tables=None)` (~L64) **merges** — only supplied fields update, so `drive_file_id`
can be set later once the HTML is synced. A name must match `_NAME`
(`^[A-Za-z0-9][A-Za-z0-9_-]*$`). An entry must carry **at least** `sql` (a query
recipe) **or** `artifact`/`drive_file_id` (a dashboard registration), else it
raises. `.sidekick/reports.json` lives in the hidden state folder (never scanned
as a data table); `_path()` migrates a legacy root-level `.reports.json` on first
access.

Companion functions (not in this node's write path but same module):
`run(project, name)` executes a recipe's SELECT via `data.query` — and refuses a
sql-less dashboard entry; `uses(project, table)` lists recipes reading a table
(drives regeneration on a data change); `list_reports(project)` enumerates them.
The dashboard's *rendering* queries live inline in the `.sk.json` bindings — the
registry exists for named reuse and the `drive_file_id` the live wrapper needs.

Dependencies: upstream `sidekick-report/query-data-store` (the SELECT to persist).
Gatekeeper detail: `skills/sidekick-core/references/reporting.md` ("A report =
recipe + artifact", "Also register the recipe"); `docs/ARCHITECTURE.md` §7b.
