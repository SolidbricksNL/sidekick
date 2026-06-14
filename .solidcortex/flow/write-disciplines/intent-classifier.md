---
flowId: write-disciplines
nodeId: intent-classifier
type: process
slug: intent-classifier
status: current
kind: derived
summary: The "what is the user trying to do?" router that classifies every write — log, brain, output, or structured data — and asks via the picker when the home is unclear.
systems: [skills]
domains: [write-disciplines]
entry: true
mainCodeFile: skills/sidekick-core/references/write-disciplines.md
edges:
  - to: write-disciplines/log-write
    via: starts
    label: process / draft / notes
  - to: write-disciplines/brain-write
    via: starts
    label: durable fact or decision
  - to: write-disciplines/output-write
    via: starts
    label: finished deliverable
  - to: write-disciplines/structured-data-handoff
    via: starts
    label: repeating records / tabular
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Classifies every prospective write into exactly one of four homes — log, brain, output, or structured data — before any disk write happens.
**Inputs:** Anything Sidekick is about to write; the intent behind the user's message (share data / share knowledge / think together / work the data).
**Outputs:** A routing decision to one of four sibling nodes; or a one-question picker when the home is unclear.
**Code anchor:** [skills/sidekick-core/references/write-disciplines.md](../../../skills/sidekick-core/references/write-disciplines.md)
**Edges:** → write-disciplines/log-write (process/draft), → write-disciplines/brain-write (durable fact), → write-disciplines/output-write (deliverable), → write-disciplines/structured-data-handoff (repeating records)
**Key rules:**
- Classify before writing: log / brain / output / structured data — exactly one home.
- Repeating records of the same kind are a table, never one brain file per item.
- When intent or home is unclear, ASK via the picker — never silently pick.

## Functional (user facing)

### Why use this?
This is the gate that keeps the workspace from sprawling. Cowork's two bad habits are dumping everything in the chat (lost at compaction) or scattering ad-hoc working documents nobody can find again. Before Sidekick writes anything, it stops and decides where that write actually belongs — so the right material ends up in the right place from the start, and the user never has to clean up a mess later.

### What it does
- Reads the **intent** behind the message first — almost everything is one of four things: share data that matters later, share knowledge, think together, or work the data.
- Routes work-in-progress, drafts, and session notes to the **log**.
- Routes a durable fact, decision, or distilled insight to the **brain**.
- Routes a finished deliverable the user asks to keep to **output**.
- Routes a spreadsheet, list, or any repeating same-shaped records to **structured data** as a table.
- Distils the *insight* from shared data into the brain while the rows themselves go to the table — the two are not the same write.

### When the home is unclear
Sidekick does not guess. It asks one short question via the picker — keep it as a tracked table, as distilled notes, or just logged for now. The reasoning: the wrong choice (20 brain files where a table was wanted) is expensive to unpick, and one question is cheaper than an undo.

### Behind the scenes
The classifier is the single decision rule loaded on demand by the core skill. It is pure routing — it performs no write itself; each of the four downstream disciplines carries its own gatekeeper. A common trap it guards against: a person's one-off background note is brain material, but *all* of them with recurring fields (status, owner, date) is a people table.

### Pro tips
- "Several items of the same kind with the same attributes" is the tell for a table, even when it arrives as free chat.
- If you catch yourself about to write a long analysis into the chat, that is a log write — summarize in chat, put the body on disk.

### Related
- [log-write](log-write.md) — the free process home.
- [brain-write](brain-write.md) — the gated memory home.
- [output-write](output-write.md) — the confirmed deliverable home.
- [structured-data-handoff](structured-data-handoff.md) — the table branch.

## Technical

**Main code:** `skills/sidekick-core/references/write-disciplines.md` — the classifier reference: the decision table (log / brain / output / data + gatekeeper per row), the four-intent "what is the user trying to do?" framing, the repeating-records rule, and the ASK-when-unclear rule. Loaded on demand by `skills/sidekick-core/SKILL.md`; no executable backing — the routing is model-applied prose, not a script.

**Decision surface.** Five rows map content shape → home → gatekeeper: process/WIP/draft/notes → `log/` (no gate); durable fact/decision/insight → `brain/` (diff + approval); finished deliverable → `output/` (confirm); structure change (new table/column) → `data/` (confirm in plain language); record fitting existing columns → `data/` (free, via `scripts/data.py`).

**Authoritative cross-refs.** `docs/ARCHITECTURE.md` §2 defines the same four-way split as the plugin's central principle. The structured-data branch only *recognizes* tabular input; the table mechanics (`data.py`, schema, snapshots) live in the sibling `structured-data` subflow, not here.

**Dependencies.** Entry node of the `write-disciplines` flow; fans out to the four sibling `process` nodes (`log-write`, `brain-write`, `output-write`, `structured-data-handoff`) via `starts` edges. Consumed by `sidekick-core` on every prospective write.
