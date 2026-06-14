---
flowId: sidekick-status
nodeId: status-entry
type: screen
slug: status-entry
status: current
kind: derived
summary: The /sidekick-status command surface — gates the workspace, reads settings, orchestrates the read-only per-project gather, and prints the short prose overview to chat.
systems: [skills, commands]
domains: [triage-checkin, surface-gate]
parent: main/sidekick-status
mainCodeFile: skills/sidekick-status/SKILL.md
entry: true
edges:
  - to: sidekick-status/gather-per-project
    via: starts
    label: walk each non-archived project
  - to: sidekick-status/read-data-tables
    via: starts
    label: count data/ table rows
  - to: sidekick-status/fetch-calendar
    via: calls
    label: near-term calendar (if connected)
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Entry surface for `/sidekick-status` — gates the workspace, reads settings, runs the read-only per-project gather, and prints one short prose overview.
**Inputs:** `/sidekick-status` command or a status-style question ("where do things stand", "give me an overview"); `sidekick.settings.md`; `projects/` direct children.
**Outputs:** Short prose dashboard in the chat language, two lines max per project; optional `/sidekick-checkin` nudge; nothing written.
**Code anchor:** [skills/sidekick-status/SKILL.md](../../../skills/sidekick-status/SKILL.md)
**Edges:** → sidekick-status/gather-per-project (starts), → sidekick-status/read-data-tables (starts), → sidekick-status/fetch-calendar (calls)
**Key rules:**
- Read-only: writes nothing, distills nothing, proposes nothing, never touches the calendar.
- Gate first — no `sidekick.settings.md` and no Cowork MCP tools means reply "not a Sidekick workspace" and stop.
- No proposal cards and no pickers; it decides nothing.
- Only direct children of `projects/` are projects; never descend into `brain/<area>` or `output/<area>`.
- Missing `sidekick.settings.md` (but in Cowork) points the user to `/sidekick-init`.

## Functional (user facing)

### Why use this?
This is the one-glance dashboard for everything you have in flight. When you ask "where do things stand?" or run the status command, you get a compact picture of every active project at once — open agenda items, how far behind the brain is, when you last checked in, what data you're tracking, and which projects have gone quiet — without anyone touching a file or asking you to make a decision.

### Quick Orientation
- **The gate** — before anything runs, this surface confirms you're in a real Sidekick workspace. Outside Cowork, or with no Sidekick settings present, it simply tells you so and stops.
- **The per-project loop** — it visits each non-archived project in turn and pulls the same handful of facts from each.
- **The summary** — one short prose readout in your chat language, a line or two per project, with cross-project flags called out.

### How to use it
1. Run `/sidekick-status`, or just ask where things stand.
2. It reads your workspace settings (chat language, whether a calendar is connected).
3. It walks every active project and gathers the same set of signals from each.
4. If a calendar is connected, it folds in what's coming up in the next week or two.
5. You get back a scannable summary — and, if action is clearly due, a gentle suggestion to run a check-in.

### Connected screens
- The natural next step when something needs doing is the check-in — see [sidekick-checkin](../sidekick-checkin/_flow.md) (run `/sidekick-checkin`). Status never acts; it points you there.

### Behind the scenes
For each active project the surface kicks off the per-project gather (agenda, undistilled logs, last check-in, staleness) and the data-table read (row counts), and optionally a near-term calendar fetch. It collects all of that and turns it into prose — no cards, no buttons, nothing persisted.

### Pro tips
- Because it changes nothing and needs no approval, you can run it as often as you like — it's safe to spam.
- The detail lives inside each project; treat this as the index, not the full record.
- If it tells you the workspace isn't initialized, run `/sidekick-init` first.

### Related
- [gather-per-project](gather-per-project.md) — the per-project read it drives.
- [read-data-tables](read-data-tables.md) — the data/ row-count read it drives.
- [fetch-calendar](fetch-calendar.md) — the near-term calendar read, when connected.

## Technical

**Main code locations**
- `skills/sidekick-status/SKILL.md` — the whole behaviour: gate blockquote, preconditions (read settings, list `projects/` direct children only, optional calendar), the per-project read spec, output shape, and the read-only boundaries.
- `commands/sidekick-status.md` — the thin `/sidekick-status` command wrapper; its body just invokes the `sidekick-status` skill and restates the four output steps.

**Control flow**
1. Gate check (description tail + `> **Gate:**` blockquote): absence of `sidekick.settings.md` together with no Cowork MCP tools → reply "not a Sidekick workspace" and halt. This mirrors the surface-gate discriminator used across the typed skills.
2. Precondition reads: parse `sidekick.settings.md` for chat language and connected-calendar flag; if absent (but on Cowork), tell the user the workspace isn't initialized and point at `/sidekick-init`.
3. Enumerate `projects/` direct children, excluding `_archive/`. Never recurse — `brain/<area>` and `output/<area>` are subprojects of their parent, not projects.
4. For each project, dispatch the gather-per-project read and the read-data-tables read; optionally fetch-calendar once if a calendar is connected.
5. Render a prose summary in the chat language and, when action is due, append a single `/sidekick-checkin` suggestion.

**Dependencies**
- Downstream nodes: `sidekick-status/gather-per-project`, `sidekick-status/read-data-tables`, `sidekick-status/fetch-calendar`.
- No `data.py` writes, no backup, no gatekeeper — see ARCHITECTURE.md §11b ("The read-only layer"). The data read it triggers shells out to `data.py info` only.
- Cross-flow: hands the user off to the `sidekick-checkin` flow when action is due; shares the surface-gate discriminator with the other typed skills.
