---
domains:
  - project-model
edges:
  - label: build empty dashboard skeleton
    to: sidekick-sync/build-dashboard
    via: starts
flowId: project-detection
generatedAt: 2026-06-14T11:55:56Z
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generator: solidcortex@0.17.0
kind: derived
mainCodeFile: skills/sidekick-core/references/project-claude-template.md
nodeId: scaffold-new-project
parent: sidekick-core/project-detection
related:
  - sidekick-init/scaffold-first-project
slug: scaffold-new-project
status: current
summary: Create a top-level project under projects/<slug>/ — seed CLAUDE.md and agenda.md from templates, make brain/log/archive/output, and build the empty dashboard skeleton.
systems:
  - skills
type: process
---

## TLDR (agent)
**Purpose:** Creates a new top-level project folder with its standard files, folders, and an empty dashboard skeleton, on an explicit go-ahead.
**Inputs:** trigger = explicit new-project intent (or "New project" picked in the picker); a kebab-case slug; the project-claude and agenda templates.
**Outputs:** `projects/<slug>/` with seeded `CLAUDE.md` + `agenda.md` and empty `brain/ log/ archive/ output/`; an empty "<Project> Dashboard" built via `build_dashboard`. `data/` and `.sidekick/` are not created yet.
**Code anchor:** [skills/sidekick-core/references/project-claude-template.md](../../../skills/sidekick-core/references/project-claude-template.md)
**Edges:** ← project-detection/detect-active-project, ← project-detection/project-picker, → sidekick-sync/build-dashboard (build empty dashboard skeleton)
**Key rules:**
- Slug is kebab-case and short; it is the folder name under `projects/`.
- Only `CLAUDE.md` + `agenda.md` go loose in the project root — every other write has a folder.
- `data/` is lazy (first table); `.sidekick/` is lazy (first registry/sync write) — neither is made at scaffold.
- Scaffolding is top-level only — an area gets no scaffold.
- Every project starts with an empty "<Project> Dashboard"; later "show me…" requests fill it, and it self-heals if deleted.

## Functional (user facing)

### Why use this?
Starting a new piece of work gives you a clean, consistent home for it in one step: a memory file, a running agenda, and the right folders for drafts, knowledge, finished deliverables, and data — plus an empty dashboard ready to fill. You never have to set this structure up by hand or wonder where something should go.

### What it does
- Runs when you clearly ask for a new project, or when you pick "New project" in the picker — that ask is itself the approval, so Sidekick goes ahead.
- Creates a folder named after a short, hyphenated slug for the project.
- Seeds a project memory file and a starter agenda from templates so the project opens with sensible defaults.
- Creates the empty working folders: a place for distilled knowledge, a place for daily logs and drafts, a place for superseded originals, and a place for finished deliverables.
- Builds an empty dashboard named after the project, ready to be filled later when you ask to see your data.
- Holds off on the data folder and the hidden machine-state folder — those appear only the first time you actually store data or save a recipe.

### Behind the scenes
The data folder is deliberately lazy: it is created the first time you store structured data, not at scaffold, so empty projects stay tidy. If output sync is turned on, the new project's deliverables and dashboard are also synced and a live dashboard artifact is created. The empty dashboard is a real skeleton — it has no numbers until a later "show me…" request binds queries to it — and Sidekick rebuilds it automatically if it ever goes missing.

### Pro tips
- You do not need a separate "create project" command — just say what you want to work on as a new project, and the scaffold runs.
- Keep the project name short; the slug becomes the folder name, so concise and descriptive (like `q3-board-prep`) works best.
- This only ever creates a top-level project. If your work is really a strand inside an existing project, it belongs in an area instead — which is set up differently and gets no scaffold.

### Related
- [detect-active-project](detect-active-project.md) — routes an explicit new-project intent here.
- [project-picker](project-picker.md) — "New project" choice lands here.
- [setup-subproject-area](setup-subproject-area.md) — the area path, which deliberately skips scaffolding.

## Technical

**Main code locations**
- `skills/sidekick-core/SKILL.md` — "Scaffolding a project": the eager set (`CLAUDE.md`, `agenda.md`, `brain/`, `log/`, `archive/`, `output/`) seeded from `references/project-claude-template.md` + `references/agenda-template.md`, the lazy `data/`, the `build_dashboard` skeleton call, and the "top-level only / only two loose root files" invariants.
- `skills/sidekick-core/references/project-claude-template.md` — the `CLAUDE.md` seed (`{{PROJECT_NAME}}` placeholder, "Read at session start" list, write-discipline reminder, subproject note).
- `skills/sidekick-core/references/project-structure.md` — "The complete project layout": authoritative folder map and eager-vs-lazy split (`dashboard/` + `artifacts/` are part of the scaffolded skeleton; `data/` and `.sidekick/` are lazy).
- `docs/ARCHITECTURE.md` §3.0 (scaffold) and §3.2 (slug convention).

**Key structures / calls**
- `build_dashboard` (the `sidekick-sync` MCP tool) is invoked with `{project:"<ABS>/projects/<slug>", slug, title:"<Project> Dashboard"}` to bake the empty dashboard; absolute project path is required.
- Templates use `{{PROJECT_NAME}}` / `{{MAIN_TOPIC}}` placeholders resolved at seed time.

**Dependencies**
- Upstream: `project-detection/detect-active-project`, `project-detection/project-picker`.
- Downstream / external: `sidekick-sync/build-dashboard` (cross-flow edge) for the skeleton, and (if output sync on) `reconcile_output` + the live Cowork dashboard artifact.
- Note: scaffolding is explicitly NOT applied to subprojects — see `project-detection/setup-subproject-area`.
