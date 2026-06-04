# Write disciplines — the decision rule

Loaded on demand by the `sidekick` skill. This is the single rule that
keeps Cowork from sprawling. Before writing **anything**, classify it.

## The rule

> Is this **log**, **brain**, or **output/data**?

| If it is… | It goes to… | Gatekeeper |
|---|---|---|
| Process, work-in-progress, a draft, session notes, an analysis | `log/` | **None — write freely.** |
| A durable fact, decision, or distilled insight | `brain/` | **Show a diff, write only after approval.** |
| A finished deliverable (doc, sheet, deck, PDF) | `output/` | **Confirm before create / edit / delete.** |
| A **structure** change (new table/column) | `data/` | **Confirm in plain language.** |
| A **record** that fits the existing columns | `data/` | **None — insert freely** (via `scripts/data.py`). |

## First: what is the user trying to do?

Before classifying a single write, read the **intent** behind the message. Apart
from the explicit `/sidekick-*` commands, almost everything is one of four:

1. **Share data that will matter later** (figures, a list of records, a
   spreadsheet) → it belongs in **`data/`** as a table (via `data.py`), not as
   prose. Distil any insight into `brain/`; the rows go to the table.
2. **Share knowledge** (context, a decision, how something works — not
   record-shaped) → **`log/`** now, **`brain/`** for the durable distilled version.
3. **Think together** — analysis, advice, sparring over the data/knowledge →
   answer in chat and **log the working in `log/`**; only a deliverable the user
   asks to keep becomes `output/` (drafted in `log/` first).
4. **Work the data** — edit records, query, build/refresh a dashboard view → the
   data layer + `sidekick-report` (dashboards in `dashboard/` + `artifacts/`).

**Repeating records are data, not brain.** When the user gives you several items
of the **same kind** with the **same attributes** — employees, clients, deals,
risks, each with status/owner/date/… — that is a **table**, even when it arrives
as free chat. Propose a table and put the rows in `data/`; do **not** scatter one
brain file per item. (One person's background note = brain; *all* of them with
recurring fields = a `people` table.)

**When the intent or the right home is unclear, ASK** — via the picker — *how
they want it kept*: a tracked **table** (data), distilled **notes** (brain), or
just **logged** for now. Don't silently pick; the wrong choice (e.g. 20 brain
files where a table was wanted) is expensive to unpick. One short question beats a
structure the user has to undo later.

## Why each rule exists

- **Log is free** because the entire problem is that work ends up in the
  chat (lost at compaction) or in scattered ad-hoc documents. The log is
  the designated place for that work to land instead. Making it
  friction-free is the point. Always log to disk and summarize in the
  chat — never the reverse.

- **Brain is gated** because it is permanent memory. Noise, duplication,
  or a wrong fact written here poisons every future session. The diff +
  approval step keeps it trustworthy.

- **Output is confirmed** because deliverables are deliberate artifacts
  the user will keep or share. Sidekick must never produce them
  unprompted, and never overwrite or delete them without a yes. *If the
  optional **output sync** setting is on (and an **Output sync base path** is
  set), `output/` is also kept **two-way** in step with `<base path>/<slug>/
  output/` via the CLI `scripts/sync.py` (plain file copies — never base64 a
  file through the chat): reconcile after each write and at session start / the
  check-in, **additive** (deletes never propagate), a true conflict **asks**
  via the picker. See `references/sync-discipline.md`, ARCHITECTURE §7c.*

- **Data structure is confirmed, records are free** because the user
  approves the *shape* of the data once; after that, records flowing in
  is normal use. Confirming every row would be unworkable. Confirming
  every structure change keeps the data model clean. All data access runs
  through `scripts/data.py` — never a raw read/edit of the JSON files.

## Tone for the gatekeeper questions

Always non-technical, tied to the user's actual content:

- Brain: *"Shall I record this in the project brain? Here's the change:"*
  then the diff.
- Output: *"Shall I create a Word document for this in output?"*
- Data: *"You're now tracking deadlines per task. Shall I add a
  deadline field to the task list?"* — never SQL.

## Default mistakes to avoid

- Writing a long analysis into the chat → put it in `log/`, summarize in
  chat.
- Quietly creating a "working doc" in `output/` → that needs
  confirmation, and probably belongs in `log/` anyway.
- Adding a fact to `brain/` without a diff → always diff first.
- Asking permission to insert each data record → records that fit are
  free.
- Spinning up a new table when an existing one could take a column →
  extend before you add.
- Dropping a file **loose in the project root** → only `CLAUDE.md` + `agenda.md`
  belong there; every other write has a folder (drafts/scratch → `log/`,
  approved deliverables → `output/`, knowledge → `brain/`, data → `data/`,
  dashboards → `dashboard/` + `artifacts/`, machine state → `.sidekick/`). The
  complete map is in `project-structure.md`.
- Leaving a **draft** in `output/` → a deliverable is worked in `log/` and only
  **promoted to `output/` when the user approves it as final**, so `output/`
  stays clean.
