---
flowId: project-detection
nodeId: setup-subproject-area
type: process
slug: setup-subproject-area
status: current
kind: derived
summary: Set up an area within a parent project — brain/<sub>/ (seed overview.md via brain diff+approval) and output/<sub>/, agenda items under the parent's agenda, never a nested or scaffolded project.
systems: [skills]
domains: [project-model]
parent: sidekick-core/project-detection
mainCodeFile: skills/sidekick-core/references/project-structure.md
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Sets up a strand of work as an area inside an existing parent project, reusing the parent's harness rather than creating a new project.
**Inputs:** trigger = explicit "area within / part of / under <parent>" intent (or the area choice in the picker); a confirmed parent project; an area sub-slug.
**Outputs:** `projects/<parent>/brain/<sub>/overview.md` (seeded via brain diff + approval) + `projects/<parent>/output/<sub>/`; agenda items under a `## <sub>` heading in the parent's `agenda.md`; the overview added to the parent's `CLAUDE.md` read-list.
**Code anchor:** [skills/sidekick-core/references/project-structure.md](../../../skills/sidekick-core/references/project-structure.md)
**Edges:** ← project-detection/detect-active-project, ← project-detection/project-picker
**Key rules:**
- A subproject is never a project — no own `CLAUDE.md`, no own `agenda.md`, no scaffold, never a nested `projects/<parent>/<sub>/`.
- Seeding `overview.md` is a brain write — show the diff, write only after approval.
- The area reuses the parent's `agenda.md` (optional `## <sub>` heading), `log/`, and `archive/`.
- When it is unclear whether something is a new project or an area, ask via the picker.

## Functional (user facing)

### Why use this?
When a piece of work is big enough to keep apart but still clearly belongs to an existing project, you get a clean separation for it without spinning up a whole second project. The area shares the parent's agenda, context, and people, so it stays in the same loop for check-ins, status, and search instead of becoming an orphan.

### What it does
- Runs when you clearly mean a strand inside an existing project — phrases like "an area for X in Y", "part of Y", "under Y", or "a sub-area of Y".
- Creates a knowledge subfolder for the area inside the parent's brain, and seeds a short overview describing what the area is and where it stands.
- Creates a deliverables subfolder for the area inside the parent's output, ready for its finished work.
- Adds the area's to-dos to the parent's existing agenda, optionally grouped under a heading named for the area.
- Updates the parent's memory file so the area's overview is read at the start of every session in that project.
- Deliberately does not create any new project, any separate memory or agenda file, or any nested project folder.

### When intent is ambiguous
If it is not clear whether you mean a brand-new project or an area inside an existing one, Sidekick asks you via the picker — "a new project, or an area inside <parent>?" — rather than guessing. Choosing wrong in either direction (a real project folded in as an area, or an area split out as a nested project) is exactly what this step avoids.

### Behind the scenes
Seeding the area's overview goes through the brain discipline: you see the proposed text as a diff and it is only written after you approve. Because the whole area lives inside the parent — its knowledge in the parent's brain, its deliverables in the parent's output, its agenda items in the parent's agenda — it is automatically covered by triage, check-in, status, and find as part of the parent, with nothing extra to wire up.

### Pro tips
- An area can be promoted to a full project later if it outgrows the parent, but that is a deliberate, confirmed move — the default for a strand of work is to keep it as an area.
- Logs and archived originals for the area stay at the parent level; a log's name can name the area (for example a research log slugged with the area name) without needing its own folder.

### Related
- [detect-active-project](detect-active-project.md) — routes an explicit area intent here.
- [project-picker](project-picker.md) — the area choice (and the ambiguity question) lands here.
- [scaffold-new-project](scaffold-new-project.md) — the contrasting path: a full top-level project with a scaffold.

## Technical

**Main code locations**
- `skills/sidekick-core/references/project-structure.md` — "Creating a subproject (area)": the 5-step procedure (brain `<sub>/overview.md` via diff+approval; `output/<sub>/`; agenda items under a `## <sub>` heading in the parent's agenda; add overview to parent `CLAUDE.md` read-list; log the creation). Also the project-vs-subproject comparison table, the cardinal rule (never nested, never own `CLAUDE.md`/`agenda.md`), the detection guard, and the worked `competitor-scan` example.
- `skills/sidekick-core/SKILL.md` — "Subprojects (areas within a project)": the condensed contract and the "ask via the picker when unclear" rule.
- `docs/ARCHITECTURE.md` §3.4 — the canonical area definition, the project-vs-subproject choice signals, and the worked example.

**Behavior**
- Model-procedure, not executable code. The only structural writes are the two subfolders and the seed `overview.md` (gated by the brain diff+approval discipline), plus edits to the parent's `agenda.md` and `CLAUDE.md`.
- Hard negative invariant: never produce `projects/<parent>/<sub>/`, a `<sub>/CLAUDE.md`, a `<sub>/agenda.md`, or any scaffold — nesting a project breaks detection/triage/check-in/status, which only walk the direct children of `projects/`.

**Dependencies**
- Upstream: `project-detection/detect-active-project`, `project-detection/project-picker`.
- Cross-cutting: the brain-write discipline (`references/brain-protocol.md`) governs the `overview.md` seed; coverage by triage/check-in/status/find is automatic because the area lives inside the parent.
