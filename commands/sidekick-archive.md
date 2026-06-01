---
description: Archive a Sidekick project by moving it to _archive/ (never deletes).
---

Run the **sidekick-archive** skill now.

Identify the project to archive (if unspecified, list the non-archived projects
with a one-line status and ask). Confirm in plain language exactly what will
move, then move the whole `projects/<slug>/` folder to
`_archive/projects/<slug>/` — a move, never a delete; on a name collision append
a date suffix. Prefer a true rename; if the runtime cannot rename atomically,
copy, verify the copy, and only then remove the source. Offer to restore a
project back if asked.
