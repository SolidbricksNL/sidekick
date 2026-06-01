---
name: sidekick-archive
description: Archive a Sidekick project by moving it to _archive/ (never deletes).
---

Invoke the `sidekick-archive` skill. It will:

1. Identify the project to archive (if unspecified, list the non-archived
   projects with a one-line status and ask).
2. Confirm in plain language exactly what will move, then move the whole
   `projects/<slug>/` folder to `_archive/projects/<slug>/` — a move, never a
   delete; on a name collision it appends a date suffix.
3. Prefer a true rename; if the runtime cannot rename atomically, copy, verify
   the copy, and only then remove the source.

It can also restore an archived project back on request.
