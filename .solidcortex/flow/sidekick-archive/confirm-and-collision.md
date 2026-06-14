---
flowId: sidekick-archive
nodeId: confirm-and-collision
type: process
slug: confirm-and-collision
status: current
kind: derived
summary: State plainly what will move and wait for a clear yes, then check _archive/projects/<slug>/ for a collision and append a date suffix (slug-archived-YYYYMMDD) rather than overwrite.
systems: [skills]
domains: [project-model]
parent: main/sidekick-archive
mainCodeFile: skills/sidekick-archive/SKILL.md
edges:
  - to: sidekick-archive/move-folder
    via: starts
    label: confirmed, no overwrite
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Get an explicit go-ahead for the move, then pick a destination name that never overwrites an existing archive.
**Inputs:** The confirmed slug from select-project; the user's yes/no; the contents of `_archive/projects/`.
**Outputs:** A user-approved decision to proceed plus a collision-safe destination path; control passes to move-folder.
**Code anchor:** [skills/sidekick-archive/SKILL.md](../../../skills/sidekick-archive/SKILL.md)
**Edges:** ← sidekick-archive/select-project (starts, slug confirmed), → sidekick-archive/move-folder (starts, confirmed + no overwrite)
**Key rules:**
- State plainly what moves where and that nothing is deleted, then wait for a clear yes.
- If `_archive/projects/<slug>/` already exists, do not overwrite.
- On a clash, append a date suffix `<slug>-archived-YYYYMMDD` and tell the user.
- Do not archive a mid-task project until the current session's work is logged.

## Functional (user facing)

### Why use this?
This is the checkpoint between deciding and doing. Before a single folder moves, the assistant tells you exactly what is about to happen in plain words and waits for you to say yes. It also quietly protects any project you archived before under the same name, so a new archive never stamps over an old one.

### What it does
- Describes the move in full: the whole project — brain, logs, archive, output, database, agenda — going to its archive location.
- Reassures you that nothing is deleted and the project can be restored later.
- Waits for a clear yes before continuing; anything short of that stops the flow.
- Looks at the archive to see whether a project of the same name was already shelved there.
- When there is a clash, gives the incoming copy a dated name instead of overwriting the old one, and tells you the name it used.

### When you say no (or anything unclear)
Nothing moves. The flow halts at this point — the project stays exactly where it is.

### When an archived project of the same name already exists
The assistant does not overwrite it. The new archive is stored under a name carrying the date it was archived, so both copies survive side by side, and you are told which name the new one got.

### Behind the scenes
The clash check looks specifically at where archives live, so it only triggers on a genuine name collision in the archive — not on the live project itself. The dated suffix uses the archive date, making it easy to tell repeated archives of the same project apart later.

### Pro tips
- Read the move summary before saying yes — it lists everything that travels, including the database and agenda.
- If you archive, change your mind, and re-archive the same project, expect the second copy to carry a date suffix rather than replace the first.
- Make sure the current session's work is logged before archiving a project you are still working in.

### Related
- sidekick-archive/select-project — the previous step, where the slug is chosen.
- sidekick-archive/move-folder — the next step, which performs the actual relocation.

## Technical

Implemented as steps 2 and 3 of the `sidekick-archive` skill procedure in `skills/sidekick-archive/SKILL.md`.

Behaviour:
- **Confirm (step 2).** The skill states the move in plain language — the entire `projects/<slug>/` folder (brain, logs, archive, output, database, agenda) relocating to `_archive/projects/<slug>/`, nothing deleted, restorable — and blocks on a clear yes. The Yes/No prompt follows `skills/sidekick-core/references/interaction-style.md`.
- **Collision check (step 3).** It tests whether `_archive/projects/<slug>/` already exists. If so, the archived copy is named `<slug>-archived-YYYYMMDD` (the archive date) instead of overwriting; the chosen name is surfaced to the user.
- **Boundary.** The skill's Boundaries section forbids archiving a project mid-task before the current session's work is logged; that guard applies before this confirmation lets the flow proceed.

Data/model: reads the `_archive/projects/` layout from `docs/ARCHITECTURE.md` §3.3 (archiving = move to `_archive/projects/<slug>/`, never delete). Upstream: `sidekick-archive/select-project` supplies the confirmed slug. Downstream: `sidekick-archive/move-folder` receives the approval plus the collision-safe destination name and performs the relocation.
