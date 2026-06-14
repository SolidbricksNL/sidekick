---
domains:
  - write-disciplines
flowId: write-disciplines
generatedAt: 2026-06-14T11:55:56Z
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generator: solidcortex@0.17.0
kind: derived
mainCodeFile: skills/sidekick-core/references/write-disciplines.md
nodeId: output-write
parent: sidekick-core/write-disciplines
related:
  - sidekick-report/live-artifact-wrapper
slug: output-write
status: current
summary: The confirmed output/ write — a finished deliverable is drafted in log/, then promoted to output/ only on a yes, with create / edit / delete each confirmed in plain language.
systems:
  - skills
type: process
---

## TLDR (agent)
**Purpose:** The confirmed write discipline — a finished deliverable enters `output/` only after the user confirms its create, edit, or delete.
**Inputs:** A deliverable the user asks to keep (doc, sheet, deck, PDF), drafted first in `log/` and routed here by the intent-classifier.
**Outputs:** A confirmed file in `output/`, in the default output language; optionally two-way synced to external storage.
**Code anchor:** [skills/sidekick-core/references/write-disciplines.md](../../../skills/sidekick-core/references/write-disciplines.md)
**Edges:** ← write-disciplines/intent-classifier (parent / routes finished deliverables here)
**Key rules:**
- Confirm before every create, edit, or delete in `output/` — never produce one unprompted.
- A deliverable is worked in `log/` and promoted to `output/` only when approved as final.
- `output/` holds final work only — never leave a draft here.

## Functional (user facing)

### Why use this?
Output is where the deliberate, keepable artifacts live — the Word doc, the Excel sheet, the deck, the PDF the user will actually keep or share. Because these are deliberate, Sidekick must never spring one on the user unprompted, and must never overwrite or delete one without a yes. The confirmation step is what makes `output/` a place the user can trust to hold only finished, wanted work.

### What it does
- Takes a deliverable the user has asked to keep and produces it in `output/`.
- Asks for confirmation before every create, edit, or delete — in plain language ("Shall I create a Word document for this in output?"), never technical.
- Generates in the default output language from settings, unless the user requests another.
- Keeps `output/` clean by promoting only final work into it.

### When output sync is on
If the optional output-sync setting is on and a base path is set, `output/` (and the dashboard `artifacts/`) is kept two-way in step with `<base path>/<slug>/output/` on a mounted Drive/OneDrive folder. After each write and at session start / the check-in, Sidekick reconciles — additively, so a delete is never propagated — and a true conflict stops to ask the user via the picker which version to keep. The deliverable itself was already confirmed under this gate, so the sync push adds no extra prompt.

### Behind the scenes
The discipline is paired with the log: a deliverable is drafted and worked in `log/` first, then promoted to `output/` only once the user approves it as final. That is what keeps drafts out of `output/`. The sync, when on, moves plain file copies through a native MCP server — never base64'd through the chat — so the bytes land on the real filesystem the storage client watches.

### Pro tips
- A "working doc" quietly created in `output/` is the classic mistake — it needs confirmation, and it probably belongs in `log/` anyway until it is final.
- To fully remove a synced deliverable, delete it on *both* sides — sync is additive and will otherwise re-create it from the surviving side.

### Related
- [intent-classifier](intent-classifier.md) — routes finished deliverables here.
- [log-write](log-write.md) — where the deliverable is drafted before promotion.
- [brain-write](brain-write.md) — the sibling gated discipline for durable knowledge.

## Technical

**Main code:** `skills/sidekick-core/references/write-disciplines.md` — the "Output is confirmed" rule, the draft-in-log-then-promote rule, and the plain-language gatekeeper tone. The output layer is defined in `docs/ARCHITECTURE.md` §7, and the two-way sync mechanics in §7c (`scripts/sync.py` + the `sidekick-sync` MCP server, `references/sync-discipline.md`). No executable backing for the write itself — it is a confirmed model file write into `projects/<slug>/output/`.

**The gate.** Confirm on create / edit / delete, every time; never unprompted. Distinct from the brain gate (a diff) — output confirmation is a plain yes/no on a deliverable, in the default output language. Combining brain-approval and output-confirm into one "approve & build" prompt is allowed only within the same turn and only if the brain diff is still shown.

**Sync coupling (optional).** When Output sync is on and a base path is reachable, `reconcile_output` runs after a confirmed write and at session start / check-in; conflicts go to `resolve_output` via the picker. Manifest `projects/<slug>/.sidekick/sync.json` holds the baseline. Sync is additive (no delete propagation) and never blocks a local write — failures are reported, not fatal.

**Dependencies.** Child of `write-disciplines/intent-classifier`. Downstream of `log-write` (deliverables are drafted there first). The dashboard `artifacts/` folder rides the same output-sync path (ARCHITECTURE §7b/§7c).
