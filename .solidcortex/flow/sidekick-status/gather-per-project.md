---
flowId: sidekick-status
nodeId: gather-per-project
type: process
slug: gather-per-project
status: current
kind: derived
summary: Per-project read loop — collects open agenda items and waiting-on, counts undistilled logs, reads the last check-in date, and flags staleness, all without writing.
systems: [skills]
domains: [triage-checkin, project-model]
parent: main/sidekick-status
mainCodeFile: skills/sidekick-status/SKILL.md
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** The per-project read loop that gathers the non-data signals for one project — open agenda items, undistilled-log count, last check-in date, and staleness.
**Inputs:** One non-archived project folder; its `agenda.md`, `log/` directory, and `log/YYYYMMDD-checkin.md` files.
**Outputs:** Per-project facts handed back to the entry surface for the prose summary; nothing written.
**Code anchor:** [skills/sidekick-status/SKILL.md](../../../skills/sidekick-status/SKILL.md)
**Edges:** ← sidekick-status/status-entry (started by)
**Key rules:**
- Read-only: never write, stamp, distill, or modify any file.
- An undistilled log is a `log/` file lacking the `> distilled to brain:` stamp.
- Last check-in = newest `log/YYYYMMDD-checkin.md` date, if any.
- Keep agenda reporting to the few items that matter (open count + waiting-on/overdue).
- Staleness is judged from the most recent `log/` modification date (e.g. quiet 10+ days).

## Functional (user facing)

### Why use this?
This is the part of the status glance that tells you, for each project, whether it needs your attention — without you having to open it. It surfaces what's still on the agenda, how far the brain has fallen behind your notes, when you last sat down with the project, and whether it's gone quiet. The value is mostly invisible: you only notice it as the per-project lines in your status summary.

### What it does
- Reads `agenda.md` and reports the count of open items, plus anything marked waiting-on or overdue.
- Counts the logs that haven't been folded into the brain yet — a heads-up that the brain is behind your notes.
- Finds the most recent check-in date so you know when you last reviewed the project.
- Flags projects that have gone quiet based on how long it's been since any log changed.
- Keeps it tight: only the agenda items that actually matter, not an exhaustive dump.

### When nothing is stale
If a project has recent activity, no overdue agenda items, and no pile of undistilled logs, its line in the summary is short and quiet — that's the signal that it's healthy and needs nothing from you right now.

### Behind the scenes
For each non-archived project the loop reads three plain-markdown sources — the agenda, the log folder, and the dated check-in files — and derives a few counts and dates from them. None of this is persisted; the numbers exist only long enough to be folded into the prose summary.

### Pro tips
- A growing undistilled-log count is the earliest sign a project's brain is drifting out of date — that's usually the cue to run a check-in.
- "Last check-in" is read from the dated check-in filenames, so a project you've logged into recently but never formally checked in on will still show as stale on that axis.

### Related
- [status-entry](status-entry.md) — the surface that starts this loop and prints the result.
- [read-data-tables](read-data-tables.md) — the sibling read that adds data/ row counts to the same per-project line.

## Technical

**Main code locations**
- `skills/sidekick-status/SKILL.md`, "Per-project read" section — the spec for this loop: items 1 (open agenda + waiting-on), 2 (undistilled-log count), 3 (last check-in date), and 5 (activity/staleness). Item 4 (data tables) is delegated to the read-data-tables node.

**Inputs read (per project, all markdown / filesystem)**
- `agenda.md` — open-item count and waiting-on/overdue markers.
- `log/` directory — files scanned for the `> distilled to brain:` stamp; absence of the stamp ⇒ counted as undistilled.
- `log/YYYYMMDD-checkin.md` — newest filename date taken as the last check-in.
- `log/` modification times — most recent mtime drives the staleness flag (e.g. no activity in 10+ days).

**Constraints**
- Strictly read-only — no writes, no stamping, no distillation, no backup, no gatekeeper (ARCHITECTURE.md §11b).
- Operates per non-archived project; the entry surface handles enumeration and the direct-children-only rule, so this loop never re-scans for nested projects.

**Dependencies**
- Upstream: `sidekick-status/status-entry` invokes this once per project.
- Sibling: `sidekick-status/read-data-tables` contributes the data/ table counts for the same project; the two are merged into one summary line by the entry surface.
