# Root-hygiene guard

Defense-in-depth against the root-leak failure mode (ARCHITECTURE §3.0b): a
cheap, after-the-fact scan that catches anything written **loose to the
workspace root** despite the always-on contract — e.g. a document skill
(`pptx`/`docx`/`xlsx`/`pdf`) that defaulted to the selected-folder root, or a
stray note/script/draft.

This is a **backstop, not the primary defence.** Prevention lives in the root
`CLAUDE.md` override + project detection. This guard only mops up what slips
past.

## What belongs in the workspace root (everything else is "stray")

The root holds **exactly**:

- **Files:** `sidekick.settings.md` and `CLAUDE.md`. Nothing else.
- **Folders:** `projects/`, `_triage/`, `_archive/`. Nothing else.

Anything else loose in the root — a `*.pptx`/`*.docx`/`*.xlsx`/`*.pdf`, a `*.md`
note, a `*.py` script, a data file, an extra folder — is **stray** and should be
relocated into the project it belongs to (or removed by the user).

> Cowork housekeeping files the host itself manages (e.g. a `.git/` if present,
> OS files like `.DS_Store`/`Thumbs.db`) are **not** Sidekick's to move — ignore
> them, don't report them as strays.

## The scan

At the relevant moment (see "Where this runs"), list the **top level** of the
workspace root only — do **not** recurse into `projects/` (everything under a
project is already in its place). Collect every entry that is not in the
allow-list above. If there are none, the root is clean — say nothing (or, in
status, a one-line "root clean").

## Acting on strays — report vs. relocate (per skill contract)

Two behaviours, chosen by whether the running skill is allowed to act:

- **Read-only skills (`/sidekick-status`, `/sidekick-triage`) → REPORT only.**
  Surface the strays as a flag ("2 files loose in the root:
  `Sidekick-Overview.pptx`, `notes.md` — these belong in a project; run
  `/sidekick-checkin` to relocate"). Triage writes the flag into its `_triage/`
  findings file; status notes it in its prose summary. Neither moves anything.

- **Acting skills (`sidekick-core` session-start, `/sidekick-checkin`) → OFFER
  relocation.** Present a **tappable** choice per stray (or grouped when they
  clearly share a home):
  1. Pick the destination **project** — best-guess existing projects first, plus
     "New project" and "Leave it" (and a free-text "another project").
  2. Pick the destination **discipline within that project**:
     - a finished **deliverable** (deck, doc, sheet, PDF) → `output/`
       (confirm, per Discipline 3);
     - a **draft / scratch / note / script** → `log/` (free write).
  3. **Move** it there (true move/rename; verify the copy before removing the
     original — same primitive as archiving). Then log one line in that
     project's `log/` recording the relocation.

## Hard rules

- **Never delete.** A stray is relocated, or left in place if the user declines
  — never removed. (If the user wants it gone, that is their explicit call.)
- **Never guess the destination silently.** Unclear home → ask via the picker.
- **Don't touch host/OS housekeeping files** (see note above).
- **Don't recurse into `projects/`** — a file already under a project is not a
  root stray.
- Keep it cheap: one top-level listing, no deep walk, skip silently when the
  root is clean.

## Where this runs

| Surface | Behaviour |
|---|---|
| `sidekick-core` session-start (step 6) | Scan after project detection; **offer relocation** if strays found. |
| `/sidekick-status` | **Report** strays as a cross-project flag (read-only). |
| `/sidekick-checkin` | **Offer relocation** alongside the per-project proposals. |
| `/sidekick-triage` | **Report** a stray-root count/list in the `_triage/` file (write-only to `_triage/`). |
