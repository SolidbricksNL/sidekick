---
flowId: structured-data
nodeId: record-write
type: process
slug: record-write
status: current
kind: derived
summary: Free record-level writes that fit existing columns — batch insert, plus update/delete on instruction (delete refuses an empty match).
systems: [python-helpers]
domains: [structured-data]
parent: sidekick-core/structured-data
mainCodeFile: skills/sidekick-core/scripts/data.py
edges:
  - to: structured-data/snapshot-backup
    via: starts
    label: each write snapshots first
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Make record-level changes to existing tables — batch `insert` of fitting rows, plus `update` and `delete` on user instruction — without any structure change.
**Inputs:** `insert --json '<object-or-array>'`; `update --match '{…}' --set '{…}'`; `delete --match '{…}'`; all `--project DIR --table NAME`.
**Outputs:** `insert` → `{inserted, total}`; `update` → `{updated}`; `delete` → `{deleted, remaining}`; each snapshots the table file first.
**Code anchor:** [skills/sidekick-core/scripts/data.py](../../../skills/sidekick-core/scripts/data.py)
**Edges:** → structured-data/snapshot-backup (each write snapshots first)
**Key rules:**
- `insert` is free (normal use); `update`/`delete` run on the user's instruction, not a structure gate.
- `insert` rejects any row carrying a column not yet in the table — add it via `addcol` first.
- `delete` refuses an empty `--match` (cannot wipe every row by accident); an update/delete matching nothing is a clean no-op (0 rows).
- `--json` takes a single object or an array — insert a whole sheet in one batched call, one snapshot.
- Matching is exact-equality on every key in `--match`; there is often no `id` column, so match on real keys.

## Functional (user facing)

### Why use this?
Once a table's shape is approved, this is where the data itself moves: adding rows, correcting a value, or removing entries. Adding rows that fit the existing fields is everyday use and needs no approval — the shape was signed off once, so records flow in freely.

### What it does
- Adds one row or a whole batch of rows in a single call, as long as every field already exists on the table.
- Corrects rows that match a set of field values, setting new values on just those rows.
- Removes rows that match a set of field values.
- Reports exactly what happened — how many rows were inserted, updated, or deleted, and the new totals.

### When a row brings a new field
If an inserted row carries a field the table does not have, the write is refused with a pointer to add that field first. New fields are a shape change and go through the gated design step — they are never created silently by an insert.

### When the match hits nothing
An update or delete whose match finds no rows is a clean no-op: it reports zero changed and leaves the file untouched. A delete with an *empty* match is refused outright — that guard exists so an accidental "delete everything" cannot happen.

### Behind the scenes
Every one of these writes copies the table file into a safety snapshot before changing anything, so an in-session slip is always recoverable. Because of that, correcting or removing data is low-risk and can be done directly on your instruction. Inserting a spreadsheet as one batch is both faster and gentler on the snapshot ring than inserting row by row.

### Pro tips
- Hand a whole spreadsheet in as one array — a single batch is one subprocess and one snapshot, versus one of each per row.
- There is usually no `id` column; match update/delete on the real key fields (check them via the discovery step first).
- Values typed as numbers stay numbers on disk, so no quoting gymnastics are needed for numeric fields.

### Related
- structured-data/snapshot-backup — the pre-write snapshot every operation here triggers.
- structured-data/design-table — where a genuinely new field must be added before an insert can carry it.
- structured-data/info-discover — confirm the target columns (and that there is no `id`) before writing.

## Technical

**Entry points.** `cmd_insert`, `cmd_update`, `cmd_delete` in `skills/sidekick-core/scripts/data.py`, on subparsers `insert` (`--json`, aliased `--rows`/`--row`), `update` (`--match`, `--set`), `delete` (`--match`).

**`cmd_insert`.** Parses `--json`; a single dict is wrapped to a one-element list; an empty/non-list payload errors. Requires the table to exist (schema or file). When the table is in the schema it computes `allowed = set(_table_columns(...))` and rejects any row with an unknown column ("add them with addcol first"). Snapshots, loads rows, `setdefault`s every known column to `None` on each new row (so rows are column-complete), extends, and writes. Returns `{inserted: len(new), total: len(rows)}`.

**`cmd_update`.** Parses `--match`/`--set` (both must be dicts, `--set` non-empty). `_match_idx` returns the indices where every `match` key equals the row value. No match → `{updated:0}` no-op (no snapshot, no write). Otherwise snapshots, `dict.update`s each matched row with `setvals`, writes, returns `{updated: len(idx)}`.

**`cmd_delete`.** Parses `--match`; a non-dict or **empty** match errors (`"refusing to delete every row"`) — the structural safety guard. `_match_idx` finds the targets; none → `{deleted:0}` no-op. Otherwise snapshots, keeps rows whose index is not matched, writes, returns `{deleted, remaining}`.

**Key structures.** Matching is `all(r.get(k) == v for k,v in match.items())` — exact equality, no operators. `_snapshot` is invoked only after validation passes and at least one row is affected (insert always snapshots once validation passes).

**Dependencies.** Shares `_ident`, `_load_schema`, `_table_columns`, `_load_rows`, `_write_rows`, `_snapshot`, `_match_idx` with `data.py`. The free-vs-instruction discipline (insert free; update/delete on instruction; delete-empty refused) is documented in `references/data-discipline.md` and ARCHITECTURE.md §4.
