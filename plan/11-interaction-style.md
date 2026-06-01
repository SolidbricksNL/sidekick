# Interaction style

**Status:** not started
**Depends on:** 02-skill-prompt-review

## Goal
"Done" means the plugin-wide multiple-choice principle is consistently
referenced and applied in all five skills, with sensible escape hatches and the
"open questions only for genuinely free-form answers" exception honored. The
acceptance artifact is a **checklist** confirming every user-facing choice point
across all skills offers multiple choice (or is a justified free-form
exception).

## Context
- `ARCHITECTURE.md` §12 (plugin-wide interaction principle).
- `skills/sidekick/references/interaction-style.md` (the rule).
- All five `SKILL.md` files — each must reference and apply it.

## Tasks
1. [ ] Confirm `interaction-style.md` states: 2–4 short mutually-exclusive
   options; always an escape hatch (Something else / None / Not now); plain
   language tied to the user's content, never SQL/jargon; one question at a time
   for consequential choices; multiple choice does not replace the gatekeeper —
   it is how the gatekeeper question is asked; free-form only for names, role,
   reply bodies, and rich typed instructions.
2. [ ] Confirm each skill references the rule:
   - `sidekick` — loads it ("How you ask questions").
   - `sidekick-init` — references it; questionnaire uses multiple choice.
   - `sidekick-triage` — references it for its one interactive choice.
   - `sidekick-checkin` — references it; proposals are Yes/No/Edit.
   - `sidekick-archive` — references it; numbered list + Yes/No.
3. [ ] **Enumerate every user-facing choice point** across all skills and tag
   each: multiple-choice (good) / should-be-multiple-choice (fix) / justified
   free-form (name, role, reply body). Examples to cover: project detection;
   init's seven questions + re-configure prompt + first-project name; triage's
   "run check-in now?"; check-in per-item proposals + new-project handling;
   archive's project pick + confirm.
4. [ ] Flag any choice point currently phrased open-endedly that should be
   multiple choice, and any over-forced multiple choice that should be free-form
   (e.g. don't force buttons on the role or a reply body). Record as proposed
   wording fixes (coordinate with plan 02).
5. [ ] Confirm escape hatches exist wherever the user could be boxed in.
6. [ ] **Build the checklist** (write it into this plan as the artifact): a
   table of every choice point × skill × {multiple choice? / escape hatch? /
   free-form-justified?}.

## Acceptance criteria
- A checklist table exists covering every user-facing choice point in all five
  skills.
- Every consequential choice offers multiple choice with an escape hatch, or is
  a documented free-form exception.
- All five skills reference `interaction-style.md`.
- Any deviation has a concrete proposed fix recorded.

## Notes / open questions
- **Batching approvals.** The rule allows batching quick yes/no items (check-in
  proposals). Confirm the boundary between "batch the quick ones" and "one
  consequential question at a time" is clear enough to apply consistently.
- **Free-form exceptions.** Confirm the agreed free-form set (project name, role,
  reply body, and rich typed instructions) is exhaustive, or extend it.
