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
  unprompted, and never overwrite or delete them without a yes.

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
