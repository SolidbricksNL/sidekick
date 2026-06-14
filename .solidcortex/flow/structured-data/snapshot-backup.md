---
flowId: structured-data
nodeId: snapshot-backup
type: process
slug: snapshot-backup
status: current
kind: derived
summary: The safety net — a best-effort per-write snapshot ring (last 20) before every mutation, plus dated check-in backups of all table files.
systems: [python-helpers]
domains: [structured-data]
parent: sidekick-core/structured-data
mainCodeFile: skills/sidekick-core/scripts/data.py
edges:
  - to: structured-data/info-discover
    via: starts
    label: recover then re-inspect
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Protect the data store — copy a table file into a rolling snapshot ring before every mutation, and on the check-in write a dated backup of all table files.
**Inputs:** `_snapshot(project, table)` auto-runs inside insert/update/delete/addcol; `data.py backup --project DIR [--label check-in]` runs explicitly.
**Outputs:** Snapshot → `data/.snapshots/<table>-<ts>.json` (ring kept to last 20); backup → `data/.backups/<ts>[-label]/` with every `*.json` copied; backup emits `{backup, files}`.
**Code anchor:** [skills/sidekick-core/scripts/data.py](../../../skills/sidekick-core/scripts/data.py)
**Edges:** → structured-data/info-discover (recover then re-inspect)
**Key rules:**
- Snapshotting is best-effort — an OS error prints a warning and the write still proceeds (a blocked sandbox never aborts a mutation).
- The snapshot ring keeps the last 20 per table (`_SNAPSHOT_KEEP`); older ones are pruned.
- A snapshot is taken before the change, so it captures the pre-mutation state.
- `backup` no-ops cleanly (`exists:false`) when the project has no `data/` yet.
- Restoring is a plain file copy back from `.snapshots/` or `.backups/` — there is no special restore command.

## Functional (user facing)

### Why use this?
This is the reason a mistake in the data store is never fatal. Every change is preceded by a quiet copy of the affected table, and the regular check-in takes a full dated backup — so an in-session slip or a bad day's edits can always be rolled back by copying a file.

### What it does
- Copies a table's file into a snapshot folder immediately before any change to it, keeping the most recent twenty copies per table.
- Takes a timestamped, labelled backup of every table file (and the schema) on the check-in, before anything else is processed.
- Never blocks a real write: if the environment refuses to make a snapshot, it warns and lets the change go through anyway.
- Reports cleanly when there is nothing to back up because the project has no data yet.

### When a snapshot can't be written
In a locked-down sandbox the snapshot copy can fail. Rather than abandon the user's edit, this layer prints a warning and lets the write proceed — the durable, dated check-in backup is the fallback safety line in that case. Recovering from a snapshot or backup is just copying the saved file back into place, after which the discovery step re-confirms the restored shape.

### Behind the scenes
There are two layers. Per-write snapshots are a short-term ring covering the current session's slips — twenty deep, oldest pruned automatically. The check-in backup is the long-term, dated line: it copies the whole `data/` folder into a timestamped subfolder before the check-in touches anything. Snapshots and backups are ordinary files, so they are inspectable, diffable, and restored by a plain copy. This two-layer net is part of why the store is plain files rather than a single binary database that a stray command could empty.

### Pro tips
- Twenty snapshots per table is a rolling window, not unlimited history — the dated check-in backups are the durable record for anything older.
- A backup labelled `check-in` lands in a clearly named dated folder, making it easy to find the right point to restore from.

### Related
- structured-data/record-write — every insert/update/delete here triggers a pre-write snapshot.
- structured-data/design-table — `addcol` also snapshots before altering the table.
- structured-data/info-discover — after restoring a file, re-inspect to confirm the recovered shape.

## Technical

**Entry points.** `_snapshot(project, table)` (internal, called by `cmd_addcol`/`cmd_insert`/`cmd_update`/`cmd_delete`) and `cmd_backup(args)` (the `backup` subparser, `--project` + optional `--label`) in `skills/sidekick-core/scripts/data.py`.

**`_snapshot`.** Returns immediately if the source table file is absent. Otherwise `mkdir -p data/.snapshots`, `shutil.copy2` to `<table>-<_ts()>.json` (timestamp `%Y%m%d-%H%M%S-%f`, microsecond-unique). The copy is wrapped in `try/except OSError`: on failure it prints `warning: snapshot … skipped` and returns — the caller's mutation continues regardless (best-effort contract). Pruning then deletes all but the newest `_SNAPSHOT_KEEP = 20` matching `data/.snapshots/<table>-*.json`, each `unlink` individually guarded so a prune failure is non-fatal.

**`cmd_backup`.** If `data/` is absent, emits `{exists:false, backup:None}`. Otherwise builds `data/.backups/<_ts()>[-label]/`, `shutil.copy2`s every `data/*.json` (table files **and** `_schema.json`) into it, and returns `{backup: <path>, files:[…]}`. Invoked by the project check-in (`--label check-in`) before it processes a project.

**Restore.** There is deliberately no restore subcommand — recovery is a manual file copy back from `.snapshots/` or `.backups/`, consistent with the plain-files design.

**Dependencies.** Shares `_data_dir`, `_table_path`, `_ts` with `data.py`; uses stdlib `shutil`/`pathlib` only. Ordering invariant: callers `_snapshot` *before* writing, so the snapshot holds the pre-mutation state. The best-effort rationale and the check-in backup role are in ARCHITECTURE.md §4 and `references/data-discipline.md`.
