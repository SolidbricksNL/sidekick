---
flowId: write-disciplines
nodeId: log-write
type: process
slug: log-write
status: current
kind: derived
summary: The free log/ write — process, drafts, and session notes land on disk with no gatekeeper, summarized in chat rather than the reverse.
systems: [skills]
domains: [write-disciplines]
parent: sidekick-core/write-disciplines
mainCodeFile: skills/sidekick-core/references/write-disciplines.md
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** The free write discipline — process, work-in-progress, drafts, and session notes go to `log/` with no permission step.
**Inputs:** Substantive work, analysis, or session notes routed here by the intent-classifier.
**Outputs:** A markdown file in `log/`, named `YYYYMMDD-<slug>.md`; a short summary in the chat.
**Code anchor:** [skills/sidekick-core/references/write-disciplines.md](../../../skills/sidekick-core/references/write-disciplines.md)
**Edges:** ← write-disciplines/intent-classifier (parent / routes process-and-draft work here)
**Key rules:**
- No gatekeeper — log writes are free; that is the whole point.
- Always log to disk and summarize in chat — never the reverse.
- One file per topic/session; new topic = new dated file, same topic = update existing.

## Functional (user facing)

### Why use this?
The log is the answer to the core problem: work-in-progress ends up either buried in the chat (lost the moment the session compacts) or scattered across ad-hoc documents nobody can find again. The log is the one designated place for that work to land instead. Making it completely friction-free is deliberate — if logging cost a confirmation each time, work would drift back into the chat.

### What it does
- Takes process, work-in-progress, drafts, and session notes and writes them straight to `log/`.
- Names each file with a start date and a slug, e.g. `20260301-research-financial.md`.
- Records the *process*: which documents were handled this session, decisions made, deliverables produced, open points.
- Updates the existing log file for the same topic, or starts a new dated file for a different one.
- Keeps a short summary in the chat — the body lives on disk.

### What it does not do
The log is the workbench, not the memory. Durable conclusions do not stop here — they are written back to the brain (the log records that the work happened; the brain keeps the lasting essence). A log is also not a place to leave a finished deliverable; that is drafted here but promoted to `output/` once approved.

### Behind the scenes
A safety net closes the loop even if the inline write-back to the brain is missed: the check-in scans each project's `log/` for files lacking a `> distilled to brain:` stamp, distils each into the brain (with diff + approval), then stamps the log. So a good logged discussion always gets its chance to reach permanent memory, even sessions later.

### Pro tips
- Think of the chat as the steering wheel and the log as the workbench — short questions and alignment in chat, the actual working in the log.
- A log slug can name a subproject/area (e.g. `20260602-competitor-scan-research.md`) — logs stay shared at the parent-project level.

### Related
- [intent-classifier](intent-classifier.md) — routes process and draft work here.
- [brain-write](brain-write.md) — where a log's durable insights are distilled.
- [output-write](output-write.md) — where an approved deliverable, first drafted in the log, lands.

## Technical

**Main code:** `skills/sidekick-core/references/write-disciplines.md` — the "Log is free" rule and its rationale; the file-naming and one-file-per-topic convention is detailed in `skills/sidekick-core/references/brain-protocol.md` (the log layer) and `docs/ARCHITECTURE.md` §6. No executable backing — log writes are ordinary file writes by the model into `projects/<slug>/log/`.

**File convention.** `YYYYMMDD-<slug>.md`, one per session/topic. A new file is created only when the topic differs from existing logs; otherwise the existing file is appended/updated. Drafts and scratch belong here too — never loose in the project root.

**The distilled-to-brain stamp.** A footer line `> distilled to brain: <date>` marks a log whose durable insights have been folded into the brain. Written only by the check-in (`sidekick-checkin`), never by triage. Its absence is what the check-in scans for; the triage reports only an undistilled-log *count* as a heads-up (§6, §10, §11).

**Dependencies.** Child of `write-disciplines/intent-classifier`. Feeds `write-disciplines/brain-write` indirectly via the check-in write-back loop. Carries no gatekeeper, so it adds no approval surface.
