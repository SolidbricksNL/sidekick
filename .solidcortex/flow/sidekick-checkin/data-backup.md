---
flowId: sidekick-checkin
nodeId: data-backup
type: process
slug: data-backup
status: current
kind: derived
summary: Hard-rule timestamped backup of each project's data/ via data.py backup (into data/.backups/) before the check-in processes anything in that project.
systems: [python-helpers]
domains: [structured-data]
parent: main/sidekick-checkin
mainCodeFile: skills/sidekick-core/scripts/data.py
edges:
  - to: sidekick-checkin/per-project-walk
    via: starts
    label: proceed to per-project walk
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Takes a dated, labelled copy of a project's structured data before the check-in does anything else with that project.
**Inputs:** trigger: check-in reaching a project that has a `data/` folder; runs `data.py backup --project projects/<slug> --label check-in`; helper located via find-resolver (`$CLAUDE_PLUGIN_ROOT` unset in shell).
**Outputs:** a timestamped copy of every `data/*.json` under `data/.backups/<timestamp>-check-in/`; JSON result with `backup` path + copied `files`; then per-project walk.
**Code anchor:** [skills/sidekick-core/scripts/data.py](../../../skills/sidekick-core/scripts/data.py)
**Edges:** ← sidekick-checkin/checkin-entry (parent), → sidekick-checkin/per-project-walk (starts)
**Key rules:**
- Hard rule: the check-in never processes a project's data without first taking a dated backup.
- Backup runs before anything else in that project (step 0 of the per-project walk).
- A project with no `data/` folder yet is skipped silently (the command returns `exists: false`).
- Only `*.json` files in `data/` are copied; the copy lands in `data/.backups/`, not in `output/` or the brain.

## Functional (user facing)

### Why use this?
Your structured records are the one thing in a project you can't easily reconstruct by hand. Before the check-in starts proposing edits, corrections, or new records, it quietly takes a dated snapshot of that data — so if anything goes sideways during the session, the pre-check-in state is always recoverable.

### What it does
- Runs once per project, as the very first thing the check-in does with that project — ahead of reading the agenda or proposing actions.
- Copies the project's data records into a dated backup folder kept inside the data area, labelled so you can tell it came from a check-in.
- Skips projects that don't have any structured data yet — there's nothing to back up, and it says nothing about it.

### Behind the scenes
The snapshot is a plain file copy into a hidden backups folder beside your data; it doesn't touch the live records, the brain, or your deliverables. Each backup is stamped with the moment it was taken, so older snapshots accumulate as a history rather than overwriting each other. Once the copy is done, the check-in moves on to actually walking the project.

### Pro tips
- These snapshots are your undo for the session — if a check-in edit to your data was wrong, the pre-check-in copy is sitting in the backups folder.
- Backups pile up over time; they live in the data area's hidden backups folder, so they don't clutter what you see day to day.

### Related
- [checkin-entry](checkin-entry.md) — the step that gathers projects before this safeguard runs.
- [per-project-walk](per-project-walk.md) — what runs immediately after the backup, project by project.

## Technical

Backed by `skills/sidekick-core/scripts/data.py`, the `backup` subcommand (`cmd_backup`). The skill invokes it per project as step 0 of the per-project walk.

- **Invocation.** `python3 "$SK/data.py" backup --project projects/<slug> --label check-in`, where `$SK` is resolved at runtime via the find-resolver pattern (`SK="$(find ~ -ipath '*/sidekick-core/scripts' -type d ... | head -1)"`) because `$CLAUDE_PLUGIN_ROOT` is not exported into the shell.
- **What gets copied.** `cmd_backup` resolves the project's `data/` dir; if it does not exist it emits `{ok: true, exists: false, backup: null}` and returns (the silent skip). Otherwise it builds `dest = data/.backups/<_ts()>-check-in/`, `mkdir(parents=True)`, then `shutil.copy2`-copies every `sorted(data_dir.glob("*.json"))` file into it and emits `{ok, backup: <dest>, files: [...]}`.
- **Label.** `--label check-in` becomes the `-check-in` suffix on the timestamped folder name, distinguishing check-in snapshots from other backup origins.
- **Scope.** Only top-level `data/*.json` is copied — the structured store proper. The `.backups/` and `.snapshots/` subfolders and `.sidekick/` state are not recursed. Copies stay under `data/.backups/` (ARCHITECTURE §3.x project layout: backups/snapshots live in `data/.backups` + `data/.snapshots`), never synced to external storage.

**Dependencies.** Parent `sidekick-checkin/checkin-entry` supplies the project list. Hands off to `sidekick-checkin/per-project-walk`, which performs the remaining steps 1–6 per project. Shares `data.py` with the data-discipline layer (ARCHITECTURE §4) but only the read-only `backup` path is exercised here.
