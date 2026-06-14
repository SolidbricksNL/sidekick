---
flowId: project-detection
nodeId: detect-active-project
type: process
slug: detect-active-project
status: current
kind: derived
summary: Every session, list projects/, read each project's agenda and brain index, match chat intent, and pick the explicit-match path or the doubt path.
systems: [skills]
domains: [project-model]
parent: sidekick-core/project-detection
mainCodeFile: skills/sidekick-core/SKILL.md
entry: true
edges:
  - to: project-detection/project-picker
    via: starts
    label: on no match or doubt
  - to: project-detection/scaffold-new-project
    via: starts
    label: explicit new-project intent
  - to: project-detection/setup-subproject-area
    via: starts
    label: explicit area-within-parent intent
  - to: project-detection/route-to-skill
    via: starts
    label: clear specialized intent
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Opens every substantive session by deciding which project the conversation belongs to before any real work happens.
**Inputs:** trigger = session start / first substantive turn; reads = `projects/` listing, each project's `agenda.md` + brain index (the brain files its `CLAUDE.md` names); the user's stated intent.
**Outputs:** an adopted active project (one-line confirmation), or a branch to the picker, the scaffolder, the area setup, or a typed skill. No structural writes from this node itself.
**Code anchor:** [skills/sidekick-core/SKILL.md](../../../skills/sidekick-core/SKILL.md)
**Edges:** → project-detection/project-picker (no match or doubt), → project-detection/scaffold-new-project (explicit new), → project-detection/setup-subproject-area (explicit area), → project-detection/route-to-skill (clear specialized intent)
**Key rules:**
- Only the direct children of `projects/` are projects — never descend into a project's subfolders looking for more.
- Never silently create a project, never silently nest a project, never fall back to an open "which project?" question.
- Case A (explicit) proceeds directly; Case B (doubt) hands off to the picker — nothing structural until the user chooses.
- New-project intent IS approval to scaffold; area intent ("within / part of X") routes to area setup, never a nested project.

## Functional (user facing)

### Why use this?
So you never have to re-explain where you left off. Every time you start talking to Sidekick, it figures out which piece of your work this is about and pulls up that project's context — its agenda and its distilled knowledge — before doing anything. Work, decisions, and files then land in the right place instead of piling up loose.

### What it does
- Runs at the very start of a session, before any real work, because everything Sidekick does belongs to exactly one project.
- Looks over your existing projects and reads each one's running agenda and its index of distilled knowledge, so it has context without asking you to repeat yourself.
- Reads your intent and takes one of a few paths depending on how clear it is.
- When you name an existing project, it simply adopts it and says one line ("Working in *okrs*.") so you know where you are.
- When you clearly ask for something new or for an area inside an existing project, it treats that as your go-ahead and moves to the matching setup step.
- When it is not obvious which project you mean, it does nothing structural and instead offers you a tappable choice.

### When the match is explicit
You named a project, or clearly asked for a new one, or clearly asked for an "area within / part of" an existing one. Sidekick proceeds on that — adopting, scaffolding, or setting up the area — without a confirmation detour.

### When there is doubt
If your intent does not map cleanly to one project, Sidekick will not guess and will not ask an open-ended "what is this about?". It hands off to the picker so you choose from its best guesses plus an escape hatch.

### Behind the scenes
Sidekick treats only the top-level folders under `projects/` as actual projects; the sub-areas living inside a project are covered automatically as part of their parent, so it never mistakes one for a separate project. After a project is settled it reads that project's memory and agenda, and (if output sync is on) pulls the latest deliverables before working.

### Pro tips
- The fastest path is to name the project up front ("let's work on the budget project") — that is the explicit path and skips any picker.
- Phrases like "under", "within", or "part of" an existing project signal an area, not a new project — Sidekick will route accordingly.

### Related
- [project-picker](project-picker.md) — the tappable choice shown on doubt.
- [scaffold-new-project](scaffold-new-project.md) — what happens on a new-project go-ahead.
- [setup-subproject-area](setup-subproject-area.md) — what happens on an area go-ahead.
- [route-to-skill](route-to-skill.md) — handing a specialized request to its typed skill.

## Technical

**Main code locations**
- `skills/sidekick-core/SKILL.md` — the "Project detection" section is the authoritative procedure: list `projects/`, read each project's `agenda.md` and the brain files its `CLAUDE.md` names, then branch on Case A (explicit) vs Case B (doubt). Also the session-start protocol (read settings → determine project → read project `CLAUDE.md`/brain/agenda → `reconcile_output` if sync on → proceed).
- `skills/sidekick-core/references/project-structure.md` — "Detection guard" subsection: enforces that only direct children of `projects/` are enumerated; `brain/<area>/` and `output/<area>/` are areas, not projects.
- `docs/ARCHITECTURE.md` §3.1 — the canonical 6-step detection algorithm and the "never silently" invariants.

**Behavior**
- This node is model-procedure, not executable code — there is no detection script. It runs as instructions inside the always-on `sidekick-core` skill, invoked by the model at session start.
- Case A short-circuits to one of three downstream nodes; Case B produces no structural change and dispatches to `project-picker`.
- The brain index is indirect: a project's `CLAUDE.md` lists the brain files to read at session start; detection reads those rather than globbing `brain/`.

**Dependencies**
- Downstream: `project-detection/project-picker`, `project-detection/scaffold-new-project`, `project-detection/setup-subproject-area`, `project-detection/route-to-skill`.
- Upstream context: the settings read (`sidekick.settings.md`) and the workspace-root `CLAUDE.md` contract gate whether `sidekick-core` acts at all (the surface gate); detection only runs once the plugin is active in a Cowork workspace.
