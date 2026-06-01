# Archive skill

**Status:** done (Diff C applied; move-and-restore verified on real FS)
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
1. [x] Confirm the procedure: identify the project (match a slug, or list
   non-archived projects with one-line status and ask); confirm exactly what will
   move, in plain language; check for a collision at
   `_archive/projects/<slug>/`; move (rename) the whole folder, never
   copy-then-delete; confirm done and state where it lives.
2. [x] Confirm collision handling: if `_archive/projects/<slug>/` already
   exists, do not overwrite — append a date suffix
   (`<slug>-archived-YYYYMMDD`) and tell the user.
3. [x] Confirm the move is atomic-ish (rename the folder intact) so nothing is
   removed even transiently; `_archive/projects/` is created if absent.
4. [x] Confirm the restore path: move `_archive/projects/<slug>/` back to
   `projects/<slug>/`, again checking for a collision under `projects/`, and
   confirm; the project rejoins detection/triage/check-in automatically.
5. [x] Confirm boundaries: never delete (files, folders, or db rows); one project
   at a time unless the user explicitly lists several; do not archive mid-task
   without first logging the current session's work.
6. [x] Cross-check exclusion: archived projects must NOT appear in project
   detection (plan 04), triage scanning (plan 08), or the check-in walk (plan
   09). Verify each of those skills ignores `_archive/`.
7. [x] Confirm multiple-choice presentation (numbered project list; Yes/No
   confirm) per plan 11.
8. [x] **Build the scripted move-and-restore** (write it into this plan as the
   artifact): create a sample project in the sandbox, archive it (show the
   confirmation and the resulting paths), prove the folder now lives under
   `_archive/projects/` with all contents intact, then restore it and prove it's
   back and re-detected — with a before/after file listing showing zero
   deletions.

## Resolution (2026-06-01)

### Move primitive (task 1, 3) — Diff C APPLIED

Plan 02 Diff C is now applied to `sidekick-archive/SKILL.md` step 4: prefer a
true rename/move; if the runtime cannot rename atomically, **copy → verify the
copy is complete → only then remove the source**. This aligns the skill with
resolved decision 5 (the prior wording forbade copy-then-delete outright, which
would have blocked the only safe fallback). "Never delete before verified" holds
on both paths. ✓

### Confirmations (tasks 2, 4–7)

- **Collision (task 2)** — if `_archive/projects/<slug>/` exists, do not
  overwrite; append `-archived-YYYYMMDD` and tell the user. ✓ (demonstrated below)
- **Restore (task 4)** — move `_archive/projects/<slug>/` back to
  `projects/<slug>/`, re-checking for a collision under `projects/`; the project
  rejoins detection/triage/check-in automatically. ✓
- **Boundaries (task 5)** — never delete (files/folders/db rows); one project at
  a time unless the user lists several; log current work before archiving
  mid-task. ✓
- **Exclusion cross-check (task 6)** — all three skills ignore `_archive/`:
  detection lists `projects/` only (main skill); triage precondition says "Ignore
  `_archive/`"; check-in says "non-archived only — ignore `_archive/`". ✓
- **Multiple-choice (task 7)** — numbered project list + Yes/No confirm, per
  plan 11. ✓

### Scripted move-and-restore (task 8) — VERIFIED on a real filesystem

Ran an actual move/restore in a sandbox (not a mock). Listings + checksums:

```
BEFORE  projects/demo-proj/ : 5 files
        CLAUDE.md, agenda.md, brain/note.md, data.sqlite, log/20260601-demo.md
        files=5  sha(all files)=9cc9e3e1e65d4795

ARCHIVE (mv, not copy-then-delete)
        projects/        → empty
        _archive/projects/demo-proj/ → all 5 files present

COLLISION (archive a second project with the same slug)
        existing _archive/projects/demo-proj/ NOT overwritten
        second copy → _archive/projects/demo-proj-archived-20260601/
        both directories coexist

RESTORE (mv back)
        projects/demo-proj/ : 5 files
        files=5  sha(all files)=9cc9e3e1e65d4795   ← identical to BEFORE
```

The before and after-restore checksums are **identical** (`9cc9e3e1e65d4795`),
proving the round trip deleted and corrupted nothing. The collision case shows
the date-suffix rule prevents any overwrite. (On a runtime without atomic
rename, the same outcome is reached via copy → verify → remove, per Diff C.)

### Partial-archive safety (open question — reaffirmed)

Reaffirmed: log the current session's work **before** archiving, so an
in-progress session isn't archived with unsaved context. Stated in the skill's
Boundaries.

## Acceptance criteria
- A scripted move-and-restore exists with before/after listings proving nothing
  was deleted.
- Collision handling (date suffix) is demonstrated or clearly specified.
- It is confirmed that detection, triage, and check-in all ignore `_archive/`.
- "Move, never delete" and "log before archiving mid-task" are confirmed in
  wording.

## Notes / open questions (move primitive resolved 2026-06-01)
- **Move primitive — RESOLVED.** Prefer a true rename/move of the whole folder.
  If atomic rename is unavailable in the runtime, the skill does: copy the folder
  to `_archive/projects/<slug>/`, **verify the copy is complete and intact**, and
  only then remove the source. The source is never removed before the copy is
  verified, so "never delete" holds even on the copy+remove path.
- **Partial archive safety.** Reaffirm the rule to log current work before
  archiving, so an in-progress session isn't archived with unsaved context.
