---
flowId: sidekick-checkin
nodeId: per-project-walk
type: process
slug: per-project-walk
status: current
kind: derived
summary: Per non-archived project, read agenda.md and brain index, cross-reference triage and calendar, scan log/ for undistilled logs, and propose concrete gated actions through the interactive picker.
systems: [skills]
domains: [triage-checkin]
parent: main/sidekick-checkin
mainCodeFile: skills/sidekick-checkin/SKILL.md
edges:
  - to: sidekick-checkin/distill-log-to-brain
    via: starts
    label: distill an approved undistilled log
  - to: sidekick-checkin/reconcile-output-sync
    via: calls
    label: reconcile output sync for this project
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** For one project, synthesize agenda + brain + triage + calendar + undistilled-log scan into concrete, gatekeeper-tagged proposals offered through the interactive picker.
**Inputs:** trigger: check-in reaching a project after its data backup; reads `agenda.md`, brain index from `CLAUDE.md`, triage findings tagged to it, related calendar items, and scans `log/` for unstamped files.
**Outputs:** per-item proposals (one question each, ≤4 per prompt) tagged with type + gatekeeper; approved items route onward to distill-log-to-brain and reconcile-output-sync.
**Code anchor:** [skills/sidekick-checkin/SKILL.md](../../../skills/sidekick-checkin/SKILL.md)
**Edges:** ← sidekick-checkin/data-backup (parent), → sidekick-checkin/distill-log-to-brain (starts), → sidekick-checkin/reconcile-output-sync (calls)
**Key rules:**
- Proposals go through the interactive question prompt only — ≤4 per prompt, then loop; self-formatted "cards"/"buttons" are not clickable.
- The check-in is the single place that detects undistilled logs: a file lacking `> distilled to brain:`, skipping any log modified within the last hour (still being written).
- Every proposed change carries its gatekeeper: brain = diff + approval, output/data-structure = confirmation, agenda = free, replies = draft-only unless explicitly told to send.
- Each proposal is tagged with one of eight action types (update brain, distill a log, do an action, create a deliverable, structured data, reply, agenda, calendar).

## Functional (user facing)

### Why use this?
This is the heart of the check-in: for each project it turns the scattered signals — your open agenda items, what the triage flagged, what's on the calendar, and any conversations that landed in the log but were never folded into the brain — into a short list of concrete things you can say yes or no to. You stay in control item by item; nothing happens until you tap a choice.

### What it does
- Reads the project's agenda (open items, what you're waiting on, notes left for next time) and the brain index so it has the project's context.
- Pulls in the triage findings and calendar items that belong to this project, matched by topic and people.
- Scans the project's log for entries whose insights were never written back to the brain, so a good discussion is never quietly lost.
- Works out what's moved, what's stuck, what's new, and what's due — then proposes specific actions for each.

### How proposals reach you
Each proposal arrives as a single tappable question — yes, no, edit first, or skip — with up to four shown at a time before the next batch. A short written summary of what was found is fine, but the actual decisions always come through these tappable prompts, never as a list of styled cards you'd have to act on yourself.

### The kinds of action it proposes
- **Update the brain** with a durable fact or decision (you'll see a diff and approve it).
- **Distill a log** whose insights belong in the brain (diff + approval, then the log gets stamped).
- **Do an action** right now in this session.
- **Create a deliverable** in your output folder (you confirm first).
- **Add or correct structured data** (a brand-new table or column gets a plain-language confirmation first).
- **Reply** to an email or chat — drafted only, never sent unless you explicitly say so.
- **Tick or add an agenda item** — bookkeeping, done freely.
- **Note a calendar commitment** — read-only, the calendar itself isn't touched.

### When a finding looks like a new project
Triage items that don't belong to any existing project are presented together, and you choose whether to start a new project, attach them to an existing one, or ignore them.

### Behind the scenes
Each project's data was already snapshotted just before this walk. As you approve items, they're carried out under their own rules — durable insights become brain entries with your approval, deliverables are confirmed, agenda ticks happen freely, and approved log-distillations and the output-sync sweep are handled by the next steps.

### Pro tips
- "Edit first" lets you reshape a proposal before it's acted on — useful when the gist is right but the wording isn't.
- A log you defer stays unstamped and comes back at the next check-in, so deferring is safe.
- If a project has gone quiet, that often shows up here as an agenda with nothing moving — a cue worth noticing.

### Related
- [data-backup](data-backup.md) — runs just before this walk, per project.
- [distill-log-to-brain](distill-log-to-brain.md) — handles an approved log-distillation and its stamp.
- [reconcile-output-sync](reconcile-output-sync.md) — the per-project output-sync sweep this walk calls.
- [checkin-close](checkin-close.md) — the wrap-up after every project is walked.

## Technical

Implements the "Per-project walk", "Handling new project? findings", and "Acting on approvals" sections of `skills/sidekick-checkin/SKILL.md`. Prompt-only; the model drives the loop.

- **Inputs read per project.** `agenda.md` (open items / waiting-on / notes) and the brain index pointed to by the project `CLAUDE.md` (ARCHITECTURE §5); triage findings tagged to the project (ARCHITECTURE §10); related calendar items by topic/people.
- **Undistilled-log scan (step 4).** Walks `log/` for files lacking the `> distilled to brain:` footer, excluding any file modified within the last hour (treated as still being written). This is the *only* place undistilled logs are detected and processed — the triage merely reports a count so the same log cannot pile up across triage runs (ARCHITECTURE §6, §10). Approved distillations route to `sidekick-checkin/distill-log-to-brain`.
- **Proposal surface.** Each proposal is one question via Cowork's tappable picker (`Yes / No / Edit / Skip`), ≤4 per prompt then loop. Self-rendered cards are non-interactive — this is the plugin-wide interaction style (`skills/sidekick-core/references/interaction-style.md`).
- **Action taxonomy + gatekeepers.** Eight tagged types, each bound to its discipline (ARCHITECTURE §2): brain → diff + approval (then source to `archive/`); distill-log → diff + approval + stamp; output → confirm; structured data → free for existing columns, plain-language confirm for a new table/column (then update `brain/data-model.md`) via `scripts/data.py`; reply → draft-only; agenda → written freely; calendar → read-only note.
- **New-project findings.** Triage's "Unassigned / new project?" group is presented together; the model hands off to the normal project scaffolding (same path as the `sidekick` skill) or attaches to an existing project.

**Dependencies.** Parent `sidekick-checkin/data-backup`. Starts `sidekick-checkin/distill-log-to-brain` for approved undistilled logs; calls `sidekick-checkin/reconcile-output-sync` (the output-sync sweep, gated on settings). Both downstream nodes feed `sidekick-checkin/checkin-close`.
