# Settings and init flow

**Status:** done (field spec finalized; template needs no change)
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
1. [x] Walk the seven questions in init against ARCHITECTURE §8 and confirm
   one-to-one mapping to settings fields: Role; Chat language; Default output
   language; Email (Yes/No); Messages (No/Slack/Teams/Google Chat/Other);
   Storage (No/Outlook/Google Drive/Other); Calendar (No/Google/Outlook/Other).
2. [x] Confirm the "ask chat-language first if unknown, then switch" behavior is
   stated and sensible.
3. [x] Confirm the dual-language explanation (chat vs output can differ) appears
   both in the question and in the settings template comments.
4. [x] Confirm the "records intent only; does not enable connectors" rule
   appears in BOTH the init body and the settings template header, with matching
   language.
5. [x] **Finalize the `sidekick.settings.md` field spec** (the acceptance
   artifact): for each field give the exact heading, allowed values, default,
   and an example. Decide and document the exact serialized form for "Other:
   <text>" answers. Record this spec in the "Acceptance criteria" output and, if
   wording changes are needed, as a proposed diff to `settings-template.md`
   (don't apply yet per plan 02 discipline; this plan MAY finalize the template
   if the user approves, since it owns the artifact).
6. [x] Verify first-project scaffolding in init matches the `sidekick` skill's
   scaffolding exactly (same files, same templates, lazy `data.sqlite`,
   creation of root `_triage/` and `_archive/projects/`). Cross-link to plan 04
   for the canonical folder contract.
7. [x] Verify the closing wrap-up covers: what was created; how to schedule
   triage in Cowork; which connectors to enable based on answers; what's next.
8. [x] Resolve the template-location question for init scaffolding (see open
   questions) in coordination with plan 04 — decide duplicate-vs-cross-reference
   and record the decision.

## Finalized field spec (2026-06-01) — the acceptance artifact

`sidekick.settings.md` is written by `/sidekick-init` to the Cowork root and read
by the always-on `sidekick` skill at session start. Verified 1:1 against the
seven init questions and ARCHITECTURE §8. The current `settings-template.md`
already encodes this spec — **no functional change required** (see "Template
verdict" below).

| Field (heading) | Allowed values | Default if user declines | Example serialized | From question |
|---|---|---|---|---|
| `## Role` | Free text | *required* — re-ask, no default | `Managing Director of a software company` | Q1 |
| `Chat language` (under `## Languages`) | English / Nederlands / Deutsch / Français / `Other: <text>` | `English` | `Nederlands` | Q2 |
| `Default output language` (under `## Languages`) | English / Nederlands / Deutsch / Français / `Other: <text>` | `English` (may mirror chat) | `English` | Q3 |
| `Email` (under `## Connections`) | `Yes` / `No` | `No` | `Yes` | Q4 |
| `Messages / chat` | `No` / `Slack` / `Microsoft Teams` / `Google Chat` / `Other: <text>` | `No` | `Slack` | Q5 |
| `Storage` | `No` / `Outlook (OneDrive)` / `Google Drive` / `Other: <text>` | `No` | `Google Drive` | Q6 |
| `Calendar` | `No` / `Google Calendar` / `Outlook Calendar` / `Other: <text>` | `No` | `Outlook Calendar` | Q7 |
| `_Last updated:_` | ISO date `YYYY-MM-DD` | date of write | `2026-06-01` | (auto) |

**"Other" serialization (decided).** For an enumerated pick, write the option
label **verbatim** (`Slack`, `Google Drive`, `No`). For a custom answer, write
`Other: <user text verbatim>` (e.g. `Other: Mattermost`) — the `Other:` prefix
marks it as a non-enumerated value so the reader skill can tell a connector it
recognizes from a free-text one. Never invent a value; never store an empty
field — use the default above if the user declines.

**Connections are intent only.** Every connection value records what the user
*wants*; init never enables a connector. The template's `## Connections` header
states this, matching the init body's "init does not turn any connector on."

**Template verdict (task 5).** `settings-template.md` matches this spec exactly:
headings, the four enumerated connection comments, the dual-language note, and
the intent-only header are all present and correct. The `{{DATE}}` placeholder
resolves to the ISO write date. **No diff proposed** — the template is finalized
as-is.

**Scaffold-parity note (task 6, cross-link plan 04).** Init and the main
`sidekick` skill scaffold a project identically — `CLAUDE.md` +
`agenda.md` from the *same* shared templates (init via
`../sidekick/references/...`, main via `references/...`; both resolve to the same
files per plan 01), empty `brain/ log/ archive/ output/`, lazy `data.sqlite`.
The **only** asymmetry is intentional: init also creates the root system folders
`_triage/` and `_archive/projects/` because it is the setup entry point; the main
skill relies on those being created lazily ("if absent") by triage/archive. Plan
04 owns the canonical folder contract and should record this split.

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
