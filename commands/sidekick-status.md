---
name: sidekick-status
description: Read-only cross-project status overview — where everything stands, no proposals.
---

Invoke the `sidekick-status` skill. It will:

1. Walk every non-archived project (read-only — it writes nothing).
2. Report per project: open `agenda.md` items and waiting-on, the count of
   undistilled logs, the date of the last check-in, the `data/` tables with
   their row counts, and how recently the project was active.
3. If a calendar is connected, note upcoming items in the near term.
4. Give a short prose summary (no proposal cards), ending with a nudge to run
   `/sidekick-checkin` if action is due.
