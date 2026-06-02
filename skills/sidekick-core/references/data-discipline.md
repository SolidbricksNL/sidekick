# Structured-data discipline (`data/`)

The full protocol for a project's structured data. Loaded on demand by the
`sidekick` skill.

## Where structured data lives

When information shared in a project is **genuinely structured** — lists,
records, repeating fields, things you would naturally query — it belongs in
the project's data store, not scattered across log files or the brain. The
store is **plain JSON files**, one per "table", under
`projects/<slug>/data/`:

```
projects/<slug>/data/
  <table>.json        a JSON array of row objects (the data itself)
  _schema.json        table → columns (+ types); the structure of a record
  .snapshots/         automatic pre-write copies (ring, last 20)
  .backups/           dated full copies (made by the check-in)
```

The brain holds prose knowledge ("the BPD contract renews annually"). The
data store holds queryable records ("142 contacts, each with name, company,
role, email"). Don't put structured records in the brain, and don't put
prose narrative in the data store.

**Why plain files, not a database file.** A single `data.sqlite` was a
binary blob the user couldn't inspect and the model couldn't safely
edit — a stray `DROP`/recreate emptied it, and the model kept reaching for
the `sqlite3` CLI (absent in Cowork) or ad-hoc `python`. Plain JSON files
are human-readable, git-diffable, trivially backed up, and have no schema to
drop. The query power that made SQLite attractive is preserved without the
risk (see "Querying" below).

## The one rule: always go through `scripts/data.py`

**Every** read and write of structured data goes through the bundled helper.
**Never** read or edit a `data/*.json` file directly, **never** use the
`sqlite3` CLI, **never** write ad-hoc `python -c "import sqlite3 …"`. The
helper exists so that:

- reads are real queries (filter/sort/count) without pulling the whole file
  into the chat, and
- writes are validated against the table's columns and **snapshot the file
  first**, so any mistake is recoverable.

Reading the raw JSON "just to look" is the start of the failure mode — it
leads to hand-edits that desync the data and the schema. Resist it; use
`query` and `info`. **This includes answering questions:** to find out "how
many", "which", or "what's the total", run `data.py query`, never `cat`/
`grep` the JSON. A `SELECT` is more reliable than eyeballing the file (it
won't miss a row or mis-match a value) and it scales when the table is large.

### Emergency fallback (only when the helper truly fails)

The helper is robust, but a sandbox can still break it in ways you can't fix
(e.g. it refuses a file operation). If `data.py` **repeatedly fails on a
genuine environment problem** — not a usage mistake — you may, as a last
resort, write the table file directly. When you do:

1. First re-check it isn't a usage error: an `insert` takes `--json` (a JSON
   object, or a **JSON array** for many rows); table/column names are
   letters/digits/underscore; columns must already exist (`info`).
2. Keep `<table>.json` a **valid JSON array of objects** whose keys match
   `_schema.json` exactly. Do not change the structure by hand — a new
   column still goes through `addcol` (or hand-edit `_schema.json` too, and
   say so).
3. **Tell the user** you fell back to a direct write and why, and go back to
   the helper for the next operation.

This escape hatch exists precisely so a permission glitch never blocks the
work. It is the exception, not the routine — the helper is still the rule.

### Locating the helper in Cowork

The plugin installs outside the working directory, and **`$CLAUDE_PLUGIN_ROOT`
is not set in the shell the model runs** — it only expands inside `plugin.json`
and hook commands, never in a Bash call. So resolve the scripts dir once by
searching, then call the helper from it (the `--project` path stays relative to
the Cowork root):

```
SK="$(find ~ -ipath '*/sidekick-core/scripts' -type d 2>/dev/null | head -1)"
python3 "$SK/data.py" <cmd> --project projects/<slug> …
```

The same `$SK` holds `reports.py` and `sync.py`. If `$SK` comes back empty the
search didn't reach the install — widen the root (e.g. `find ~ /` ). If a helper
dies with `SyntaxError` / "'(' was never closed", the installed copy was
**truncated on install** (Cowork caps plugin files near ~15.8 KB); report that
rather than falling back to raw JSON reads.

## When to use the data store

Use it when the information has a clear, repeating shape and the user will
plausibly want to filter, count, sort, or relate it. Signals:

- The user shares or builds a list of similar items.
- The same fields recur across many entries.
- The user asks questions like "how many", "which ones", "sorted by".

**A shared spreadsheet, CSV, or exported table is structured by default.**
When the user hands you tabular data — rows with consistent columns — the
correct first move is to **propose a table and load the rows**, not to write
the data into a log file and chat a summary. Classify the input's shape on
arrival; if it is tabular, the data store is the destination for the rows.
(The prose *insights* you draw from it still go to `brain/`, the original
file to `archive/`, and the process to `log/` — but the rows themselves
belong in `data/`.) Defaulting tabular input into a log + summary, with no
table proposed, is the failure this discipline exists to prevent.

Do **not** force unstructured or one-off information into tables. A single
fact is a brain line, not a table.

## Three principles

1. **You design the tables.** Decide the columns yourself, based on the
   actual shape of the data. Choose clear table and column names a
   non-technical person would recognize. Table and column names use
   letters, digits, and underscores (e.g. `recurring_revenue`).
2. **Extend before you add.** When new related information arrives, run
   `info` first to see whether it fits an existing table (possibly via
   `addcol`) before creating a new table. The store must not become a
   tangle of overlapping tables.
3. **Schema as knowledge.** Document every table in plain language in
   `brain/data-model.md` so that you — and the user — can write clear
   queries later without re-inspecting the structure.

## The gatekeeper: structure changes only

**Confirmation is required for structure changes, in plain language.**

A structure change is: **creating a table** (`create`) or **adding a
column** (`addcol`).

- Ask in terms the user understands, tied to their data — never SQL.
  - Good: *"You're now also tracking phone numbers for contacts. Shall I
    add a phone field to the contact list?"*
  - Bad: *"ALTER TABLE contacts ADD COLUMN phone TEXT;"*
- Show what will change and why, then wait for approval.
- Only after approval, run the `create`/`addcol` command and update
  `brain/data-model.md`.

**No confirmation needed for:**

- **Reading** data (`query`, `info`).
- **Populating** existing tables with records that fit the existing
  columns (`insert`). Adding rows is normal use, not a structure change.
- **Correcting** rows (`update`/`delete`) is record-level, not structural —
  but it changes the user's data, so do it on the user's instruction and
  let the snapshot cover any slip. The helper refuses a `delete` with an
  empty match, so you can't wipe every row by accident.

This keeps the workflow fluid: the user approves the *shape* once, then
data flows in freely.

## The helper commands

All commands print a JSON result and exit non-zero on error. `DIR` is the
project path, e.g. `projects/finance`.

| Need | Command | Gatekeeper |
|---|---|---|
| Create a table | `data.py create --project DIR --table NAME --columns "a:text,b:number"` | confirm first |
| Add a column | `data.py addcol --project DIR --table NAME --column NAME --type text` | confirm first |
| Insert records that fit | `data.py insert --project DIR --table NAME --json '<object-or-array>'` | free |
| Correct rows | `data.py update --project DIR --table NAME --match '{...}' --set '{...}'` | on instruction |
| Remove rows | `data.py delete --project DIR --table NAME --match '{...}'` | on instruction |
| Query (read-only) | `data.py query --project DIR --sql "<SELECT>"` | free |
| Inspect tables/columns | `data.py info --project DIR` | free |
| Dated backup | `data.py backup --project DIR --label check-in` | the check-in |

**Insert in one batch, not row by row.** `--json` takes a **JSON array** of
objects, so a whole spreadsheet goes in with a *single* `insert` call. Do
that — it is one subprocess and one snapshot, versus one of each per row.
Inserting 34 rows as 34 separate calls is slow and needlessly churns
snapshots. (`--row`/`--rows` are accepted as aliases of `--json`.) Each
mutating call snapshots the table first; snapshotting is **best-effort** — if
the sandbox refuses it, the write still goes through (a warning is printed).

Column types for `create`/`addcol`: `text`, `number` (alias `real`),
`integer`, `bool`, `date`. Types are preserved on disk (a JSON number stays
a number), so numeric queries need no casting. `_schema.json` stores only the
column **name and type** — human-readable column *descriptions* live in
`brain/data-model.md` (prose), kept in step with the structure, not in the
schema file.

## Querying — over a throwaway in-memory database

`query` loads every `data/<table>.json` into a **fresh in-memory SQLite**,
runs your `SELECT`, returns the rows as JSON, and discards the database. The
on-disk files are read only for loading and never written, so a query
**cannot** mutate or lose data — there is no persistent database to corrupt.

- Each table is available under its file name (`recurring_revenue.json` →
  table `recurring_revenue`).
- Only `SELECT`/`WITH` statements are accepted; the helper rejects anything
  else with a clear message. To change data, use `insert`/`update`/`delete`.
- Write clear SQL; prefer explicit column lists over `SELECT *` in anything
  you keep. Summarize results in the chat language; put any large extract in
  `log/`, not the chat. If a result becomes a deliverable (an exported
  sheet), that is an `output/` action and needs confirmation.

**Match exact values on category columns.** A filter like
`WHERE section = 'ONPREM'` silently returns nothing if the stored value is
`ON-PREM`. Before filtering on a text/category column whose spelling you are
not certain of, check the real values first: `data.py info` lists the
**distinct values of every low-cardinality column** (so you'd see `ON-PREM`,
`CLOUD`, `SOFTWARE`), or run `SELECT DISTINCT section FROM …`. Record those
allowed values in `brain/data-model.md` so the next session doesn't have to
rediscover them.

## Safety: snapshots and backups

- **Per-write snapshots.** Before every `insert`/`update`/`delete`/`addcol`,
  the helper copies the table file into `data/.snapshots/` (a ring of the
  last 20). An in-session slip is always recoverable from there.
- **Dated backups.** The **check-in** runs `data.py backup` per project
  before it processes anything, writing a timestamped copy of all table
  files + `_schema.json` into `data/.backups/`. This is the durable, dated
  safety line. Restoring is a plain file copy back.

## `brain/data-model.md` format

Keep it lean and current. One section per table:

```markdown
# Data model

_Last updated: 2026-06-01_

## contacts
Stores people we deal with in this project.

| column   | type   | meaning                          |
|----------|--------|----------------------------------|
| name     | text   | full name                        |
| company  | text   | organization they belong to      |
| role     | text   | their job title                  |
| email    | text   | primary email                    |
| phone    | text   | primary phone (added 2026-06-01) |
| segment  | text   | category: `CLOUD`, `ON-PREM`, `SOFTWARE` |

Typical queries: list all contacts at a given company; find contacts
without an email.
```

For **category columns** (a small fixed set of values), write the exact
allowed values into the `meaning` cell, as `segment` shows above — that is
what stops the next `WHERE` from guessing `ONPREM` instead of `ON-PREM`.
`data.py info` reports those distinct values, so you can fill or refresh this
from the live data.

When you change the structure, update this file in the same step (after
approval). Regenerate it from the live structure with `info` if it drifts.

## Lazy creation

Do not create `data/` during project scaffolding. It appears the first time
structured data actually needs storing — the first `create` makes `data/`,
`_schema.json`, and the first `<table>.json`. That first `create` is itself a
structure change, so confirm it in plain language.
