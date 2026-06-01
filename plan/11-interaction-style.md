# Interaction style

**Status:** done (choice-point checklist complete; no deviations)
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
1. [x] Confirm `interaction-style.md` states: 2–4 short mutually-exclusive
   options; always an escape hatch (Something else / None / Not now); plain
   language tied to the user's content, never SQL/jargon; one question at a time
   for consequential choices; multiple choice does not replace the gatekeeper —
   it is how the gatekeeper question is asked; free-form only for names, role,
   reply bodies, and rich typed instructions.
2. [x] Confirm each skill references the rule:
   - `sidekick` — loads it ("How you ask questions").
   - `sidekick-init` — references it; questionnaire uses multiple choice.
   - `sidekick-triage` — references it for its one interactive choice.
   - `sidekick-checkin` — references it; proposals are Yes/No/Edit.
   - `sidekick-archive` — references it; numbered list + Yes/No.
3. [x] **Enumerate every user-facing choice point** across all skills and tag
   each: multiple-choice (good) / should-be-multiple-choice (fix) / justified
   free-form (name, role, reply body). Examples to cover: project detection;
   init's seven questions + re-configure prompt + first-project name; triage's
   "run check-in now?"; check-in per-item proposals + new-project handling;
   archive's project pick + confirm.
4. [x] Flag any choice point currently phrased open-endedly that should be
   multiple choice, and any over-forced multiple choice that should be free-form
   (e.g. don't force buttons on the role or a reply body). Record as proposed
   wording fixes (coordinate with plan 02).
5. [x] Confirm escape hatches exist wherever the user could be boxed in.
6. [x] **Build the checklist** (write it into this plan as the artifact): a
   table of every choice point × skill × {multiple choice? / escape hatch? /
   free-form-justified?}.

## Resolution (2026-06-01)

### Rule statement (task 1)

`interaction-style.md` states all required elements: 2–4 short mutually-exclusive
options; always an escape hatch (Something else / None / Not now); plain language
tied to the user's content, never SQL/jargon; one question at a time for
consequential choices; multiple choice does **not** replace the gatekeeper — it
is how the gatekeeper question is asked; free-form only for genuinely free-form
answers (name, role, reply body) and when the user is already typing rich
instructions. ✓

### Reference check (task 2)

All five skills reference the rule (paths confirmed resolving in plan 01):
`sidekick` loads it ("How you ask questions"); `sidekick-init`, `sidekick-triage`,
`sidekick-checkin`, `sidekick-archive` each link `../sidekick/references/
interaction-style.md` and apply MC in their bodies. ✓

### Choice-point checklist (tasks 3, 5, 6) — the acceptance artifact

| Skill | Choice point | MC? | Escape hatch | Verdict |
|---|---|---|---|---|
| `sidekick` | project detection (no match / doubt) | ✓ | New project / Something else | good |
| `sidekick` | project detection (clear match) | confirm | implicit correct path | good |
| `sidekick` | new project name | free-form | — | justified (a name) |
| `sidekick` | brain diff approval | ✓ | Not now | good |
| `sidekick` | output create/edit/delete | ✓ | Not now | good |
| `sidekick` | db structure change | ✓ | Explain first / No | good |
| `sidekick-init` | re-configure vs keep (settings exist) | ✓ | Keep | good |
| `sidekick-init` | Q1 role | free-form | — | justified (role) |
| `sidekick-init` | Q2 chat language | ✓ | Other (specify) | good |
| `sidekick-init` | Q3 output language | ✓ | Other (specify) | good |
| `sidekick-init` | Q4 email | ✓ | (Yes/No) | good |
| `sidekick-init` | Q5 messages | ✓ | Other (specify) | good |
| `sidekick-init` | Q6 storage | ✓ | Other (specify) | good |
| `sidekick-init` | Q7 calendar | ✓ | Other (specify) | good |
| `sidekick-init` | first-project name | free-form | — | justified (a name) |
| `sidekick-init` | final confirm before write | ✓ | (re-answer) | good |
| `sidekick-triage` | "Run check-in now?" (interactive) | ✓ | Not now | good |
| `sidekick-checkin` | per-item proposal | ✓ | No / Edit first | good |
| `sidekick-checkin` | unassigned / new project | ✓ | Ignore | good |
| `sidekick-checkin` | reply: draft vs send | ✓ (explicit send) | draft only default | good |
| `sidekick-checkin` | reply body | free-form | — | justified (a body) |
| `sidekick-archive` | which project | ✓ (numbered list) | (cancel) | good |
| `sidekick-archive` | confirm move | ✓ | No | good |
| `sidekick-archive` | restore (if asked) | ✓ | No | good |

### Deviations (task 4)

**None requiring a fix.** Every consequential choice offers multiple choice with
an escape hatch; the three free-form points (project name, role, reply body) are
justified exceptions, not over-forced. No choice point is phrased open-endedly
where MC is warranted, and no MC is forced where free-form is right.

Note: plan 02 **Diff B** (negative-scope clause on the `sidekick` description) was
applied in this batch — it concerns *triggering*, not interaction style, so it
does not affect this checklist.

### Open questions — decided

- **Batching boundary.** `interaction-style.md` is clear enough: batch only quick
  yes/no items (the check-in proposal run); ask one question at a time for
  anything consequential. Applied consistently in the matrix above.
- **Free-form exceptions exhaustive?** The set — **project name, role, reply
  body**, plus the moment the user is already typing rich instructions — is
  exhaustive. A custom "Other" value is captured as free text *within* an MC
  option, so it doesn't need a separate exception.

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
