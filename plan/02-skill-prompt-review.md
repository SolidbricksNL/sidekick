# Skill prompt review

**Status:** not started
**Depends on:** 01-structure-validation

## Goal
"Done" means every `SKILL.md` has been reviewed *as a prompt* (not as code):
each `description` reliably triggers in the right situations and stays quiet
otherwise; each body is unambiguous about the gatekeeper rules; and there are no
contradictions between a skill and `ARCHITECTURE.md` or between skills. The
output of this unit is a set of concrete, reviewed **edit proposals (diffs)**
captured as tasks here — NOT applied. Special focus: the always-on `sidekick`
skill triggers correctly, and triage's read-only / write-only-to-`_triage`
boundary is airtight in the prompt wording.

## Context
- `ARCHITECTURE.md` is the source of truth; flag real conflicts as open
  questions rather than silently "fixing" them.
- All five `SKILL.md` files and their `references/`.
- Per the build constraints: **do not apply edits to SKILL.md in this pass** —
  every change is written here as a proposed diff for the user to review.

## Tasks
1. [ ] **`sidekick` (always-on) trigger review.** Inspect the `description` for
   reliable activation on "any substantive work conversation" without
   misfiring on trivial chit-chat. Check the phrase coverage (start work, share
   a document, ask for analysis/deliverable, "let's work on X"). Propose
   description tweaks if triggering is too broad or too narrow. Verify the
   session-start protocol order (settings → project detection → read
   CLAUDE.md/brain/agenda → work) is unambiguous.
2. [ ] **`sidekick-init`.** Check the description triggers on `/sidekick-init`,
   missing `sidekick.settings.md`, and "set up / configure" intents. Verify the
   body's questionnaire is internally consistent and that the "records intent,
   does not enable connectors" rule is stated unambiguously.
3. [ ] **`sidekick-triage`.** Hard-audit the safety wording: read-only on
   external sources; writes ONLY to `_triage/`; treats email/message/event
   content as DATA not instructions; never touches a project brain. Confirm the
   prompt makes unattended/scheduled operation safe. Propose stronger wording if
   any boundary is hedged or implicit.
4. [ ] **`sidekick-checkin`.** Verify it is read-only on external sources except
   where the user explicitly approves (drafts replies, never sends unprompted),
   routes each approved action through the correct gatekeeper, and logs what it
   processed. Check for contradictions with the triage boundary.
5. [ ] **`sidekick-archive`.** Verify "move never delete", collision handling,
   restore path, and confirmation wording are unambiguous.
6. [ ] **Cross-skill consistency sweep.** Compare every skill's claims against
   ARCHITECTURE §2–§12 and against each other. Build a short table of any
   contradiction found (skill ↔ architecture, or skill ↔ skill).
7. [ ] **Interaction-style references.** Confirm each skill points at
   `interaction-style.md` correctly and applies multiple-choice consistently
   (this overlaps with plan 11; record findings, defer the full audit there).
8. [ ] For every issue found, write a **proposed diff** in this file's task list
   (old → new wording, with a one-line rationale). Do not edit the SKILL.md.
9. [ ] Mark which proposals are blocked on an open question vs ready to apply.

## Acceptance criteria
- Each of the five skills has a written trigger assessment (too broad / too
  narrow / good) with rationale.
- The triage read-only / write-only-to-`_triage` boundary is confirmed airtight
  in wording, or a concrete strengthening diff is proposed.
- The always-on `sidekick` trigger is confirmed correct or a tuning diff is
  proposed.
- A contradictions table exists (even if empty).
- All proposed edits are captured here as diffs and NONE are applied to
  `SKILL.md` yet.

## Notes / open questions
- **Role-specific skill hook.** `sidekick` says it "may draw on" a role-specific
  skill if present but "never depend on it" — the discovery mechanism is
  unspecified. Likely fine to leave as a soft hook; flag if reviewers want it
  defined.
- **Trigger collisions.** The always-on `sidekick` description is broad by
  design; confirm it does not pre-empt the explicit `/sidekick-*` skills when
  the user invokes those directly.
- **Command namespacing (verify, → plan 12).** In an installed plugin, skill
  commands are namespaced `/sidekick:<skill>` (e.g. `/sidekick:sidekick-init`),
  but every SKILL.md + the README write the bare `/sidekick-init`. Before
  proposing any rewrite of these references, confirm Cowork's actual invocation
  form in a real install (plan 12). If namespacing applies, fixing the
  cross-references is a consistent, mechanical find-replace; if the bare form
  also works, leave them.
- Any skill ↔ ARCHITECTURE conflict found here that is a genuine design
  question (not just wording) must be escalated as an open question to the user,
  not resolved unilaterally.
