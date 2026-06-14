---
domains:
  - structured-data
flowId: sidekick-status
generatedAt: 2026-06-14T11:55:56Z
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generator: solidcortex@0.17.0
kind: derived
mainCodeFile: skills/sidekick-core/scripts/data.py
nodeId: read-data-tables
parent: main/sidekick-status
related:
  - structured-data/query-data
  - structured-data/info-discover
  - sidekick-find/probe-data-tables
  - sidekick-report/query-data-store
slug: read-data-tables
status: current
summary: Resolves the data.py helper via find and runs data.py info per project to report each data/ table with its row count — own-backend read, no writes.
systems:
  - python-helpers
type: process
---

## TLDR (agent)
**Purpose:** Per-project data read — resolves the `data.py` helper and runs `data.py info` to report each `data/` table with its row count.
**Inputs:** A project slug; the project's `data/` JSON tables and `_schema.json`; the resolved path to `data.py`.
**Outputs:** Per-table name + row count (and categorical column values) for the status summary; nothing written.
**Code anchor:** [skills/sidekick-core/scripts/data.py](../../../skills/sidekick-core/scripts/data.py)
**Edges:** ← sidekick-status/status-entry (started by)
**Key rules:**
- Read-only — `info` only reads `data/*.json`; it never writes, snapshots, or backs up.
- `$CLAUDE_PLUGIN_ROOT` is unset in the shell — resolve `data.py` by `find` first.
- Skip any project with no `data/` directory.
- `info` returns `exists`, and `tables[]` each with `name`, `columns`, `rowcount`.
- Run with an absolute project path (`--project projects/<slug>`).

## Functional (user facing)

### Why use this?
This is the part of the status glance that tells you, per project, what structured data you're tracking and how much of it there is — the "deals: 42 rows, contacts: 8 rows" line. It saves you opening a project just to remember what tables exist or whether one has grown.

### What it does
- For each project that has a `data/` folder, lists every table and its current row count.
- Quietly skips projects that don't track any structured data, so they don't clutter the summary.
- Reads the live table files directly, so the counts reflect the latest state every time you run status.

### When a project has no data
Projects without a `data/` folder are simply left out of the data portion of their summary line — there's no "0 tables" noise, just silence on that axis.

### Behind the scenes
This read asks the Sidekick data helper for a project's table inventory. The helper opens each table file, counts its rows, and hands back the list. Nothing is created, changed, or snapshotted — it's a pure look.

### Pro tips
- The row counts are a fast sanity check that an import or a recent update actually landed — if a number looks wrong, that's the cue to open the project and look closer.
- Because the read goes straight to the table files, the numbers are always current; there's no cached figure that can go stale.

### Related
- [status-entry](status-entry.md) — the surface that starts this read and merges its counts into the summary.
- [gather-per-project](gather-per-project.md) — the sibling read covering agenda, logs, and staleness for the same project.

## Technical

**Main code locations**
- `skills/sidekick-core/scripts/data.py`, `cmd_info` — the `info` action. Globs `data/*.json` (skipping `_schema.json`), loads `_schema.json` for column definitions, and for each table emits `{name, columns, rowcount}` where `rowcount = len(rows)`. Categorical columns carry an extra `values` list (distinct values, exact-spelling match).
- `skills/sidekick-status/SKILL.md`, "Per-project read" item 4 — the caller-side contract: resolve the helper, run it per project, report each table with its row count, skip projects with no `data/`.

**Helper resolution**
- `$CLAUDE_PLUGIN_ROOT` is not exported into the shell, so the skill locates the script at run time:
  `SK="$(find ~ -ipath '*/sidekick-core/scripts' -type d 2>/dev/null | head -1)"`, then
  `python3 "$SK/data.py" info --project projects/<slug>`.

**Output shape (`action: info`)**
- No `data/` dir ⇒ `{ok: true, action: "info", project, exists: false, tables: []}`.
- Otherwise ⇒ `{ok: true, action: "info", project, exists: true, tables: [{name, columns:[{name, type, values?}], rowcount}]}`.

**Constraints**
- `info` is a read-only branch of `data.py` — unlike `insert`/`update`/`delete`, it takes no snapshot and writes nothing. Read-only by construction, so no gatekeeper or backup (ARCHITECTURE.md §11b).

**Dependencies**
- Upstream: `sidekick-status/status-entry` invokes this once per non-archived project that has a `data/` folder.
- The same `data.py info` command is reused by the `sidekick-find` recall flow; this node only consumes the read, it does not own the helper.
