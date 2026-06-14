---
domains:
  - structured-data
edges:
  - label: shape approved, data flows in
    to: structured-data/record-write
    via: starts
  - label: addcol snapshots first
    to: structured-data/snapshot-backup
    via: starts
flowId: structured-data
generatedAt: 2026-06-14T11:55:56Z
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generator: solidcortex@0.17.0
kind: derived
mainCodeFile: skills/sidekick-core/scripts/data.py
nodeId: design-table
parent: sidekick-core/structured-data
related:
  - write-disciplines/structured-data-handoff
slug: design-table
status: current
summary: The gated structure change — create a new table or addcol an existing one, confirmed in plain language and recorded in brain/data-model.md.
systems:
  - python-helpers
type: process
---

## TLDR (agent)
**Purpose:** Make a gated structure change — `create` a new table from a column spec, or `addcol` a column onto an existing one — each confirmed in plain language before it runs.
**Inputs:** `data.py create --project DIR --table NAME --columns "a:text,b:number"`; `data.py addcol --project DIR --table NAME --column NAME --type text`.
**Outputs:** `create` → `{ok, action:"create", table, columns}` + empty `<table>.json` + `_schema.json` entry; `addcol` → `{ok, action:"addcol", table, column}`, back-filling existing rows with `null`.
**Code anchor:** [skills/sidekick-core/scripts/data.py](../../../skills/sidekick-core/scripts/data.py)
**Edges:** → structured-data/record-write (shape approved, data flows in), → structured-data/snapshot-backup (addcol snapshots first)
**Key rules:**
- Both `create` and `addcol` require plain-language user confirmation first (the only gated operations); reads and inserts are free.
- `create` refuses an existing table — extend with `addcol`, never recreate (recreate discards data).
- Table/column names must be `[A-Za-z_][A-Za-z0-9_]*`; types limited to text/number/integer/real/bool/boolean/date.
- `addcol` snapshots the table before altering it; `create` writes a fresh empty array (nothing to snapshot).
- After approval, also update `brain/data-model.md` to keep schema-as-knowledge current.

## Functional (user facing)

### Why use this?
This is the one place the data store's *shape* changes — a new list (table) or a new field (column) on an existing list. Because shape decisions are the ones a user should sign off on, this step always asks first, in plain terms tied to your data, never in database jargon.

### What it does
- Creates a new table from a list of named columns, each with a type, and starts it empty.
- Adds a single new column to an existing table, filling every existing row with a blank value for it.
- Rejects recreating a table that already exists, so an accidental "create" can never wipe rows that are already there.
- Accepts only simple, recognisable names (letters, digits, underscores) and a short list of column types.

### When confirmation is needed
Creating a table and adding a column are the only two operations gated behind a yes. Sidekick presents the change the way you would describe it — "You're now also tracking phone numbers for contacts. Shall I add a phone field to the contact list?" — and waits. Reading data and adding rows that fit existing columns are never gated; you approve the shape once, then records flow in freely.

### When a table already exists
Asked to create a table that is already there, this step refuses rather than overwriting — recreating would discard the existing data. The correct move to grow it is to add a column, which preserves every row.

### Behind the scenes
The very first `create` in a project is also what lazily brings the `data/` folder into being, alongside the schema file. From that point the schema file records each table's columns and types. Adding a column also takes a safety snapshot of the table first, since it rewrites every row to include the new blank field. Whenever the shape changes, the project's plain-language data-model notes are updated in the same step so future queries can be written without re-inspecting the structure.

### Pro tips
- Choose clear, human-recognisable table and column names — a non-technical person should know what `recurring_revenue` holds.
- Prefer extending an existing table over spawning a near-duplicate one; check fit with the discovery step first.
- Record a category column's allowed values into the data-model notes when you create it, so later filters match the exact spelling.

### Related
- structured-data/record-write — once the shape is approved, records flow in here.
- structured-data/snapshot-backup — `addcol` takes a pre-change snapshot through this safety layer.
- structured-data/info-discover — check whether an existing table already fits before creating a new one.

## Technical

**Entry points.** `cmd_create(args)` and `cmd_addcol(args)` in `skills/sidekick-core/scripts/data.py`, on the `create` (`--table`, `--columns`) and `addcol` (`--table`, `--column`, `--type`) subparsers. The plain-language confirmation gate is enforced by the calling skill, not the script — `data.py` performs the validated mutation once invoked.

**`cmd_create`.** Validates the table name via `_ident`, then refuses if the table is already in `_load_schema` **or** its file exists (the "use addcol, do not recreate" guard). Parses `--columns` as comma-separated `name:type` (bare name defaults to `text`), validating each name with `_ident` and each type against `_TYPES = {text, number, integer, real, bool, boolean, date}`; an empty list errors. Writes the schema entry `{columns:[…], created: _ts()}` via `_save_schema` and an empty `[]` row file via `_write_rows` — this is the call that first materialises `data/` and `_schema.json` (lazy creation).

**`cmd_addcol`.** Validates table + column names and the type, requires the table to be in the schema, and refuses a duplicate column. Calls `_snapshot` before mutating (its edge to snapshot-backup), appends the column to the schema, then `setdefault(column, None)` on every existing row and rewrites the file — so existing rows gain the column as `null`.

**Key structures.** `_schema.json` maps `table → {columns:[{name,type}], created}`. `_IDENT = ^[A-Za-z_][A-Za-z0-9_]*$`. Types stored verbatim; `_schema.json` holds only name+type — human-readable column descriptions live in `brain/data-model.md` (prose), not the schema.

**Dependencies.** Shares `_ident`, `_load_schema`, `_save_schema`, `_write_rows`, `_load_rows`, `_snapshot`, `_ts` with the rest of `data.py`. Gatekeeper protocol and the data-model-notes upkeep rule are in `references/data-discipline.md` and ARCHITECTURE.md §4.
