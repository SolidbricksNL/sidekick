# Docs and release

**Status:** not started
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
1. [ ] **README accuracy pass.** Confirm the one-picture layout, the disciplines
   table, the skills table, and Getting Started all match the shipped skills and
   the finalized templates. Fix drift.
2. [ ] **ARCHITECTURE sync.** Update §13 "open items" to reflect what is now
   resolved (init questionnaire wording exists; agenda template finalized) and
   restate what genuinely remains deferred (e.g. `.mcp.json` connector config).
   Apply any design clarifications that the user approved during plans 02–11
   (and ONLY those — ARCHITECTURE stays the source of truth; no silent design
   changes).
3. [ ] **INSTALL section.** Write a short, non-technical "Install in Cowork"
   section: how to add the plugin, how to run `/sidekick-init`, how to attach
   `sidekick-triage` as a scheduled task, and which connectors to enable. Place
   it in the README (and/or a dedicated `INSTALL.md`).
4. [ ] **Validator hook.** Reference `scripts/validate-structure.*` (plan 01) in
   the README so contributors can re-check structure before release.
5. [ ] **Version + tag.** Bump `plugin.json` `version` per semver (decide the
   target, e.g. `0.2.0` for the hardened pre-release or `1.0.0` for first ship).
   Create a matching annotated git tag and push it.
6. [ ] **Internal rollout note.** Write a short note for colleagues: what
   Sidekick is, how to install it in Cowork, the one-time init, the
   three-disciplines mental model, and where to give feedback. Keep it internal
   (the repo is private).
7. [ ] **Final consistency check.** Re-run the validator and a quick read-through
   so README ↔ ARCHITECTURE ↔ skills ↔ plugin.json all agree before tagging.

## Acceptance criteria
- README and ARCHITECTURE agree with the shipped files; no stale claims.
- A short INSTALL section/file explains installing in Cowork, init, scheduling
  triage, and enabling connectors.
- `plugin.json` version is bumped and a matching git tag exists and is pushed.
- An internal rollout note exists for colleagues.
- The structure validator passes on the final tree.

## Notes / open questions
- **Version target.** Decide whether the hardened build ships as `0.2.0`
  (pre-release) or `1.0.0` (first real release). Needs the user's call.
- **Where INSTALL lives.** README section vs a separate `INSTALL.md` — pick one;
  a section keeps it discoverable, a file keeps the README lean.
- **Release mechanism.** Confirm how Cowork plugins are distributed/installed
  internally (a git URL, a marketplace, a zipped artifact). This shapes both the
  INSTALL section and the rollout note. Flag for the user.
