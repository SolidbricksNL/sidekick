---
flowId: sidekick-archive
nodeId: select-project
type: process
slug: select-project
status: current
kind: derived
summary: Identify the project to archive — match a named slug or list non-archived projects with a one-line agenda status and ask which, confirming the exact slug before anything moves.
systems: [skills]
domains: [project-model]
parent: main/sidekick-archive
mainCodeFile: skills/sidekick-archive/SKILL.md
entry: true
edges:
  - to: sidekick-archive/confirm-and-collision
    via: starts
    label: slug confirmed
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Resolve which project the user wants archived and lock in its exact slug before any folder is touched.
**Inputs:** `/sidekick-archive` or a phrase like "close out / retire / shelve X"; an optional named project; the `projects/` directory; each project's `agenda.md`.
**Outputs:** A single confirmed slug under `projects/`; control passes to confirm-and-collision. No filesystem change here.
**Code anchor:** [skills/sidekick-archive/SKILL.md](../../../skills/sidekick-archive/SKILL.md)
**Edges:** → sidekick-archive/confirm-and-collision (starts, on slug confirmed)
**Key rules:**
- Gate first: no `sidekick.settings.md` and no cowork MCP tools → say it isn't a Sidekick workspace and stop.
- A named project must be matched to a real slug under `projects/`; never guess.
- If ambiguous or unnamed, list non-archived projects and ask — one numbered option per project.
- Confirm the exact slug before anything moves.

## Functional (user facing)

### Why use this?
This is the front door of archiving. It makes sure the right project is the one that gets moved, so a tidy-up never relocates the wrong harness. You can name the project outright ("archive the Q2 pricing project") or just ask to archive something and let the assistant show you what's available.

### What it does
- Reads your request and looks for a project name in it.
- When you named one, it lines that name up against the projects that actually exist and settles on the precise slug.
- When nothing was named, or the name is ambiguous, it gathers every project that has not already been archived and shows them to you.
- Each project in that list comes with a one-line status pulled straight from its agenda, so you can tell them apart at a glance.
- It asks you to pick, then echoes back the exact slug it intends to act on.

### When the project is named clearly
The assistant matches the name to one slug and moves straight to confirming what will happen — it still names the slug back so a near-miss match is caught before anything moves.

### When the project is unnamed or ambiguous
You get a numbered list of the non-archived projects with their current status, and a question asking which to archive. Picking one settles the slug.

### Behind the scenes
The list is drawn only from live projects — anything already sitting in the archive is left out, so you never see or accidentally re-archive a shelved project. The status line for each comes from that project's own agenda, not a separate index, so it reflects the latest state.

### Pro tips
- Naming the project in your first message skips the list step.
- If you are not sure of the exact name, just ask to archive "a project" — the list will jog your memory and show you the real slugs.

### Related
- sidekick-archive/confirm-and-collision — the next step, where you approve the move and a name clash is handled.

## Technical

Implemented as step 1 of the `sidekick-archive` skill procedure in `skills/sidekick-archive/SKILL.md`; the command shim `commands/sidekick-archive.md` invokes the skill.

Behaviour:
- **Gate.** The skill opens with the Cowork surface gate (blockquote after the H1, restated in the description tail). Outside a Sidekick workspace — no `sidekick.settings.md` and no cowork MCP tools — the skill declines and stops, so selection never runs on a foreign surface.
- **Named match.** A name in the request is resolved against directory entries under `projects/` to a single slug.
- **Listing.** When unnamed/ambiguous, the non-archived projects under `projects/` are enumerated; each one's one-line status is read from its `agenda.md`. Already-archived projects live under `_archive/projects/` and are excluded by construction.
- **Multiple-choice prompt.** Per `skills/sidekick-core/references/interaction-style.md`, the list is presented as numbered options and the user picks one.
- **Confirmation of slug.** The exact slug is echoed and confirmed before control passes on; no rename, copy, or delete happens in this node.

Data/model: operates purely on the project-model folder layout (`projects/<slug>/`, each with its own `agenda.md`) described in `docs/ARCHITECTURE.md` §3.3. Downstream dependency: `sidekick-archive/confirm-and-collision` consumes the confirmed slug.
