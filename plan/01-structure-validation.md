# Structure validation

**Status:** not started
**Depends on:** none

## Goal
"Done" means the plugin's on-disk structure is provably correct for Claude
Cowork: `plugin.json` is valid JSON with all fields Cowork requires; the folder
layout matches `docs/ARCHITECTURE.md` §12; only `plugin.json` lives inside
`.claude-plugin/`; every skill has valid YAML frontmatter whose `name` matches
its folder; every `references/...` path mentioned in any `SKILL.md` resolves to
a real file; and there are no dead cross-skill links. A re-runnable validation
script under `scripts/` reports all of this automatically and exits non-zero on
any failure.

## Context
- `docs/ARCHITECTURE.md` §12 (plugin structure) is the authoritative layout.
- `.claude-plugin/plugin.json` — manifest.
- All five skills: `skills/sidekick/`, `skills/sidekick-init/`,
  `skills/sidekick-triage/`, `skills/sidekick-checkin/`,
  `skills/sidekick-archive/`.
- Reference files under `skills/sidekick/references/` (6 files),
  `skills/sidekick-init/references/settings-template.md`,
  `skills/sidekick-triage/references/triage-template.md`.
- This plan is purely verification + a checker script. It does NOT fix issues it
  finds — it records them; fixes belong to the targeted plans (02, 03, 04…).

## Tasks
1. [ ] Confirm the current tree against ARCHITECTURE §12. Expected:
   - `.claude-plugin/plugin.json` and nothing else under `.claude-plugin/`.
   - `skills/<name>/SKILL.md` for all five skills.
   - `skills/sidekick/references/` has exactly: `interaction-style.md`,
     `database-discipline.md`, `brain-protocol.md`, `write-disciplines.md`,
     `project-claude-template.md`, `agenda-template.md`.
   - `skills/sidekick-init/references/settings-template.md`.
   - `skills/sidekick-triage/references/triage-template.md`.
   - `docs/ARCHITECTURE.md`, `README.md`.
2. [ ] Validate `plugin.json`: parses as JSON; has `name`, `version`,
   `description`, `author`. Confirm whether Cowork requires any further fields
   (see open questions) and that `name` (`sidekick`) is consistent with the repo
   and the main skill folder.
3. [ ] For each `SKILL.md`, parse the YAML frontmatter and check:
   - It has `name` and `description`.
   - `name` exactly equals the parent folder name (`sidekick` →
     `skills/sidekick/`, etc.).
   - `description` is non-empty and within a sane length.
4. [ ] Extract every `references/...` (and `../sidekick/references/...`) path
   mentioned in any `SKILL.md` body and confirm each target file exists. Record
   any that resolve across skill boundaries (e.g. init pointing at the
   `sidekick` skill's templates) for plan 03/04 to resolve — see open questions.
5. [ ] Check for dead links between skills: every `/sidekick-*` slash command
   referenced in a body corresponds to an existing skill folder.
6. [ ] Write `scripts/validate-structure.mjs` (Node, zero-dependency) — or a
   POSIX `scripts/validate-structure.sh` if Node is undesirable — that performs
   tasks 1–5 and prints a PASS/FAIL line per check, exiting non-zero on any
   failure. Keep it dependency-free so it runs anywhere.
7. [ ] Add a one-line "how to run the validator" note to `plan/README.md` and
   (later, in plan 13) to the repo README.
8. [ ] Run the validator; record the actual output and any failures in the
   "Notes / open questions" section of the relevant downstream plan.

## Acceptance criteria
- A committed `scripts/validate-structure.*` exists and runs clean on a correct
  tree, non-zero on a broken one (verify by temporarily breaking a path).
- `plugin.json` confirmed valid JSON with all Cowork-required fields.
- Every skill folder name matches its frontmatter `name`.
- Every `references/...` path in every `SKILL.md` resolves to a real file, OR
  the unresolved ones are explicitly logged as open questions for plan 03/04.
- No dead `/sidekick-*` command references.

## Notes / open questions
- **Cowork manifest required fields.** Current `plugin.json` has `name`,
  `version`, `description`, `author{name}`. Unconfirmed whether Cowork also
  wants e.g. `license`, `homepage`, a `skills`/`commands` array, or an icon.
  ARCHITECTURE says only `plugin.json` lives in `.claude-plugin/` and implies
  skills are auto-discovered from `skills/`. **Needs confirmation against the
  current Cowork plugin spec before we call the manifest "valid".**
- **Cross-skill reference reads.** `skills/sidekick-init/SKILL.md` instructs the
  init skill to scaffold from `references/project-claude-template.md` and
  `references/agenda-template.md`, but those templates physically live in
  `skills/sidekick/references/`, not under `sidekick-init/`. Two unknowns: (a)
  can a Cowork skill read a *sibling* skill's reference files at runtime? (b) the
  `agenda-template.md` mention in init has no "(in the sidekick skill)" qualifier,
  so the literal path `sidekick-init/references/agenda-template.md` does not
  exist — a likely dead link. Resolution options (duplicate the templates into
  init, or rely on cross-skill paths) are decided in plan 03/04; this plan only
  flags it.
- **Slash-command declaration.** Confirm whether `/sidekick-init` etc. are
  auto-derived from skill names or need explicit declaration in `plugin.json`.
