# Structure validation

**Status:** done
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
1. [x] Confirm the current tree against ARCHITECTURE §12. Expected:
   - `.claude-plugin/plugin.json` and nothing else under `.claude-plugin/`.
   - `skills/<name>/SKILL.md` for all five skills.
   - `skills/sidekick/references/` has exactly: `interaction-style.md`,
     `database-discipline.md`, `brain-protocol.md`, `write-disciplines.md`,
     `project-claude-template.md`, `agenda-template.md`.
   - `skills/sidekick-init/references/settings-template.md`.
   - `skills/sidekick-triage/references/triage-template.md`.
   - `docs/ARCHITECTURE.md`, `README.md`.
2. [x] Validate `plugin.json`: parses as JSON; has `name`, `version`,
   `description`, `author`. Confirm whether Cowork requires any further fields
   (see open questions) and that `name` (`sidekick`) is consistent with the repo
   and the main skill folder.
3. [x] For each `SKILL.md`, parse the YAML frontmatter and check:
   - It has `name` and `description`.
   - `name` exactly equals the parent folder name (`sidekick` →
     `skills/sidekick/`, etc.).
   - `description` is non-empty and within a sane length.
4. [x] Extract every `references/...` (and `../sidekick/references/...`) path
   mentioned in any `SKILL.md` body and confirm each target file exists. Record
   any that resolve across skill boundaries (e.g. init pointing at the
   `sidekick` skill's templates) for plan 03/04 to resolve — see open questions.
5. [x] Check for dead links between skills: every `/sidekick-*` slash command
   referenced in a body corresponds to an existing skill folder.
6. [x] Write `scripts/validate-structure.mjs` (Node, zero-dependency) — or a
   POSIX `scripts/validate-structure.sh` if Node is undesirable — that performs
   tasks 1–5 and prints a PASS/FAIL line per check, exiting non-zero on any
   failure. Keep it dependency-free so it runs anywhere.
7. [x] Add a one-line "how to run the validator" note to `plan/README.md` and
   (later, in plan 13) to the repo README.
8. [x] Run the validator; record the actual output and any failures in the
   "Notes / open questions" section of the relevant downstream plan.

## Acceptance criteria
- A committed `scripts/validate-structure.*` exists and runs clean on a correct
  tree, non-zero on a broken one (verify by temporarily breaking a path).
- `plugin.json` confirmed valid JSON with all Cowork-required fields.
- Every skill folder name matches its frontmatter `name`.
- Every `references/...` path in every `SKILL.md` resolves to a real file, OR
  the unresolved ones are explicitly logged as open questions for plan 03/04.
- No dead `/sidekick-*` command references.

## Execution result (2026-06-01)
- `scripts/validate-structure.mjs` written (Node, zero-dep; Node v24 + Python
  3.11 both confirmed in-env — Node chosen per plan preference).
- Run on the current tree: **PASS, exit 0** — 0 fail, 4 warn. All 4 warns are
  the optional manifest fields (`repository`, `license`, `keywords`, `homepage`)
  intentionally deferred to plan 13. No downstream-blocking failures to log.
- Cross-skill `../sidekick/references/...` reads (init ×3, triage/checkin/archive
  ×1) all resolve — confirms decision 2's no-duplication convention is wired
  correctly on disk.
- Negative test: temporarily renaming `agenda-template.md` produced 3 FAILs and
  **exit 1**, then restored. Acceptance criterion (clean on correct tree,
  non-zero on broken tree) is met.
- Residual (carried, not a failure): the exact USER-typed command form
  (`/sidekick:<skill>` vs bare `/<skill>`) is still verify-on-install — the
  validator LISTS both forms and does not assert either (→ plan 12).

## Notes / open questions (resolved 2026-06-01)
- **Cowork manifest fields — RESOLVED.** Cowork uses the same plugin format as
  Claude Code; only `name` is required. The current `plugin.json` (`name`,
  `version`, `description`, `author{name}`) is **valid as-is** — `author` as an
  object with `name` is the correct shape. Skills are auto-discovered from
  `skills/`; no `skills`/`commands` array is needed. The validator (task 6) should
  assert `name` exists + JSON parses, and may *warn* (not fail) on missing
  optional `repository`/`license`/`keywords` (added at release, plan 13).
- **Slash-command derivation — RESEARCHED; verify-on-install (→ plan 12).** Docs
  say plugin skills are namespaced `/sidekick:<skill>`. Two stale-closed (i.e.
  unconfirmed-fixed) Claude Code bugs muddy this: **#22063** — a `name:` in
  SKILL.md frontmatter strips the prefix, yielding the BARE `/sidekick-init`
  (every Sidekick skill has `name:`, so this predicts the bare form); **#41842** —
  `skills/*/SKILL.md` may not register as `/` commands at all (only `commands/*.md`
  do), though model invocation still works. Cowork-specific behavior is
  undocumented. Net: the always-on `sidekick` skill and every cross-skill
  reference work by MODEL invocation regardless and are not at risk; only the
  exact USER-typed command name is uncertain. The validator should LIST the
  derived command names (so any discrepancy is visible) but must NOT fail on the
  form. Decision deferred to the plan-12 install check; fallback if skills/ don't
  register as commands: add thin `commands/<skill>.md` wrappers. Do not rewrite
  command references until the install check decides.
- **Cross-skill reference reads — RESOLVED.** Templates stay in
  `skills/sidekick/references/`; sibling skills reference them via
  `../sidekick/references/...` (the convention triage/checkin/archive already use
  for `interaction-style.md`). The whole plugin is copied to the cache as one
  unit, so within-plugin `../` paths resolve. Init's two template references were
  fixed to this path **in this pass**. The validator (task 4) should resolve
  `../sidekick/references/...` relative to each SKILL.md and confirm the targets
  exist. Hedge (→ plan 12): if Cowork sandboxes skills per-directory, move shared
  refs to a plugin-root `shared-references/` dir.
