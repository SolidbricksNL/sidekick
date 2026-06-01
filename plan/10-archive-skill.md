# Archive skill

**Status:** not started
**Depends on:** 04-project-model-and-scaffolding

## Goal
"Done" means archiving is verified to be a MOVE and never a delete, with correct
collision handling, a working restore path, and confirmation that archived
projects drop out of detection, triage, and check-in. The acceptance artifact is
a **scripted move-and-restore** in the sandbox proving nothing is ever deleted.

## Context
- `ARCHITECTURE.md` §3.3 (archiving).
- `skills/sidekick-archive/SKILL.md`.
- Detection/triage/check-in exclusion ties to plans 04, 08, 09.

## Tasks
1. [ ] Confirm the procedure: identify the project (match a slug, or list
   non-archived projects with one-line status and ask); confirm exactly what will
   move, in plain language; check for a collision at
   `_archive/projects/<slug>/`; move (rename) the whole folder, never
   copy-then-delete; confirm done and state where it lives.
2. [ ] Confirm collision handling: if `_archive/projects/<slug>/` already
   exists, do not overwrite — append a date suffix
   (`<slug>-archived-YYYYMMDD`) and tell the user.
3. [ ] Confirm the move is atomic-ish (rename the folder intact) so nothing is
   removed even transiently; `_archive/projects/` is created if absent.
4. [ ] Confirm the restore path: move `_archive/projects/<slug>/` back to
   `projects/<slug>/`, again checking for a collision under `projects/`, and
   confirm; the project rejoins detection/triage/check-in automatically.
5. [ ] Confirm boundaries: never delete (files, folders, or db rows); one project
   at a time unless the user explicitly lists several; do not archive mid-task
   without first logging the current session's work.
6. [ ] Cross-check exclusion: archived projects must NOT appear in project
   detection (plan 04), triage scanning (plan 08), or the check-in walk (plan
   09). Verify each of those skills ignores `_archive/`.
7. [ ] Confirm multiple-choice presentation (numbered project list; Yes/No
   confirm) per plan 11.
8. [ ] **Build the scripted move-and-restore** (write it into this plan as the
   artifact): create a sample project in the sandbox, archive it (show the
   confirmation and the resulting paths), prove the folder now lives under
   `_archive/projects/` with all contents intact, then restore it and prove it's
   back and re-detected — with a before/after file listing showing zero
   deletions.

## Acceptance criteria
- A scripted move-and-restore exists with before/after listings proving nothing
  was deleted.
- Collision handling (date suffix) is demonstrated or clearly specified.
- It is confirmed that detection, triage, and check-in all ignore `_archive/`.
- "Move, never delete" and "log before archiving mid-task" are confirmed in
  wording.

## Notes / open questions
- **Move primitive in Cowork.** Confirm the actual filesystem move available to
  the skill (a `mv`/rename vs a copy+verify+remove). The skill must use a true
  move; if only copy+delete is available, the "never delete" guarantee needs a
  careful sequence (copy, verify, then remove the source only after verified) —
  decide and document.
- **Partial archive safety.** Reaffirm the rule to log current work before
  archiving, so an in-progress session isn't archived with unsaved context.
