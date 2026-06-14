---
flowId: sidekick-archive
nodeId: move-folder
type: process
slug: move-folder
status: current
kind: derived
summary: Move the whole projects/<slug>/ folder into _archive/projects/ via the archive primitive — true rename, else copy then verify then remove source (never delete before verified) — then confirm it has left detection, triage, and check-in.
systems: [skills]
domains: [project-model]
parent: main/sidekick-archive
mainCodeFile: skills/sidekick-archive/SKILL.md
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Relocate the whole project folder into the archive safely, then confirm it has dropped out of the live loop.
**Inputs:** The approved move and collision-safe destination from confirm-and-collision; the source `projects/<slug>/` folder.
**Outputs:** The project folder living under `_archive/projects/`; a done message stating where it is and how to restore it.
**Code anchor:** [skills/sidekick-archive/SKILL.md](../../../skills/sidekick-archive/SKILL.md)
**Edges:** ← sidekick-archive/confirm-and-collision (starts, confirmed + no overwrite)
**Key rules:**
- Create `_archive/projects/` if absent, then move the whole `projects/<slug>/` folder intact.
- Prefer a true rename/move.
- If the runtime cannot rename atomically: copy, verify the copy is complete, then remove the source.
- Never remove the source before the copy is verified — "never delete" must hold.

## Functional (user facing)

### Why use this?
This is the step that actually moves your project into the archive — the whole harness in one piece, done in a way that cannot lose your work even if something interrupts it. When it finishes, the project is safely tucked away and out of your daily view, but still there whenever you want it.

### What it does
- Makes sure the archive area exists, then relocates the entire project folder into it as a single intact unit.
- Tries the clean, instant move first.
- If a clean move is not possible, it copies everything across, checks the copy really is complete, and only then clears the original.
- Confirms the project is archived and tells you exactly where it now lives.
- Reminds you that the project no longer shows up in detection, triage, or check-in, but is still there to consult and can be restored by moving it back.

### When a clean move is not possible
Some setups cannot rename a folder in one atomic step. In that case the assistant takes the careful route: copy first, confirm the copy is whole, and remove the original last. Your original is never cleared until its copy is verified, so an interrupted archive can never leave you with nothing.

### Behind the scenes
After the move, the project sits outside the live project area, which is why the regular sweeps no longer pick it up. Nothing about its contents changes — brain, logs, output, database, and agenda travel together — so restoring it later is just the same move in reverse, and it rejoins the loops automatically.

### Pro tips
- The whole folder travels as one unit; you do not lose history, data, or deliverables by archiving.
- To bring a project back, ask to restore it — it returns to the live area and starts appearing in detection, triage, and check-in again.
- Archiving frees your workspace from clutter without ever putting your data at risk.

### Related
- sidekick-archive/confirm-and-collision — the previous step, which approves the move and resolves a name clash.
- sidekick-archive/select-project — the start of the flow, where the project is chosen.

## Technical

Implemented as steps 4 and 5 of the `sidekick-archive` skill procedure in `skills/sidekick-archive/SKILL.md`.

Behaviour:
- **Move (step 4).** Ensures `_archive/projects/` exists, then relocates the whole `projects/<slug>/` folder there. The **archive move primitive** prefers a true rename/move; when the runtime cannot rename atomically it falls back to copy → verify → remove source. The source is never removed before the copy is verified, which is how the skill's "never delete" invariant holds (`docs/ARCHITECTURE.md`: "Archive move primitive — true rename/move, else copy → verify → remove; never delete before verified").
- **Confirm done (step 5).** Reports the archived location and notes the project drops out of project detection, triage, and check-in but stays consultable and restorable.
- **Restore path.** The skill's Restoring section reverses the move (`_archive/projects/<slug>/` → `projects/<slug>/`, re-checking for a collision under `projects/`); the project then automatically rejoins detection, triage, and check-in.

Data/model: per `docs/ARCHITECTURE.md` §3.3, archiving is a move to `_archive/projects/<slug>/` with nothing deleted; archived projects are excluded from the live cross-project loops by virtue of living outside `projects/`. Upstream: `sidekick-archive/confirm-and-collision` supplies the approval and the collision-safe destination. This node is the terminal step of the subflow.
