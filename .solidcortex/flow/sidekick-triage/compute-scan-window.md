---
flowId: sidekick-triage
nodeId: compute-scan-window
type: process
slug: compute-scan-window
status: current
kind: derived
summary: Determine the scan window by reading the run timestamp of the most recent _triage/*-triage.md file, defaulting to the last 7 days when no prior triage file exists.
systems: [skills]
domains: [triage-checkin]
mainCodeFile: skills/sidekick-triage/SKILL.md
entry: true
edges:
  - to: sidekick-triage/scan-email
    via: calls
    label: scan email since window
  - to: sidekick-triage/scan-chat
    via: calls
    label: scan chat since window
  - to: sidekick-triage/scan-calendar
    via: calls
    label: scan calendar since window
  - to: sidekick-triage/count-undistilled-logs
    via: starts
    label: count undistilled logs
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Compute the time window a triage run scans, then fan out to the three source scans and the log count.
**Inputs:** Run trigger (`/sidekick-triage` or scheduled task); `sidekick.settings.md` (connected sources, chat language); existing `_triage/*-triage.md` files.
**Outputs:** A "since" cutoff timestamp; fan-out to scan-email / scan-chat / scan-calendar / count-undistilled-logs.
**Code anchor:** [skills/sidekick-triage/SKILL.md](../../../skills/sidekick-triage/SKILL.md)
**Edges:** → sidekick-triage/scan-email (calls), → sidekick-triage/scan-chat (calls), → sidekick-triage/scan-calendar (calls), → sidekick-triage/count-undistilled-logs (starts)
**Key rules:**
- Window start = run timestamp of the most recent prior `_triage/*-triage.md` (read its `_Run at:_` line / filename), not just the date.
- First-ever run with no prior triage file falls back to a sensible default (e.g. last 7 days).
- All times are local to the workspace.
- If no sources are connected, write a short "nothing to scan" note and stop.

## Functional (user facing)

### Why use this?
This is the first step of every triage run. It works out how far back to look so the scan only surfaces what is genuinely new — you do not re-read the same email or message every time triage fires.

### What it does
- Opens your workspace settings to see which sources (email, messages, calendar) are connected and which language to write headings in.
- Looks for the most recent earlier triage findings file and uses the moment that run happened as the starting line for this scan.
- If this is the very first triage you have ever run, it falls back to a reasonable default look-back of about a week.
- Hands the window to the three source scans and to the undistilled-log count, which then run against that same cutoff.

### When nothing is connected
If your workspace has no email, chat, or calendar connected yet, there is nothing to scan. Triage writes a short note saying so (and that you can enable connectors inside Cowork) and stops there — no empty findings file full of blank sections.

### Behind the scenes
Because the cutoff is a precise timestamp rather than a calendar date, you can safely run triage several times in one day and each run only covers the slice since the previous one. The later check-in then stitches together every triage file written since you last checked in.

### Pro tips
- Running triage twice back-to-back is harmless — the second run finds almost nothing because its window starts where the first one ended.
- The chat language picked up here only affects the findings file headings; quoted snippets from your email or chat stay in their original language.

### Related
- [scan-email](scan-email.md), [scan-chat](scan-chat.md), [scan-calendar](scan-calendar.md) — the three source scans this step launches.
- [count-undistilled-logs](count-undistilled-logs.md) — the per-project log heads-up that runs alongside the scans.
- [write-findings-file](write-findings-file.md) — where all the results land.

## Technical

Implemented entirely as instruction text in `skills/sidekick-triage/SKILL.md` (Preconditions + "What to scan" sections); there is no compiled code — the agent executes the steps. This node is the skill's entry point.

Sequence:
1. Read `sidekick.settings.md` at the Cowork root for connected sources and chat language (Precondition 1). Gate first: absent `sidekick.settings.md` and no cowork MCP tools → declare "not a Sidekick workspace" and halt (the `> **Gate:**` blockquote after the H1).
2. Resolve the window. Enumerate `_triage/*-triage.md`, pick the newest by timestamp, and read the cutoff from its filename (`YYYYMMDD-HHMM`) or its `_Run at:_` line. No prior file → default to ~last 7 days. Times are workspace-local.
3. Early-exit branch: if Precondition 2 holds (no sources connected), write a minimal `_triage/` note and stop — the downstream scan nodes are skipped.
4. Read `projects/` (direct children only — `_archive/` ignored) plus each `agenda.md` summary so the source scans can attribute findings to a likely project (Precondition 3).

Fan-out: drives `scan-email`, `scan-chat`, `scan-calendar` (only for connected sources) and `count-undistilled-logs`, all bounded by the computed cutoff. All four feed `write-findings-file`. The window contract is documented in ARCHITECTURE.md §10 ("Window (supports any cadence)").
