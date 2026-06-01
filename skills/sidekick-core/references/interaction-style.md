# Interaction style — ask with multiple choice

Loaded by the `sidekick` skill and referenced by every other Sidekick
skill. This is a **plugin-wide behavior**, not a one-time setup style.

## The rule

Whenever you put a choice or a question to the user, present it as a
short **multiple-choice** prompt by default — not an open-ended question.
Tapping an option is faster and easier than typing, especially in Cowork
on desktop and mobile.

This applies in every skill, all the time:

- **Project detection** — "Where does this belong?"
  - `core-roadmap` / `client-bpd` / **New project** / Something else
- **Triage follow-up** — for each finding: "What should I do with this?"
  - Update brain / Draft a reply / Add to agenda / Ignore
- **Check-in proposals** — per item: Yes / No / Edit first
- **Archiving** — "Archive which project?" → a numbered list of projects;
  then "Proceed?" → Yes / No
- **Deliverables** — "Create this as…" → Word / Excel / PowerPoint / PDF
- **Database structure** — "You're now tracking deadlines. Add a deadline
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
