---
domains:
  - structured-data
edges:
  - label: re-check schema on no-such-column error
    to: structured-data/info-discover
    via: starts
flowId: structured-data
generatedAt: 2026-06-14T11:55:56Z
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generator: solidcortex@0.17.0
kind: derived
mainCodeFile: skills/sidekick-core/scripts/data.py
nodeId: query-data
parent: sidekick-core/structured-data
related:
  - sidekick-find/probe-data-tables
  - sidekick-status/read-data-tables
  - sidekick-report/query-data-store
slug: query-data
status: current
summary: Run a read-only SELECT over a throwaway in-memory SQLite copy of the JSON tables — the only sanctioned way to count, filter, and total data.
systems:
  - python-helpers
type: process
---

## TLDR (agent)
**Purpose:** Answer any question about a project's structured data by running a read-only SELECT over a throwaway in-memory SQLite built fresh from the JSON table files.
**Inputs:** `data.py query --project DIR --sql "<SELECT>"` (SQL via the `--sql` flag, never positional); loads every `data/<table>.json` except `_schema.json`.
**Outputs:** `{ok, action:"query", rowcount, rows:[…]}`; on bad SQL a `ValueError` → `error:` exit, enriched with the real tables+columns when the cause is `no such column/table`.
**Code anchor:** [skills/sidekick-core/scripts/data.py](../../../skills/sidekick-core/scripts/data.py)
**Edges:** → structured-data/info-discover (re-check schema on no-such-column error)
**Key rules:**
- Only statements starting with `SELECT` or `WITH` (after stripping leading `(`) are accepted; anything else is rejected.
- The in-memory DB is discarded after the read — a query physically cannot mutate or lose on-disk data.
- Each table is exposed under its file stem (`recurring_revenue.json` → table `recurring_revenue`).
- `bool` values load as `1`/`0`; `dict`/`list` cell values load as their JSON string.
- Querying is free (no gatekeeper); never `cat`/`grep` the JSON to answer a question.

## Functional (user facing)

### Why use this?
This is how Sidekick answers "how many", "which ones", "what's the total", or "sorted by" about your data — reliably and at any scale. It runs a real database query, so it will not miss a row or mis-match a value the way eyeballing a file can, and it works just as well on a 5-row table as a 5,000-row one.

### What it does
- Accepts a single read-only `SELECT` (or `WITH`) and returns the matching rows plus a row count.
- Loads a fresh, temporary in-memory database from the JSON files for each query and throws it away afterwards — your stored files are read, never written.
- Exposes each table under its plain file name, so the SQL reads naturally.
- Refuses anything that would change data (no `INSERT`/`UPDATE`/`DELETE`), with a clear message pointing to the right tool.

### When the SQL is wrong
A typo in a column or table name comes back as a `no such column/table` error — and the message now appends the real tables and their columns (`| available: deals(product, platform, arr)`), so the next attempt can land without a separate inspection round-trip. That self-correction is why this node loops back to the discovery step.

### Behind the scenes
Because the database is rebuilt from disk for every query and discarded, there is no persistent database to corrupt, drop, or desync — the failure mode that retired the old single-file SQLite store. Numbers stored as numbers stay numbers, so totals and comparisons need no casting. Large extracts belong in a log file, not the chat; if a result becomes an exported deliverable, that is a separate, confirmed output action.

### Pro tips
- Prefer explicit column lists over `SELECT *` in anything you keep.
- Filtering a category column? Check its exact spelling first (via the discovery step) — `WHERE section = 'ONPREM'` silently returns nothing if the stored value is `ON-PREM`.

### Related
- structured-data/info-discover — run first to learn the real table and column names; also where a `no such column` error sends you back.

## Technical

**Entry point.** `query(project, sql)` in `skills/sidekick-core/scripts/data.py`, exposed via `cmd_query` (the `query` subparser, `--project` + `--sql`). `query()` is also imported by the `sidekick-sync` MCP server for report recipes, so it raises `ValueError` rather than exiting — the CLI wrapper converts that to a non-zero `error:` exit.

**Guard.** `sql.strip().rstrip(";")` then a check that the lower-cased statement (after stripping leading `(`) starts with `select` or `with`; otherwise `ValueError`. This is the read-only contract — there is no SQL parser, just the prefix gate plus SQLite's own refusal of writes against a DB it discards anyway.

**Build.** Opens `sqlite3.connect(":memory:")` with `row_factory = sqlite3.Row`. For each `data/*.json` (skipping `_schema.json` and any non-identifier stem), reads the row array, resolves columns via `_table_columns`, `CREATE TABLE "<table>" (<quoted cols>)`, and `executemany` an `INSERT` of every row. Cell values pass through `_sqlval`: `dict`/`list` → JSON string, `bool` → `1`/`0`, else as-is. The set of built tables/columns is retained for error enrichment.

**Error path.** On `sqlite3.Error`, raises `ValueError("query failed: …")`; when the message contains `no such`, it appends `| available: <table>(<cols>); …` from the built map so the caller (and the discovery loop-back edge) can self-correct. `conn.close()` runs in a `finally`.

**Dependencies.** Pure stdlib `sqlite3`; shares `_data_dir`, `_load_schema`, `_table_columns`, `_IDENT` with the rest of `data.py`. The throwaway-DB rationale and the "answering any question goes through query" rule are documented in ARCHITECTURE.md §4/§13 and `references/data-discipline.md`.
