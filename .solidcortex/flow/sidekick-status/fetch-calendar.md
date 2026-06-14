---
flowId: sidekick-status
nodeId: fetch-calendar
type: integration
slug: fetch-calendar
status: current
kind: derived
summary: When a calendar is connected, fetches near-term upcoming items (next 7–14 days) from the external calendar to surface deadline clusters — read-only.
systems: [skills]
domains: [triage-checkin]
parent: main/sidekick-status
mainCodeFile: skills/sidekick-status/SKILL.md
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** When a calendar is connected, fetch near-term upcoming items from the external calendar so the status summary can flag deadline clusters.
**Inputs:** Connected-calendar flag from `sidekick.settings.md`; a near-term window (next 7–14 days).
**Outputs:** Upcoming calendar items folded into the status prose; nothing written, calendar untouched.
**Code anchor:** [skills/sidekick-status/SKILL.md](../../../skills/sidekick-status/SKILL.md)
**Edges:** ← sidekick-status/status-entry (called by)
**Key rules:**
- Read-only — fetch only; never create, edit, or delete calendar entries.
- Runs only when `sidekick.settings.md` records a connected calendar.
- Scopes the read to the near term (e.g. next 7–14 days).
- Skipped entirely when no calendar is connected.

## Functional (user facing)

### Why use this?
If you've connected a calendar, the status glance can warn you about what's coming up — a deadline cluster this week, a meeting tied to a project you've let go quiet — right alongside the project lines. It turns the status readout from "where things stand internally" into "where things stand, and what's bearing down on you."

### When it runs
Only during a status glance, and only if your workspace settings say a calendar is connected. With no calendar connected, this step is skipped silently and the summary simply has no calendar notes. It is purely on-demand — there's no background polling.

### What it talks to
Your connected external calendar. The status skill asks it for the items in the near term — roughly the next one to two weeks — and reads back what's scheduled. Nothing is sent the other way.

### Behind the scenes
This is a one-way read across an external boundary: the skill requests upcoming items in the near-term window and receives a list of what's on the calendar. Those items are woven into the prose summary (for example, flagged as part of a deadline cluster). No event is created or changed, and nothing about the read is stored in the workspace.

### Pro tips
- The calendar notes are advisory — status surfaces them so you can decide; it never schedules or moves anything.
- If you expect calendar items and see none, check that the calendar is actually recorded as connected in your Sidekick settings.

### Related
- [status-entry](status-entry.md) — the surface that calls this and merges the upcoming items into the summary.

## Technical

**Main code locations**
- `skills/sidekick-status/SKILL.md` — Preconditions item 3 ("If a calendar is connected, fetch upcoming items in the near term (e.g. next 7–14 days). Read-only.") and the output guidance to surface deadline clusters. The connected-calendar flag is read from `sidekick.settings.md` in Preconditions item 1.

**Boundary**
- This is the one external-system touch in the status flow: a connector to the user's calendar (the concrete provider is configured at the workspace/Cowork level, not in this skill). The skill itself only specifies a read of the near-term window; protocol and auth live in the calendar connector.

**Trigger / guard**
- Gated on the connected-calendar flag in `sidekick.settings.md`. Absent flag ⇒ the step is skipped and the summary carries no calendar notes.
- On-demand only — invoked inline during a `/sidekick-status` run; no scheduling or polling.

**Constraints**
- Read-only by contract — the status skill's Boundaries section forbids touching the calendar, so this is fetch-only with no write path, idempotent, and persists nothing (ARCHITECTURE.md §11b).

**Dependencies**
- Upstream: `sidekick-status/status-entry` calls this once, after settings are read, when a calendar is connected.
