# Project model and scaffolding

**Status:** done (folder contract written; agenda template final; CLAUDE template fix applied)
**Depends on:** 01-structure-validation, 03-settings-and-init-flow

## Goal
"Done" means the on-disk project model is nailed down as an unambiguous folder
contract: the exact scaffold of `projects/<slug>/` (CLAUDE.md, agenda.md,
brain/, log/, archive/, output/, and lazily-created data.sqlite), slug
conventions, the root-level `_triage/` and `_archive/projects/` folders, and
project-detection behavior (match → confirm; doubt → ask; never silently
create). The `project-claude-template.md` and `agenda-template.md` are
finalized.

## Context
- `ARCHITECTURE.md` §3 (project model), §3.0 (scaffold), §3.1 (detection),
  §3.2 (slug), §3.3 (archiving).
- `skills/sidekick/SKILL.md` ("Project detection" + "Scaffolding a project").
- `skills/sidekick/references/project-claude-template.md`.
- `skills/sidekick/references/agenda-template.md`.
- Both init (plan 03) and the always-on skill scaffold projects; they must agree.

## Tasks
1. [x] Write the canonical **folder contract** for a project, listing every path
   created on scaffold and its initial state:
   - `projects/<slug>/CLAUDE.md` (seeded from template, project name filled).
   - `projects/<slug>/agenda.md` (seeded from template).
   - `projects/<slug>/brain/` (empty until first distillation).
   - `projects/<slug>/log/` (empty).
   - `projects/<slug>/archive/` (empty).
   - `projects/<slug>/output/` (empty).
   - `projects/<slug>/data.sqlite` — NOT created on scaffold; lazy.
   - Root system folders: `_triage/`, `_archive/projects/`.
2. [x] Decide how empty directories are represented on disk so they survive in
   git/Cowork (e.g. a `.gitkeep`), and whether the live workspace needs them at
   all (the live workspace is git-ignored — see repo `.gitignore`). Document the
   decision; keep templates as the source of truth, not committed sample dirs.
3. [x] Confirm slug rules: `kebab-case`, short, descriptive (`core-roadmap`,
   `client-bpd`, `q3-board-prep`). Define how a free-text project name maps to a
   slug (lowercase, spaces→hyphens, strip punctuation, collision suffix).
4. [x] Confirm project-detection behavior matches ARCHITECTURE §3.1 exactly:
   list `projects/`, read each `agenda.md` + brain index, match intent, confirm
   on clear match, ask on doubt, scaffold only on explicit approval, **never
   silently create**. Confirm archived projects are excluded from detection.
5. [x] **Finalize `project-claude-template.md`**: verify the relative path
   `../../sidekick.settings.md` is correct from `projects/<slug>/CLAUDE.md`,
   the "read at session start" list, the write-disciplines reminder, and the
   `{{PROJECT_NAME}}` / `{{MAIN_TOPIC}}` placeholders. Propose any wording fix.
6. [x] **Finalize `agenda-template.md`**: confirm the sections (Open items /
   Waiting on / Recently done / Notes for the next check-in), the status
   vocabulary (todo/doing/waiting/done), and the `{{PROJECT_NAME}}`/`{{DATE}}`
   placeholders serve the check-in (plan 09) well.
7. [x] Reconcile init's scaffolding (plan 03) with the always-on skill's
   scaffolding so they produce byte-identical structure from the same templates.
8. [x] Cross-check that the template-location decision from plan 03 (duplicate vs
   cross-reference) is reflected here.

## Resolution (2026-06-01)

### Canonical folder contract (task 1, 7)

On project creation, **both** `/sidekick-init` and the always-on `sidekick`
skill scaffold byte-identically from the same shared templates:

| Path | Initial state | Source |
|---|---|---|
| `projects/<slug>/CLAUDE.md` | seeded, `{{PROJECT_NAME}}` filled | `skills/sidekick/references/project-claude-template.md` |
| `projects/<slug>/agenda.md` | seeded, `{{PROJECT_NAME}}` + `{{DATE}}` filled | `skills/sidekick/references/agenda-template.md` |
| `projects/<slug>/brain/` | empty (no file until first distillation, §5) | — |
| `projects/<slug>/log/` | empty | — |
| `projects/<slug>/archive/` | empty | — |
| `projects/<slug>/output/` | empty | — |
| `projects/<slug>/data.sqlite` | **not created** — lazy on first structured data | — |

Root system folders (created by **init** at setup; created lazily "if absent" by
triage/archive otherwise — the one intentional init-vs-main asymmetry):

| Path | Initial state | Created by |
|---|---|---|
| `_triage/` | empty | init (or triage on first run) |
| `_archive/projects/` | empty | init (or archive on first move) |

### Empty-directory persistence (task 2)

The live workspace is **git-ignored** (repo `.gitignore`), so empty scaffold dirs
are not a git concern, and the plugin ships **no committed sample project dirs** —
the templates are the single source of truth. Decision: **no `.gitkeep` / no
placeholder READMEs.** Scaffold creates the four dirs at runtime; each receives
content quickly (first log/brain/output write). If a Cowork sync drops an empty
dir, the next write re-creates it — harmless. Keep scaffold lean; skills tolerate
a missing dir by creating it on first write.

### Slug derivation (task 3)

`kebab-case`, short, descriptive (`core-roadmap`, `client-bpd`, `q3-board-prep`).
From a free-text project name: **lowercase → trim → strip punctuation (keep
letters/digits/spaces/hyphens) → spaces to hyphens → collapse repeated hyphens →
strip leading/trailing hyphens**. On collision with an existing
`projects/<slug>/`, append `-2`, then `-3`, … until free. Keep it short (the
first few meaningful words); the user-facing name lives in `CLAUDE.md`/`agenda.md`
headings, so the slug only needs to be a stable folder id.

### Project detection (task 4) — matches §3.1

Confirmed against ARCHITECTURE §3.1 and the `sidekick` skill body: list
`projects/` (excluding `_archive/`), read each `agenda.md` + brain index, match
intent, **confirm** on clear match, **ask** on doubt, scaffold **only** on
explicit approval, **never silently create**. Archived projects are excluded
because detection lists `projects/` only, and the archive skill states archived
projects no longer participate in detection/triage/check-in. ✓

### Template finalization (task 5, 6)

**`agenda-template.md` — finalized as-is.** Sections (Open items / Waiting on /
Recently done / Notes for the next check-in), status vocabulary
(todo/doing/waiting/done), and `{{PROJECT_NAME}}`/`{{DATE}}` placeholders match
what the check-in (plan 09) consumes. No change.

**`project-claude-template.md` — one proposed diff (resolves the `{{MAIN_TOPIC}}`
open question).** The path `../../sidekick.settings.md` is correct from
`projects/<slug>/CLAUDE.md`. The problem: the "Read at session start" list points
at `brain/{{MAIN_TOPIC}}.md`, but `brain/` is empty at scaffold (§3.0/§5 — no
brain file until the first distillation), so this is a dangling read. Fix: make
the brain line a commented example that the skill un-comments when the first brain
file is created, so a fresh project never points at a missing file.

```
- OLD:
## Read at session start

1. `brain/{{MAIN_TOPIC}}.md` — current status and knowledge
2. `agenda.md` — live items and planning
<!-- add more brain files here as the project grows, e.g.: -->
<!-- 3. brain/decisions.md — decisions made so far -->
<!-- 4. brain/data-model.md — database schema (plain language) -->

- NEW:
## Read at session start

1. `agenda.md` — live items and planning
<!-- brain/ starts empty. When the first brain file is distilled, add it
     here so it is read at session start, e.g.: -->
<!-- 2. brain/{{MAIN_TOPIC}}.md — current status and knowledge -->
<!-- 3. brain/decisions.md — decisions made so far -->
<!-- 4. brain/data-model.md — database schema (plain language) -->
```

Status: **APPLIED 2026-06-01** (user-approved). Plan 04 owns this template. With
this diff, `{{MAIN_TOPIC}}` is only ever an example inside a comment — no
scaffold-time fill needed and no broken session-start read.

### Template-location decision reflected (task 8)

No duplication: templates live in `skills/sidekick/references/`; init references
them via `../sidekick/references/...`. Both scaffolders seed from the same files,
guaranteeing identical structure. (Consistent with plan 01 + plan 03.)

## Acceptance criteria
- A documented, unambiguous folder contract exists that both init and the
  always-on skill follow identically.
- `project-claude-template.md` and `agenda-template.md` are finalized (or have
  concrete proposed diffs) with correct relative paths and placeholders.
- Slug derivation rules (including collision handling) are written down.
- Project detection is confirmed to never silently create a project and to
  exclude archived projects.

## Notes / open questions
- **Empty-folder persistence.** The live workspace is git-ignored, so empty
  scaffold dirs aren't a git concern there; but confirm Cowork tolerates empty
  `brain/`/`log/`/`archive/`/`output/` dirs, or whether each should get a tiny
  placeholder README on scaffold.
- **Template location — RESOLVED** (shared with plan 01 + plan 03): no
  duplication. Templates live in `skills/sidekick/references/`; init references
  them via `../sidekick/references/...` (already fixed in the init SKILL.md). Both
  init and the always-on skill seed from the same files, guaranteeing identical
  scaffolds.
- **`{{MAIN_TOPIC}}` at scaffold time.** The CLAUDE.md template points at
  `brain/{{MAIN_TOPIC}}.md` before any brain file exists. Decide whether to fill
  a sensible default at scaffold, leave the placeholder, or comment it out until
  the first brain file is created.
