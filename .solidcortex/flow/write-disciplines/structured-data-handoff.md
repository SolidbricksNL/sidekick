---
domains:
  - write-disciplines
edges:
  - label: hand off table create / column change
    to: structured-data/design-table
    via: starts
flowId: write-disciplines
generatedAt: 2026-06-14T11:55:56Z
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generator: solidcortex@0.17.0
kind: derived
mainCodeFile: skills/sidekick-core/references/write-disciplines.md
nodeId: structured-data-handoff
parent: sidekick-core/write-disciplines
related:
  - structured-data/design-table
slug: structured-data-handoff
status: current
summary: The classifier branch that recognizes tabular or repeating-record input as a table and hands off to the structured-data subflow, distilling only the prose insight to brain/.
systems:
  - skills
type: process
---

## TLDR (agent)
**Purpose:** The classifier branch that recognizes tabular / repeating-record input as a table and hands off to the structured-data subflow, keeping only the prose insight for `brain/`.
**Inputs:** A spreadsheet, CSV, exported table, or several same-shaped items (records with recurring fields) arriving via chat.
**Outputs:** A proposed table (handoff to the structured-data subflow); the prose insight distilled to `brain/`; the original filed to `archive/`.
**Code anchor:** [skills/sidekick-core/references/write-disciplines.md](../../../skills/sidekick-core/references/write-disciplines.md)
**Edges:** ← write-disciplines/intent-classifier (parent), → structured-data/design-table (hands off table create / column change)
**Key rules:**
- Tabular or repeating-record input is structured by default — propose a table, don't fold it into a log.
- Rows go to `data/`; only the prose insight goes to `brain/`; the original goes to `archive/`.
- Recognize structured input the moment it arrives, not only when picking where to write.

## Functional (user facing)

### Why use this?
The single failure this branch exists to prevent: a user pastes or shares a clearly tabular thing — a spreadsheet, a list of deals, a roster — and Sidekick folds it into a prose log with a chat summary and no table. That throws away the structure and makes the data un-queryable. This branch catches that input on arrival and treats it as what it is: a table.

### What it does
- Recognizes tabular or repeating-record input — a spreadsheet, CSV, exported table, or a list of same-shaped items — as structured by default.
- Proposes a table as the first response, rather than folding the rows into a log or the brain.
- Hands off the table create / column change to the structured-data subflow.
- Distils the prose *insights* drawn from the data into the brain (under the brain gate).
- Files the original file to `archive/`, and the process is logged.

### What it does not do
This node only *recognizes* and *hands off*. It does not create tables, run queries, snapshot files, or touch the data layer — none of the `data/` mechanics live here. They belong to the sibling structured-data subflow it hands off to.

### Behind the scenes
The classification decision happens the instant input arrives, not later when Sidekick picks where to write. The tell is "several items of the same kind with the same attributes" — employees, clients, deals, risks, each with status/owner/date. One person's background note is brain material; *all* of them with recurring fields is a people table. When it is genuinely unclear, Sidekick asks via the picker rather than guessing.

### Pro tips
- Extend before you add: a new related fact often fits an existing table as a column rather than needing a new table.
- The rows and the insight are two separate writes — the table gets the rows, the brain gets the meaning.

### Related
- [intent-classifier](intent-classifier.md) — routes repeating-record / tabular input here.
- [brain-write](brain-write.md) — receives the distilled prose insight (not the rows).
- structured-data/design-table — the subflow this hands the table create / column change to.

## Technical

**Main code:** `skills/sidekick-core/references/write-disciplines.md` — the "repeating records are data, not brain" rule and the recognize-on-arrival framing; reinforced by `skills/sidekick-core/references/brain-protocol.md` ("Fork on the input's shape first") and `docs/ARCHITECTURE.md` §4 ("Recognizing structured input — classify on arrival"). This node carries **no** data-layer code: `scripts/data.py`, the schema, and snapshots are deliberately out of scope and documented in the `structured-data` subflow.

**Handoff contract.** On recognizing tabular/repeating-record input, this branch emits a `starts` edge to `structured-data/design-table` — a structure change (new table / new column) presented to the user non-technically per the data gatekeeper. The rows themselves are inserted there via `data.py`; only the prose insight is routed back to `brain-write`, and the original source goes to `archive/`.

**Dependencies.** Child of `write-disciplines/intent-classifier`. Outbound `starts` edge into the `structured-data` subflow (`data-structure-change`). Feeds `write-disciplines/brain-write` with the insight-only portion of the input.
