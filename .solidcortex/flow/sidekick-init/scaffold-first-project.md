---
domains:
  - onboarding
  - project-model
flowId: sidekick-init
generatedAt: 2026-06-14T11:55:56Z
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generator: solidcortex@0.17.0
kind: derived
mainCodeFile: skills/sidekick-init/SKILL.md
nodeId: scaffold-first-project
parent: main/sidekick-init
related:
  - project-detection/scaffold-new-project
slug: scaffold-first-project
status: current
summary: Scaffolds the first project under projects/<slug>/ with its CLAUDE.md, agenda.md, core folders, and empty dashboard skeleton, plus the workspace-level _triage/ and _archive/ folders.
systems:
  - skills
  - mcp-server
type: process
---

## TLDR (agent)
**Purpose:** Roll out the project structure by scaffolding one first project plus the workspace-level system folders, so the layout exists immediately after setup.
**Inputs:** a project name from the user → derived kebab-case slug; the project templates and `references/project-structure.md`; the `build_dashboard` MCP tool.
**Outputs:** `projects/<slug>/` with `CLAUDE.md`, `agenda.md`, empty `brain/`/`log/`/`archive/`/`output/`, an empty dashboard skeleton, and root-level `_triage/` + `_archive/projects/`.
**Code anchor:** [skills/sidekick-init/SKILL.md](../../../skills/sidekick-init/SKILL.md)
**Edges:** (none)
**Key rules:**
- Create exactly one top-level project (a direct child of `projects/`); never nested subprojects or areas during init.
- Only `CLAUDE.md` + `agenda.md` sit loose in the project root; `data/` and `.sidekick/` are lazy (first table / first registry write).
- The empty dashboard skeleton is built by the `build_dashboard` MCP tool, not hand-written.
- `_triage/` and `_archive/projects/` are workspace-level, not inside any project.

## Functional (user facing)

### Why use this?
Setup isn't finished until you have somewhere to work. This step creates your first real project with everything in place — a place for notes, a place for finished deliverables, an agenda, and a ready-to-fill dashboard — so you can start working the moment setup ends.

### How to use it
1. Give your first project a short name when asked. Sidekick turns it into a tidy folder name for you.
2. Sidekick builds the project folder with its own rules file, an agenda, and empty areas for working notes, distilled knowledge, an archive, and deliverables.
3. A blank dashboard is prepared for the project so you can populate it later.
4. Two workspace-wide folders are also created behind the scenes: one where the scheduled triage drops its findings, and one for archived projects.

### What it does
- Creates a single project as a direct child of your projects area.
- Fills it with a project rules file (named after your project), an agenda, and empty folders for working notes, knowledge, archive, and deliverables.
- Prepares an empty dashboard skeleton for the project.
- Creates the workspace-level triage and archive folders if they don't exist yet.

### One project, not a tree
Init makes exactly one top-level project. It never nests projects inside projects. Later, when you want a separate strand of work within a project, Sidekick adds it as an area inside that project — not as a new project.

### What's deferred
A project's data store and its internal bookkeeping folder don't appear until they're first needed — the data store on your first table, the bookkeeping folder on the first time something is registered. So a fresh project looks deliberately lean.

### Behind the scenes
The dashboard skeleton is produced natively rather than typed out, which keeps it correct and self-contained from the start. The agenda and rules file come from standard templates with your project name filled in.

### Pro tips
- Keep the first project name short and concrete; the folder name is derived from it.
- You don't need to set up data or dashboards now — they fill in as you work.

### Related
- [sidekick-init/write-workspace-claude](write-workspace-claude.md) — the workspace rules that govern where work in this project goes.

## Technical

**Main code locations**
- `skills/sidekick-init/SKILL.md` — "Scaffolding the first project" section: ask name → derive kebab-case slug → scaffold `projects/<slug>/` per the complete layout, call `build_dashboard`, then create root-level `_triage/` and `_archive/projects/`.
- `skills/sidekick-core/references/project-structure.md` — canonical "complete project layout" (the single source of truth for the 2-root-files + 8-folders shape).
- `skills/sidekick-core/references/project-claude-template.md` and `…/agenda-template.md` — templates for the project `CLAUDE.md` (project name filled in) and `agenda.md`.

**Dashboard skeleton.** The empty dashboard is created by calling the `build_dashboard` MCP tool with `{project:"<ABS>/projects/<slug>", slug, title:"<Project> Dashboard"}`; the tool creates `dashboard/` and `artifacts/`. The agent never hand-writes the dashboard kernel (the UI kit / `ui.js` would truncate on the sandbox mount); it only later edits the small per-project `dashboard/<slug>-dashboard.sk.json`. MCP tools require absolute project paths.

**Layout invariants.** Exactly two root files (`CLAUDE.md` + `agenda.md`) plus the folder set; `brain/`, `log/`, `archive/`, `output/` are created empty. `data/` is lazy (first table) and `.sidekick/` is lazy (first registry/sync write). `_triage/` and `_archive/projects/` are workspace-root, not per-project (ARCHITECTURE §13 init questionnaire; project model). Exactly one top-level project is created — no nested `projects/<parent>/<sub>/` and no areas during init; areas (`brain/<sub>/` + `output/<sub>/`) are introduced later by the core skill.

**Why this is a process, not an integration.** The `build_dashboard` call crosses into the bundled `sidekick-sync` MCP server — our own code — not an external system, so it is an internal boundary.

**Dependencies.** Upstream: `sidekick-init/write-workspace-claude`. Systems: `skills` (scaffolding logic) + `mcp-server` (`build_dashboard`). This is the terminal node of the `sidekick-init` subflow; the closing scheduling/connector wrap-up follows in the skill but is narrative, not a separate graph node.
