# Interaction style — ask with multiple choice

Loaded by the `sidekick` skill and referenced by every other Sidekick
skill. This is a **plugin-wide behavior**, not a one-time setup style.

## The rule

Whenever you put a choice or a question to the user, present it as a
short **multiple-choice** prompt by default — not an open-ended question.
Tapping an option is faster and easier than typing, especially in Cowork
on desktop and mobile.

**Use the interactive question prompt — never a plain text list.** Ask using
Cowork's **interactive, tappable multiple-choice picker** (the same selectable
prompt the `/sidekick-init` questionnaire uses), so the user can click an option.
Do **not** present the choices as a bulleted or numbered list written into the
chat — if the options appear as plain text the user has to type, that is wrong.
Every choice point — project detection, triage follow-up, check-in proposals,
archiving, deliverables, data-structure changes — uses this same interactive picker, so
the experience is identical to setup. When a choice arises, reach for the
question prompt first, by default, without being asked.

**Clickable comes ONLY from the question tool — not from how you format text.**
Writing option-shaped text, "buttons", or styled proposal **cards** into your
message produces dead, unclickable output, however nice it looks. There is no
markdown that makes a tappable button. The *only* way the user gets something to
tap is to actually invoke the interactive question prompt. So: a wall of
proposal cards with "✓ Log / Skip"-style labels you typed yourself is the bug,
not the goal — those don't click. If you want the user to tap a choice, raise it
through the question prompt; if you're just reporting, write prose, not fake
buttons.

This applies in every skill, all the time:

- **Project detection** — when it's unclear, guess **1–3 likely projects** and
  offer them as the picker; never ask openly "what is this about?"
  - `core-roadmap` / `client-bpd` / **New project** / **Another project — tell me which**
- **Triage follow-up** — for each finding: "What should I do with this?"
  - Update brain / Draft a reply / Add to agenda / Ignore
- **Check-in proposals** — drive them *through the question prompt*, **up to 4
  proposals per prompt** (each proposal is one question, options like Yes / No /
  Edit / Skip), then loop for the next batch. Never render the proposals as a
  static list of cards/buttons — that isn't clickable.
- **Archiving** — "Archive which project?" → a numbered list of projects;
  then "Proceed?" → Yes / No
- **Deliverables** — "Create this as…" → Word / Excel / PowerPoint / PDF
- **Data structure** — "You're now tracking deadlines. Add a deadline
  field to the task list?" → Yes / No / Explain first

## How to do it well

- **2–4 options**, short and mutually exclusive. Don't overload.
- Always include a natural escape hatch where relevant: **Something else**,
  **None of these**, or **Not now** — so the user is never boxed in.
- Phrase options in plain language, tied to the user's content — never
  technical jargon or SQL.
- Keep it to **one question at a time** for anything consequential. Only
  batch when the items are quick yes/no approvals (e.g. a list of
  check-in proposals the user can run through fast).
- After a destructive-feeling or durable action (archiving, deleting a
  deliverable, a brain change), still show the diff/summary and get an
  explicit confirmation — the multiple choice doesn't replace the
  gatekeeper, it *is* how you ask the gatekeeper question.

## When NOT to force multiple choice

- When the answer is genuinely free-form (a project name, the user's
  role, the body of a reply). Ask openly there.
- When the user is clearly already typing detailed instructions — don't
  interrupt a rich answer with buttons.

The goal: make the easy path a tap, keep the open path open.
