---
name: sidekick-status
description: Read-only cross-project status overview for Sidekick. Use when the user runs /sidekick-status or asks "where do things stand", "what's going on across my projects", "give me an overview", or "status". Walks every non-archived project and reports, in prose, the open agenda items, the number of undistilled logs, the last check-in date, the data/ tables with row counts, and how recently each project was active; notes upcoming calendar items if connected. Writes nothing and proposes nothing — it is the read-only sibling of /sidekick-checkin. Does NOT act, distill, or change any file.
---

# Sidekick — Status

You give the user a fast, **read-only** picture of where everything stands.
You change nothing, propose nothing, and ask nothing through a picker — this
is a glance, not a decision point. (The check-in is where actions happen.)

## Preconditions

1. Read `sidekick.settings.md` (chat language, connected calendar). If it is
   missing, say the workspace isn't initialized and point to `/sidekick-init`.
2. List `projects/` — non-archived only (ignore `_archive/`). **Direct
   children only:** a project's internal `brain/<area>/` or `output/<area>/`
   subfolders are **subprojects/areas**, covered as part of their parent — not
   separate projects. Never descend into a project looking for more projects.
3. If a calendar is connected, fetch upcoming items in the near term
   (e.g. next 7–14 days). **Read-only.**

## Per-project read

For **each** non-archived project, gather (without writing anything):

1. **Open agenda items.** From `agenda.md`: count open items and list any
   marked waiting-on or overdue. Keep it to the few that matter.
2. **Undistilled logs.** Count files in `log/` that lack the
   `> distilled to brain:` stamp (a heads-up that the brain is behind).
3. **Last check-in.** The newest `log/YYYYMMDD-checkin.md` date, if any.
4. **Data tables.** Resolve the helper once — `$CLAUDE_PLUGIN_ROOT` is unset in
   the shell, so find it:
   `SK="$(find ~ -ipath '*/sidekick-core/scripts' -type d 2>/dev/null | head -1)"`,
   then run `python3 "$SK/data.py" info --project projects/<slug>`
   and report each table with its row count. Skip projects with no `data/`.
5. **Activity / staleness.** From the most recent `log/` modification date,
   note projects that have gone quiet (e.g. no activity in 10+ days).

## Output

Give a **short prose summary** in the chat language — one compact line or two
per project. **No proposal cards, no pickers** (you decide nothing). Surface
cross-project flags worth attention: a deadline cluster, a project gone quiet,
a pile of undistilled logs.

End with a single nudge if action is clearly due, e.g. *"3 logs wachten op
distillatie en BPD heeft een deadline donderdag — `/sidekick-checkin` draaien?"*
— phrased as a suggestion, not a forced choice.

Keep it scannable. The detail lives in the projects; this is the dashboard.

## Boundaries

- **Read-only.** Never write, distill, stamp, or modify any file, and never
  touch the calendar.
- For anything that needs a decision or a change, point to `/sidekick-checkin`
  (or the relevant skill) — don't do it here.
