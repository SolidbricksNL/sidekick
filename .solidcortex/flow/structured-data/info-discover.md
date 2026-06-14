---
flowId: structured-data
nodeId: info-discover
type: process
slug: info-discover
status: current
kind: derived
summary: Inspect a project's data store first — list tables, columns, and the distinct values of low-cardinality columns before any query or write.
systems: [python-helpers]
domains: [structured-data]
parent: sidekick-core/structured-data
mainCodeFile: skills/sidekick-core/scripts/data.py
entry: true
edges:
  - to: structured-data/query-data
    via: starts
    label: discover then read
  - to: structured-data/design-table
    via: starts
    label: extend before add
  - to: structured-data/record-write
    via: starts
    label: confirm columns before insert
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Report a project's data store — every table, its columns and types, row counts, and the distinct values of each low-cardinality column — as the mandatory first step before querying or writing.
**Inputs:** `data.py info --project DIR`; reads `data/_schema.json` + every `data/<table>.json`; no flags beyond `--project`.
**Outputs:** One JSON object `{ok, action:"info", project, exists, tables:[{name, columns:[{name,type,values?}], rowcount}]}`; `exists:false` with empty tables when no `data/` yet.
**Code anchor:** [skills/sidekick-core/scripts/data.py](../../../skills/sidekick-core/scripts/data.py)
**Edges:** → structured-data/query-data (discover then read), → structured-data/design-table (extend before add), → structured-data/record-write (confirm columns before insert)
**Key rules:**
- Run `info` before the first query/update/delete on any table not inspected this session.
- A column gets a `values` list only when it has ≤12 distinct non-null values (the enum cap); above that the key is omitted.
- Never assume an `id` column exists — match on the real key columns `info` reports.
- Reading never touches disk for writing; `info` is free (no gatekeeper).

## Functional (user facing)

### Why use this?
Before Sidekick can answer a question about your data or change a record, it needs to know exactly what is stored: which tables exist, what each column is called, and which spellings a category column actually uses. This step gives it that picture in one shot, so a later query lands on the real column names instead of guesses.

### What it does
- Lists every table in the project's data store with its columns, each column's type, and how many rows it holds.
- For any column with only a small, fixed set of values (a category like `CLOUD` / `ON-PREM` / `SOFTWARE`), it reports the exact allowed values — so a filter matches the real spelling instead of inventing one.
- Reports cleanly that the store is empty when a project has no data yet, rather than erroring.
- Reads only — it never changes a single record, so it is always safe to run.

### When the store is empty
A project does not get a `data/` folder until the first table is actually created. Asked to inspect a project that has never stored structured data, this step reports an empty store (nothing exists yet) instead of failing — a cue that the next move, if data is arriving, is to propose a table.

### Behind the scenes
This is the discovery move that the data discipline opens with: "info first, then act." It reads the schema and the row files straight off disk and summarises them; nothing it does can alter your data. The distinct-value reporting is what lets Sidekick record a category column's allowed spellings into the project's data-model notes so the next session does not have to rediscover them.

### Pro tips
- If a later query fails with "no such column/table," that error now lists the real tables and columns — but running `info` up front avoids the round-trip entirely.
- The allowed values it surfaces for category columns are the cure for silent empty results: a `WHERE` on a mis-spelled category returns nothing without complaining.

### Related
- structured-data/query-data — the read step `info` precedes.
- structured-data/design-table — when `info` shows no fitting table, this is where a new one (or column) is proposed.
- structured-data/record-write — confirm the target columns exist (via `info`) before inserting.

## Technical

**Entry point.** `cmd_info(args)` in `skills/sidekick-core/scripts/data.py`, wired to the `info` subparser (only `--project`). It is the graph's `entry: true` node for the structured-data flow.

**Flow.** Resolves `data/` via `_data_dir`. If absent, emits `{exists:false, tables:[]}` and returns — this is the lazy-creation contract (no `data/` until the first `create`). Otherwise loads `_schema.json` (`_load_schema`) and iterates `sorted(data_dir.glob("*.json"))`, skipping `_schema.json`. For each table file it reads the row array, takes the column list from the schema when present else infers it from row keys via `_table_columns`, and for every column computes `_distinct_values`.

**Key structures.** Output `tables[]` entries carry `name`, `columns` (each `{name, type}`, plus `values` when categorical), and `rowcount`. `_distinct_values(rows, name)` walks rows collecting distinct non-null values; it returns `None` (column omitted from the `values` enrichment) as soon as the count exceeds `_ENUM_MAX = 12`, otherwise returns the values sorted by `str()`. Non-scalar values are keyed by their JSON dump for de-duplication.

**Dependencies.** Internal helpers only — no other node's code. Shares `_load_schema`, `_table_columns`, `_data_dir` with the rest of `data.py`. The protocol that mandates calling this first lives in `skills/sidekick-core/references/data-discipline.md` ("info first, then act"). All five structured-data nodes back the same single ~400-LOC file, which sits under the ~15.8 KB Cowork install-truncation cap (the `BUDGET` banner in the module docstring); see ARCHITECTURE.md §13.
