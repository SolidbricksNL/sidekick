---
flowId: session-startup
nodeId: load-project-context
type: process
slug: load-project-context
status: current
kind: derived
summary: Determine the active project and read its CLAUDE.md, the brain files it points to, and agenda.md so work begins with full context.
systems: [skills]
domains: [project-model]
parent: sidekick-core/session-startup
mainCodeFile: skills/sidekick-core/SKILL.md
edges:
  - to: session-startup/reconcile-output-sync
    via: calls
    label: if output sync on
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Determine the active project and load its context — `CLAUDE.md`, the brain files it points to, and `agenda.md` — so work begins without the user re-explaining.
**Inputs:** trigger = session start after settings/role; reads `projects/<slug>/` listing, each project's `agenda.md` and brain index, then the chosen project's `CLAUDE.md` + brain files + `agenda.md`; uses chat intent.
**Outputs:** one active project selected and its context loaded; on ambiguity a tappable picker; if output sync is on, calls reconcile next.
**Code anchor:** [skills/sidekick-core/SKILL.md](../../../skills/sidekick-core/SKILL.md)
**Edges:** ← session-startup/read-settings (parent), → session-startup/reconcile-output-sync (calls, if output sync on)
**Key rules:**
- Everything belongs to a project — pick the active project before real work; only direct children of `projects/` are projects.
- Explicit intent → proceed (named project, new project = approval to scaffold, area within a project = area not a nested project).
- Ambiguous → offer a tappable picker of 1–3 likely projects plus "New project"; never an open "which project?", never silently create or nest.

## Functional (user facing)

### Why use this?
Every conversation in Sidekick happens inside a project, so it figures out which one you mean before doing anything — then loads that project's memory, so it already knows the decisions, context, and open items without you repeating them. The work starts grounded instead of cold.

### What it does
- Lists your projects and skims each one's agenda and brain index to understand what exists.
- Reads your intent and picks the active project; on a clear match it confirms in one line ("Working in *okrs*.").
- Loads the chosen project's context: its `CLAUDE.md`, the brain files that file points to, and its `agenda.md`.
- Treats a request for a brand-new project as your approval to set one up, and a strand of work *inside* an existing project as an area, never a new or nested project.

### When it isn't clear which project
Sidekick never asks an open "what is this about?" It puts up a tappable picker — its best guess of one to three likely existing projects, most likely first, plus "New project" and a free-text "Another project — tell me which". Nothing structural happens until you choose. If no project exists yet, it offers just the last two.

### Behind the scenes
Projects are the direct children of a `projects/` folder; a folder nested inside a project is never itself a project. Picking the active project up front is what lets every later action — logging, distilling to the brain, producing output — land in the right place. If output sync is on for the active project, this step hands straight off to a reconcile so work starts from the latest deliverables.

### Pro tips
- Name the project explicitly ("let's work on finance") to skip the picker entirely.
- Say "an area for X in Y" or "part of Y" to get a subproject inside Y rather than a separate project.
- If Sidekick guesses the wrong project, the picker's free-text escape lets you redirect it.

### Related
- session-startup/read-settings — the parent step; role and languages are applied just before this.
- session-startup/reconcile-output-sync — called next when output sync is enabled for the active project.

## Technical

**Backing code.** The "Session-start protocol" (steps 2–3), "Project detection" (Case A / Case B), "Scaffolding a project", and "Subprojects (areas within a project)" sections of `skills/sidekick-core/SKILL.md`. Cross-referenced docs: `references/project-structure.md` (canonical layout), `docs/ARCHITECTURE.md` §3.0–§3.4.

**Detection algorithm.** List `projects/`; read each project's `agenda.md` and brain index (the brain files named in its `CLAUDE.md`). Match chat intent → Case A (explicit: adopt named project, treat new-project request as scaffold approval, treat in-project strand as an area) or Case B (ambiguous: tappable picker of 1–3 best-guess existing projects + "New project" + free-text escape). Invariants: only direct children of `projects/` are projects; never silently create, never fall back to an open question, never nest a project inside another, ask via picker when new-project-vs-area is unclear.

**Context load.** For the chosen project, read its `CLAUDE.md`, the brain files that file references, and `agenda.md`, so the session has full context without the user re-explaining.

**Scaffolding (top-level only).** On approval: create `projects/<slug>/` with `CLAUDE.md` (from `references/project-claude-template.md`), `agenda.md` (from `references/agenda-template.md`), empty `brain/ log/ archive/ output/`; `data/` is lazy; then build the standard dashboard skeleton via the `build_dashboard` tool. An area gets no scaffold — only `brain/<sub>/` + `output/<sub>/` and a `## <sub>` heading in the parent's `agenda.md`.

**Dependencies.** Parent `session-startup/read-settings`. Conditional edge to `session-startup/reconcile-output-sync` (`via: calls`, "if output sync on") — the next protocol step when Output sync is enabled for the active project.
