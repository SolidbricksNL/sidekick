---
flowId: sidekick-checkin
nodeId: checkin-close
type: process
slug: checkin-close
status: current
kind: derived
summary: Closing wrap-up in the chat language — per project what was decided and what's still open plus cross-project flags, log the processed check-in to log/YYYYMMDD-checkin.md, and leave each touched agenda.md clean.
systems: [skills]
domains: [triage-checkin]
parent: main/sidekick-checkin
mainCodeFile: skills/sidekick-checkin/SKILL.md
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Closes the check-in: a short steering wrap-up, a processed-check-in log per touched project, and a cleaned-up agenda.
**Inputs:** trigger: per-project walk + output-sync sweep complete; the decisions made and items left open this session; chat language from settings.
**Outputs:** wrap-up message in the chat language; `log/YYYYMMDD-checkin.md` written per touched project; each touched `agenda.md` left clean for the next check-in.
**Code anchor:** [skills/sidekick-checkin/SKILL.md](../../../skills/sidekick-checkin/SKILL.md)
**Edges:** ← sidekick-checkin/reconcile-output-sync (parent)
**Key rules:**
- The wrap-up is delivered in the chat language and stays a steering summary — not a wall of text; detail lives in logs and agendas.
- What the check-in processed and decided is logged to the project's `log/` as `YYYYMMDD-checkin.md`, written freely.
- Each touched `agenda.md` is updated so the next check-in starts clean.
- Cross-project flags (deadline clusters, a project gone quiet) are called out in the wrap-up.

## Functional (user facing)

### Why use this?
After all the per-project decisions, you want one clear read on where things landed — not a transcript. This closing step gives you a short, steering summary of what was decided and what's still open, flags anything that cuts across projects, and quietly tidies up so the next check-in starts from a clean slate.

### What it does
- Gives a brief wrap-up, per project: what was decided this session and what remains open.
- Points out cross-project signals worth your attention — a cluster of deadlines, or a project that's gone quiet.
- Records what the check-in processed and decided in each project's log, so the session is on the record.
- Cleans up each agenda it touched, so the next check-in begins from an accurate, up-to-date list.

### Behind the scenes
The summary is meant to help you steer, not to re-list everything — the full detail already lives in the per-project logs and agendas this step writes and tidies. The wrap-up is given in whatever language you've set for chatting; the logs and agendas are the durable record left behind.

### Pro tips
- Treat the wrap-up as a dashboard, not a report — if you need specifics, the project's log and agenda hold them.
- A "gone quiet" flag is a useful nudge: it's the check-in noticing nothing has moved, not just nothing being proposed.

### Related
- [reconcile-output-sync](reconcile-output-sync.md) — the output-sync sweep that runs just before the close.
- [per-project-walk](per-project-walk.md) — where the decisions summarised here were made.

## Technical

Implements the "Closing" section of `skills/sidekick-checkin/SKILL.md`. Prompt-only; no script backing.

- **Wrap-up.** Rendered in the **chat language** from `sidekick.settings.md` (ARCHITECTURE §8). Per project: what was decided + what's still open; plus cross-project flags (deadline cluster, a quiet project). Deliberately a steering summary, not a wall of text — the detail lives in the logs/agendas.
- **Check-in log.** What the check-in processed and decided is recorded in each touched project's `log/` as `YYYYMMDD-checkin.md`, written freely (the log layer has no gatekeeper — ARCHITECTURE §6). This is distinct from the distilled-to-brain flow: it is a session record, not a brain write.
- **Agenda cleanup.** Each touched `agenda.md` is updated directly so the next check-in starts clean (agenda is bookkeeping, written freely — ARCHITECTURE §2). The agenda is intentionally simple markdown (a status list) so the check-in can work with it well (ARCHITECTURE §11).

**Dependencies.** Parent `sidekick-checkin/reconcile-output-sync`. Terminal node of the subflow — no outbound edges. Consumes the decisions produced across `sidekick-checkin/per-project-walk` and `sidekick-checkin/distill-log-to-brain`; reads chat language set up in `sidekick-checkin/checkin-entry`'s preconditions.
