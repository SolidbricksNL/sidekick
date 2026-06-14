---
domains:
  - write-disciplines
flowId: write-disciplines
generatedAt: 2026-06-14T11:55:56Z
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generator: solidcortex@0.17.0
kind: derived
mainCodeFile: skills/sidekick-core/references/brain-protocol.md
nodeId: brain-write
parent: sidekick-core/write-disciplines
related:
  - sidekick-checkin/distill-log-to-brain
slug: brain-write
status: current
summary: The gated brain/ write — distil to essence, show a before/after diff, and write the durable fact only after explicit approval, amending existing lines.
systems:
  - skills
type: process
---

## TLDR (agent)
**Purpose:** The gated write discipline — a durable fact, decision, or distilled insight enters `brain/` only after a shown diff is approved.
**Inputs:** A durable fact/decision/insight (often distilled from shared input or a log) routed here by the intent-classifier.
**Outputs:** An approved line or new file in `brain/`; the original source filed to `archive/`.
**Code anchor:** [skills/sidekick-core/references/brain-protocol.md](../../../skills/sidekick-core/references/brain-protocol.md)
**Edges:** ← write-disciplines/intent-classifier (parent / routes durable knowledge here)
**Key rules:**
- Always show a diff first; write only after explicit approval.
- Distil, don't copy — the essence, not the raw text.
- Amend the existing line on a change; never stack a second contradictory version.
- No new brain files without asking.

## Functional (user facing)

### Why use this?
The brain is the project's permanent memory — it is what lets a new session start with full context instead of the user re-explaining everything. Because it is permanent, it is also the most dangerous place to be careless: a wrong fact, a duplicate, or noise written here poisons every future session. The diff-and-approval gate is what keeps that memory trustworthy.

### What it does
- Reads shared input (a document, note, article, report) and extracts the key points — the essence, not the text.
- Adds those points to the right brain file, or updates an existing line.
- Files the original source into `archive/` for reference, keeping the brain lean.
- Presents the proposed change as a plain before/after diff and waits.
- Writes only once the user approves.

### When it is a brand-new file vs an edit
For a brand-new brain file the whole file is the diff — the full proposed content is shown. For an edit, only the changed line(s) are shown as a plain before/after, and the existing line is amended in place. A fact that has changed never gets a second, contradictory line stacked beneath the old one.

### Behind the scenes
The brain is asked in non-technical language tied to the user's content — "Shall I record this in the project brain? Here's the change:" then the diff. Insights captured in a log but not written back inline are not lost: the check-in scans for undistilled logs and folds them in here under the same gate, then stamps the log. Subprojects keep their knowledge in `brain/<sub>/` subfolders, anchored by an `overview.md`.

### Pro tips
- The split between `archive/` and `brain/` is deliberate: archive holds the whole original, brain holds only what must be remembered from it.
- Start with one or two brain files per project; split only once a file grows too large or too broad.
- A brain full of outdated or duplicate lines becomes worthless — keep every file lean and current.

### Related
- [intent-classifier](intent-classifier.md) — routes durable facts and decisions here.
- [log-write](log-write.md) — the process record whose insights are distilled into the brain.
- [structured-data-handoff](structured-data-handoff.md) — for repeating records, only the prose insight comes here; the rows go to a table.

## Technical

**Main code:** `skills/sidekick-core/references/brain-protocol.md` — the per-project memory protocol: the three file layers (memory/log/output/archive), the distillation steps, the four rules for a healthy brain, and the diff+approval gate. Reinforced by `skills/sidekick-core/references/write-disciplines.md` (the "Brain is gated" row) and `docs/ARCHITECTURE.md` §5. No executable backing — brain writes are model file writes into `projects/<slug>/brain/` behind a mandatory approval step.

**The gate.** The diff+approval step is the load-bearing invariant: never write to `brain/` without first showing the change and getting a yes. New-file diff = full proposed content; edit diff = changed line(s) as before/after, amended in place. The same gate is reused by `sidekick-report` for saving/changing a report recipe (ARCHITECTURE §7b) and by the check-in's log write-back loop.

**File organisation.** Typical files: `<topic>.md`, `landscape.md`/`overview.md`, `links.md`, `decisions.md`, `data-model.md`. Areas live as `brain/<sub>/` subfolders anchored by `brain/<sub>/overview.md`. The project `CLAUDE.md` lists which brain files to read at session start.

**Dependencies.** Child of `write-disciplines/intent-classifier`. Receives the prose-insight handoff from `write-disciplines/structured-data-handoff` (table rows are excluded — they route to `data/`). Coupled to the `sidekick-checkin` distil-and-stamp loop that detects undistilled logs.
