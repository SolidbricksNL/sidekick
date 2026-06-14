---
flowId: project-detection
nodeId: project-picker
type: process
slug: project-picker
status: current
kind: derived
summary: On doubt, present the tappable multiple-choice picker — best-guess 1-3 existing projects plus New project and a free-text escape — and do nothing structural until the user chooses.
systems: [skills]
domains: [project-model]
parent: sidekick-core/project-detection
mainCodeFile: skills/sidekick-core/SKILL.md
edges:
  - to: project-detection/scaffold-new-project
    via: starts
    label: user picks New project
  - to: project-detection/setup-subproject-area
    via: starts
    label: user picks area inside parent
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Resolves an ambiguous project intent by asking the user to choose, rather than guessing or asking an open-ended question.
**Inputs:** trigger = detection reached Case B (no clean match); reads = candidate projects and their agendas/brains for the best-guess ranking.
**Outputs:** the user's choice → an adopted existing project, or a branch to scaffold-new-project / setup-subproject-area; no structural change until the choice is made.
**Code anchor:** [skills/sidekick-core/SKILL.md](../../../skills/sidekick-core/SKILL.md)
**Edges:** ← project-detection/detect-active-project (on doubt), → project-detection/scaffold-new-project (picks New project), → project-detection/setup-subproject-area (picks area inside parent)
**Key rules:**
- Use Cowork's tappable multiple-choice picker — options must be clickable, never a plain bulleted/numbered list.
- Present a best guess of 1-3 likely existing projects (most likely first) plus "New project" and "Another project — tell me which" (free-text escape).
- When no project exists yet, offer only the last two options.
- Do nothing structural until the user chooses; never fall back to an open "which project?".

## Functional (user facing)

### Why use this?
When Sidekick is not sure which project you mean, you get a quick tap instead of a typing prompt or a wrong guess. It shows you the few projects it thinks are most likely, plus a way to start fresh or name something else — so picking the right home for the work takes one tap.

### What it does
- Appears only when the active project is genuinely unclear — the fallback path of project detection.
- Shows its best guess of the one to three existing projects you most likely mean, ordered most-likely first, based on their agendas and stored knowledge.
- Always adds a "New project" option and an "Another project — tell me which" escape so you can type a name it did not list.
- Holds off on creating or changing anything until you have chosen.
- If you do not have any projects yet, it skips the guesses and just offers "New project" and the free-text escape.

### How it connects

```text
detect-active-project (doubt) → project-picker (this) → adopt / scaffold-new-project / setup-subproject-area
```

The picker is the decision point: your tap either settles on an existing project or sends Sidekick into creating a new project or setting up an area inside an existing one.

### Behind the scenes
This is Sidekick's plugin-wide way of asking any either/or question: a small set of short, clickable choices with an escape hatch, never a free-text "what do you want?". The picker never substitutes for the approval gates on writing files — it is only how the question is presented.

### Pro tips
- If none of the offered projects fit, use the "Another project — tell me which" escape and type the name; you do not have to accept a guess.
- Choosing "New project" here is the same go-ahead as asking for a new project outright — it leads straight into scaffolding.

### Related
- [detect-active-project](detect-active-project.md) — the step that routes here on doubt.
- [scaffold-new-project](scaffold-new-project.md) — reached when you pick New project.
- [setup-subproject-area](setup-subproject-area.md) — reached when the choice is an area inside a parent.

## Technical

**Main code locations**
- `skills/sidekick-core/SKILL.md` — "Project detection", Case B: defines the picker contents (1-3 best-guess existing projects + "New project" + free-text escape), the most-likely-first ordering, the no-existing-projects degenerate case (offer only the last two), and the "do nothing structural until they choose" invariant.
- `skills/sidekick-core/SKILL.md` — "How you ask questions (plugin-wide)" section: mandates Cowork's interactive tappable multiple-choice picker (2-4 short options + escape hatch) for every either/or, forbidding plain bullet/number lists. Full guidance in `references/interaction-style.md`.
- `docs/ARCHITECTURE.md` §3.1 step 4 — the doubt branch ("Does this belong to project X, or shall I start a new project Y?").

**Behavior**
- Model-procedure, not executable code; rendered through Cowork's picker UI primitive.
- Pure decision node: emits no file writes. Its only output is the routing of the user's selection to a downstream node (or adoption of an existing project, which returns control to the main session flow).

**Dependencies**
- Upstream: `project-detection/detect-active-project` (Case B).
- Downstream: `project-detection/scaffold-new-project`, `project-detection/setup-subproject-area`.
- UI dependency: Cowork's multiple-choice picker; behavioral reference `skills/sidekick-core/references/interaction-style.md`.
