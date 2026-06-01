# Settings and init flow

**Status:** not started
**Depends on:** 01-structure-validation, 02-skill-prompt-review

## Goal
"Done" means the init questionnaire is validated end to end and the
`sidekick.settings.md` field spec is finalized as the acceptance artifact: the
multiple-choice questions, the exact fields written, the dual-language handling
(chat language vs default output language), the "init records intent but does
not enable connectors" rule, first-project scaffolding, and the closing
explanation about scheduling triage and enabling connectors are all consistent
across the init skill, the settings template, and ARCHITECTURE §8.

## Context
- `ARCHITECTURE.md` §8 (settings layer) and §13 (open item: questionnaire
  wording).
- `skills/sidekick-init/SKILL.md` (the questionnaire + scaffolding + closing).
- `skills/sidekick-init/references/settings-template.md` (the file shape).
- The `sidekick` skill reads this settings file at session start (plan 02).

## Tasks
1. [ ] Walk the seven questions in init against ARCHITECTURE §8 and confirm
   one-to-one mapping to settings fields: Role; Chat language; Default output
   language; Email (Yes/No); Messages (No/Slack/Teams/Google Chat/Other);
   Storage (No/Outlook/Google Drive/Other); Calendar (No/Google/Outlook/Other).
2. [ ] Confirm the "ask chat-language first if unknown, then switch" behavior is
   stated and sensible.
3. [ ] Confirm the dual-language explanation (chat vs output can differ) appears
   both in the question and in the settings template comments.
4. [ ] Confirm the "records intent only; does not enable connectors" rule
   appears in BOTH the init body and the settings template header, with matching
   language.
5. [ ] **Finalize the `sidekick.settings.md` field spec** (the acceptance
   artifact): for each field give the exact heading, allowed values, default,
   and an example. Decide and document the exact serialized form for "Other:
   <text>" answers. Record this spec in the "Acceptance criteria" output and, if
   wording changes are needed, as a proposed diff to `settings-template.md`
   (don't apply yet per plan 02 discipline; this plan MAY finalize the template
   if the user approves, since it owns the artifact).
6. [ ] Verify first-project scaffolding in init matches the `sidekick` skill's
   scaffolding exactly (same files, same templates, lazy `data.sqlite`,
   creation of root `_triage/` and `_archive/projects/`). Cross-link to plan 04
   for the canonical folder contract.
7. [ ] Verify the closing wrap-up covers: what was created; how to schedule
   triage in Cowork; which connectors to enable based on answers; what's next.
8. [ ] Resolve the template-location question for init scaffolding (see open
   questions) in coordination with plan 04 — decide duplicate-vs-cross-reference
   and record the decision.

## Acceptance criteria
- A single, finalized `sidekick.settings.md` field spec is written down here
  (headings, allowed values, defaults, examples, "Other" serialization).
- The init questionnaire maps 1:1 to that spec with no orphan fields.
- Dual-language separation is explicit in question, template, and ARCHITECTURE.
- "Records intent, does not enable connectors" appears consistently in init body
  + settings template.
- First-project scaffolding in init is confirmed identical to the canonical
  contract in plan 04.

## Notes / open questions (resolved 2026-06-01)
- **Where init reads its scaffold templates — RESOLVED.** Init seeds `CLAUDE.md`
  and `agenda.md` from `../sidekick/references/project-claude-template.md` and
  `../sidekick/references/agenda-template.md` — no duplication. The init SKILL.md
  was fixed to these paths in this pass (it previously pointed at non-existent
  `references/...` paths). (Shared with plan 01 + plan 04.)
- **Connectors — RESOLVED.** The user installs/enables connectors in Cowork
  themselves. Init only **records intent** and, in the closing wrap-up,
  **guides** the user to enable the connectors they said yes to. Init never
  enables anything and never writes a `.mcp.json`. (Shared with plan 08.)
- **ARCHITECTURE §13 sync — RESOLVED (yes).** §13 will be updated in plan 13 to
  mark the questionnaire wording and agenda template as done, and to drop the
  `.mcp.json` auto-config item (superseded by the connectors decision above).
  Defer the actual edit to the plan 13 docs pass.
