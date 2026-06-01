---
name: sidekick-archive
description: Archive a finished or dormant project. Use when the user runs /sidekick-archive or asks to archive, close out, retire, or shelve a project. Moves the entire project folder from projects/<slug>/ to _archive/projects/<slug>/. Nothing is deleted — archiving is a move, fully reversible. Archived projects no longer participate in project detection, triage, or check-in, but remain consultable. Always confirms which project before moving, and never deletes.
---

# Sidekick — Archive

You archive a project by **moving** its folder. You never delete
anything. Archiving is reversible: it's a relocation, not a removal.

**Ask with multiple choice** — present the project list as numbered
options and the confirmation as Yes / No, per the plugin-wide style in
`../sidekick-core/references/interaction-style.md`.

## Procedure

1. **Identify the project.** If the user named one, match it to a slug
   under `projects/`. If ambiguous or unnamed, list the non-archived
   projects with a one-line status each (from their `agenda.md`) and ask
   which to archive. Confirm the exact slug before doing anything.

2. **Confirm.** State plainly what will happen: *"I'll move the entire
   `<slug>` project — brain, logs, archive, output, database, agenda — to
   `_archive/projects/<slug>/`. Nothing is deleted, and it can be
   restored later. Proceed?"* Wait for a clear yes.

3. **Check for collisions.** If `_archive/projects/<slug>/` already
   exists, don't overwrite. Append a date suffix to the archived copy
   (e.g. `<slug>-archived-YYYYMMDD`) and tell the user.

4. **Move.** Create `_archive/projects/` if absent, then move the whole
   `projects/<slug>/` folder there intact. Prefer a true rename/move. If
   the runtime cannot rename atomically, **copy the folder, verify the
   copy is complete, and only then remove the source** — the source is
   never removed before the copy is verified, so "never delete" holds.

5. **Confirm done.** Tell the user the project is archived and where it
   lives. Note that it will no longer appear in project detection,
   triage, or check-in, but stays available for reference and can be
   restored by moving it back.

## Restoring (if asked)

If the user later wants a project back, move
`_archive/projects/<slug>/` back to `projects/<slug>/` (again checking
for a name collision under `projects/`), and confirm. It rejoins
detection, triage, and check-in automatically.

## Boundaries

- **Never delete.** Not files, not folders, not database rows. Archiving
  is always a move.
- **One project at a time** unless the user explicitly asks to archive
  several; in that case confirm the full list first.
- Do not archive a project mid-task without making sure the current
  session's work has been logged first.
