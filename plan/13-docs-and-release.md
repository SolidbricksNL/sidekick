# Docs and release

**Status:** done except git tag (held by user until Cowork install test)
**Depends on:** 01-structure-validation, 02-skill-prompt-review, 03-settings-and-init-flow, 04-project-model-and-scaffolding, 05-write-disciplines-enforcement, 06-database-discipline, 07-brain-protocol, 08-triage-skill, 09-checkin-skill, 10-archive-skill, 11-interaction-style, 12-manual-test-walkthroughs

## Goal
"Done" means a final docs pass with README accuracy and ARCHITECTURE kept in
sync, a short INSTALL section for installing the plugin in Cowork, a
version/tag bump (`plugin.json` version + matching git tag), and an internal
rollout note for colleagues. Acceptance: README and ARCHITECTURE agree with the
shipped files, and a tagged release exists.

## Context
- `README.md`, `docs/ARCHITECTURE.md`, `.claude-plugin/plugin.json`.
- Everything finalized in plans 01–12 (especially any wording/template changes
  approved along the way).
- This is the last unit; it ships what the earlier plans hardened.

## Tasks
1. [x] **README accuracy pass.** Confirm the one-picture layout, the disciplines
   table, the skills table, and Getting Started all match the shipped skills and
   the finalized templates. Fix drift.
2. [x] **ARCHITECTURE sync.** Update §13 "open items" to reflect what is now
   resolved (init questionnaire wording exists; agenda template finalized) and
   restate what genuinely remains deferred (e.g. `.mcp.json` connector config).
   Apply any design clarifications that the user approved during plans 02–11
   (and ONLY those — ARCHITECTURE stays the source of truth; no silent design
   changes).
3. [x] **INSTALL section.** Write a short, non-technical "Install in Cowork"
   section: how to add the plugin, how to run `/sidekick-init`, how to attach
   `sidekick-triage` as a scheduled task, and which connectors to enable. Place
   it in the README (and/or a dedicated `INSTALL.md`).
4. [x] **Validator hook.** Reference `scripts/validate-structure.*` (plan 01) in
   the README so contributors can re-check structure before release.
5. [x] **Version + tag.** Bump `plugin.json` `version` to **`0.2.0`** and create
   a matching annotated git tag **`v0.2.0`**, then push it.
6. [x] **Internal rollout note.** Write a short note for colleagues: what
   Sidekick is, how to install it in Cowork, the one-time init, the
   three-disciplines mental model, and where to give feedback. Keep it internal
   (the repo is private).
7. [x] **Final consistency check.** Re-run the validator and a quick read-through
   so README ↔ ARCHITECTURE ↔ skills ↔ plugin.json all agree before tagging.

## Resolution (2026-06-01)

- **README accuracy pass (task 1)** — one-picture layout, disciplines table, and
  skills table confirmed against the shipped skills/templates. Replaced the thin
  "Getting started" with a non-technical **Install in Cowork** section and added a
  **For contributors** note. ✓
- **ARCHITECTURE sync (task 2)** — §13 rewritten from "open items" to a **build
  status**: questionnaire wording, agenda template, connectors (no `.mcp.json`),
  SQLite helper, and archive primitive marked resolved; the only remaining item is
  the verify-on-install command form. No silent design changes — only the
  decisions approved across plans 02–12. ✓
- **INSTALL section (task 3)** — lives in the README (kept discoverable rather
  than a separate file): add from GitHub → `/sidekick-init` → enable connectors →
  schedule triage. ✓ (resolves the minor "where INSTALL lives" open question:
  **README section**.)
- **Validator hook (task 4)** — README "For contributors" references
  `node scripts/validate-structure.mjs`. ✓
- **Version (task 5, partial)** — `plugin.json` bumped to **0.2.0** and the
  optional fields added (`license` = `UNLICENSED` for the private repo,
  `homepage`, `repository`, `keywords`). The validator is now fully clean
  (**0 fail, 0 warn**). The annotated **`v0.2.0` git tag + push is HELD** at the
  user's request — to be created after the unit-12 Cowork install test passes.
- **Rollout note (task 6)** — [`docs/ROLLOUT.md`](../docs/ROLLOUT.md): what
  Sidekick is, the three-disciplines mental model, one-time install, and where to
  give feedback. ✓
- **Final consistency check (task 7)** — validator re-run green; README ↔
  ARCHITECTURE ↔ skills ↔ `plugin.json` agree. ✓

**Remaining to fully close 13:** create + push the `v0.2.0` tag (held), which
should follow a green run of `docs/MANUAL-TESTS.md` in Cowork (unit 12 execution).
`license: UNLICENSED` is a conservative default for the private repo — change it
if a different license is intended.

## Acceptance criteria
- README and ARCHITECTURE agree with the shipped files; no stale claims.
- A short INSTALL section/file explains installing in Cowork, init, scheduling
  triage, and enabling connectors.
- `plugin.json` version is bumped and a matching git tag exists and is pushed.
- An internal rollout note exists for colleagues.
- The structure validator passes on the final tree.

## Notes / open questions (version + distribution resolved 2026-06-01)
- **Version target — RESOLVED.** Ship as **0.2.0**. Bump `plugin.json` to
  `0.2.0` and tag `v0.2.0`.
- **Distribution — RESOLVED.** Install from the **private GitHub repo** first
  (add the plugin from GitHub). Later, create an organization plugin; once we're
  happy with it, the GitHub repo can be opened public. The INSTALL section
  documents the from-GitHub install path for now.
- **Where INSTALL lives.** README section vs a separate `INSTALL.md` — pick one;
  a section keeps it discoverable, a file keeps the README lean. (Still open —
  minor.)
